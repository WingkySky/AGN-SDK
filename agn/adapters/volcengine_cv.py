"""
AGN-SDK 火山引擎方舟（Seedream/Seedance）适配器

实现火山引擎方舟平台图像和视频生成 API 的统一调用。

官方 API 文档：https://www.volcengine.com/docs/82379
- Base URL: https://ark.cn-beijing.volces.com/api/v3
- 图像生成 (Seedream): POST /images/generations (同步)
- 视频生成 (Seedance): POST /contents/generations/tasks (异步任务)
- 查询视频任务: GET /contents/generations/tasks/{task_id}
- 模型列表: GET /models (OpenAI 兼容，返回已开通模型)
- 认证: Bearer Token (火山引擎 API Key)
"""

import logging
from typing import Any

import httpx

from agn.adapters.base import BaseAdapter
from agn.adapters.factory import AdapterFactory
from agn.core.errors import (
    APIError,
    AuthenticationError,
    RateLimitError,
    UnsupportedCapabilityError,
)
from agn.core.utils import current_timestamp, generate_id
from agn.models.chat import ChatCompletion, ChatMessage
from agn.models.common import ModelInfo, ProviderConfig
from agn.models.image import ImageData, ImageGenerationResult
from agn.models.video import VideoStatus, VideoTask

logger = logging.getLogger(__name__)

# 方舟 Seedream 图像 size 规范（官方文档 https://www.volcengine.com/docs/82379/1541523）
# 方式 1（枚举）：2K / 3K / 4K
# 方式 2（像素值 WIDTHxHEIGHT）：需同时满足总像素和宽高比两项约束
_VOLCENGINE_MIN_PIXELS = 3686400  # 2560x1440
_VOLCENGINE_MAX_PIXELS = 16777216  # 4096x4096
_VOLCENGINE_MIN_RATIO = 1 / 16
_VOLCENGINE_MAX_RATIO = 16

# 方式 1 的合法枚举值（大写匹配）
_VOLCENGINE_SIZE_ENUMS = {"2K", "3K", "4K"}

# 2K 推荐宽高像素值（官方推荐表，最小合法档），按宽高比升序排列
# 格式：(宽高比 ratio, 宽, 高)
# 参考 https://www.volcengine.com/docs/82379/1541523 推荐的宽高像素值表
_VOLCENGINE_2K_PRESETS: list[tuple[float, int, int]] = [
    (9 / 16, 1600, 2848),  # 9:16
    (2 / 3, 1664, 2496),  # 2:3
    (3 / 4, 1728, 2304),  # 3:4
    (1.0, 2048, 2048),  # 1:1
    (4 / 3, 2304, 1728),  # 4:3
    (3 / 2, 2496, 1664),  # 3:2
    (16 / 9, 2848, 1600),  # 16:9
    (21 / 9, 3136, 1344),  # 21:9
]


class VolcengineCVAdapter(BaseAdapter):
    """
    火山引擎方舟 CV 适配器（Seedream 图像 / Seedance 视频）

    支持：
    - Seedream 系列：文生图
    - Seedance 系列：文生视频、图生视频
    """

    provider_type = "volcengine_cv"
    provider_name = "火山引擎 Seedream/Seedance"
    supported_capabilities = ["image", "video"]

    DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

    def __init__(self, config: ProviderConfig) -> None:
        """
        初始化适配器

        Args:
            config: Provider 配置
        """
        super().__init__(config)
        self.base_url = config.base_url or self.DEFAULT_BASE_URL
        self.api_key = config.api_key or ""
        self._http_client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        """启动适配器"""
        self._http_client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.config.timeout),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

    async def close(self) -> None:
        """关闭适配器"""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    def _get_client(self) -> httpx.AsyncClient:
        """获取 HTTP 客户端"""
        if self._http_client is None:
            raise RuntimeError("Adapter not started. Call start() first.")
        return self._http_client

    # ==================== 文本对话（不支持）====================

    async def chat(
        self,
        model: str,
        messages: list[ChatMessage],
        **kwargs: Any,
    ) -> ChatCompletion:
        """文本对话（不支持，请使用 DoubaoAdapter）"""
        raise UnsupportedCapabilityError(
            message="VolcengineCV adapter does not support chat. Use DoubaoAdapter for Doubao chat models.",
            details={"provider": self.provider_type, "capability": "chat"},
        )

    # ==================== 图像生成 (Seedream) ====================

    @staticmethod
    def _normalize_image_size(size: str) -> str:
        """
        归一化图像 size 到方舟 Seedream 规范

        方舟 Seedream size 规范（官方文档 https://www.volcengine.com/docs/82379/1541523）：
        - 方式 1（枚举）："2K" / "3K" / "4K"
        - 方式 2（像素值 WIDTHxHEIGHT）：需同时满足
          * 总像素 ∈ [3686400, 16777216]
          * 宽高比 ∈ [1/16, 16]

        本方法将不合法的尺寸（如 OpenAI 风格的 1024x1024 小尺寸）按
        最接近的宽高比映射到 2K 推荐尺寸（最小合法档），保证请求可被方舟接受。
        已合法的尺寸原样透传，不修改用户意图。

        Args:
            size: 用户传入的 size 字符串（如 "1024x1024"、"2K"、"2560x1440"）

        Returns:
            方舟规范格式的 size 字符串（如 "2048x2048"、"2K"）
        """
        if not size or not isinstance(size, str):
            return "2048x2048"

        s = size.strip().upper()

        # 方式 1：枚举值原样透传
        if s in _VOLCENGINE_SIZE_ENUMS:
            return size

        # 方式 2：解析 WIDTHxHEIGHT（兼容 x / X / * 分隔符）
        parts = s.replace("X", "x").replace("*", "x").split("x")
        if len(parts) != 2:
            return "2048x2048"

        try:
            w, h = int(parts[0]), int(parts[1])
        except ValueError:
            return "2048x2048"

        if w <= 0 or h <= 0:
            return "2048x2048"

        total = w * h
        ratio = w / h

        # 已合法：原样透传
        if (
            _VOLCENGINE_MIN_PIXELS <= total <= _VOLCENGINE_MAX_PIXELS
            and _VOLCENGINE_MIN_RATIO <= ratio <= _VOLCENGINE_MAX_RATIO
        ):
            return f"{w}x{h}"

        # 不合法：按最接近的宽高比映射到 2K 推荐尺寸
        best = _VOLCENGINE_2K_PRESETS[0]
        best_diff = abs(ratio - best[0])
        for rec_ratio, rec_w, rec_h in _VOLCENGINE_2K_PRESETS[1:]:
            diff = abs(ratio - rec_ratio)
            if diff < best_diff:
                best = (rec_ratio, rec_w, rec_h)
                best_diff = diff

        return f"{best[1]}x{best[2]}"

    async def image_generate(
        self,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> ImageGenerationResult:
        """
        生成图像（Seedream 文生图）

        Args:
            model: 方舟 Model ID（如 doubao-seedream-4-0-250828），需先在方舟控制台开通
            prompt: 提示词
            **kwargs:
                - size: 图像尺寸，默认 "1024x1024"
                  支持方舟枚举值 "2K"/"3K"/"4K" 或像素值 "WIDTHxHEIGHT"
                  小尺寸会自动归一化到方舟规范的最小合法档（2K 推荐）
                - n: 生成数量，默认 1
                - response_format: "url" 或 "b64_json"
                - negative_prompt: 负面提示词
                - seed: 随机种子

        Returns:
            图像生成结果
        """
        client = self._get_client()

        # 方舟 Seedream 对 size 有平台特定规范（最小 3686400 像素），
        # 小尺寸（如 1024x1024）会触发 503，需归一化到合法档
        raw_size = kwargs.get("size", "1024x1024")
        size = self._normalize_image_size(raw_size)

        n = kwargs.get("n", 1)
        response_format = kwargs.get("response_format", "url")

        body: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "n": n,
            "response_format": response_format,
        }

        if negative_prompt := kwargs.get("negative_prompt"):
            body["negative_prompt"] = negative_prompt
        if seed := kwargs.get("seed"):
            body["seed"] = seed

        try:
            response = await client.post("/images/generations", json=body)
        except Exception as e:
            logger.error(f"Seedream image generation failed: {e}")
            raise

        self._handle_error(response)
        data = response.json()
        return self._parse_image_response(data, model)

    # ==================== 视频生成 (Seedance) ====================

    async def video_create(
        self,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> VideoTask:
        """
        创建视频生成任务（Seedance）

        对齐方舟 Video Generation API：POST /contents/generations/tasks
        请求体为 {"model": ..., "content": [{"type":"text","text":"提示词 --flag value"}, ...]}

        Args:
            model: 模型 ID（方舟规范格式，如 doubao-seedance-1-0-pro-250528）
            prompt: 提示词
            **kwargs:
                - mode: "text2video" (默认) 或 "image2video"
                - reference_images: 参考图像 URL 列表 (image2video 首帧)
                - duration: 视频时长（秒），方舟 flag --dur
                - aspect_ratio: 宽高比，"16:9"/"9:16"/"1:1" 等，方舟 flag --rt
                - resolution: 分辨率，"720p"/"1080p"/"480p"/"4k"，方舟 flag --rs
                - seed: 随机种子，方舟 flag --seed
                - watermark: 是否加水印 (true/false)，方舟 flag --wm
                - camerafixed: 镜头是否固定 (true/false)，方舟 flag --cf

        Returns:
            视频任务信息
        """
        client = self._get_client()

        mode = kwargs.get("mode", "text2video")
        reference_images = kwargs.get("reference_images", [])

        # 构造 text content：提示词 + 方舟 flag 参数
        # 方舟 Seedance 参数通过 text 末尾的 --flag value 形式传递
        # 参考：https://www.volcengine.com/docs/82379/1520757
        text = prompt
        flags: list[str] = []
        if duration := kwargs.get("duration"):
            flags.append(f"--dur {duration}")
        if aspect_ratio := kwargs.get("aspect_ratio"):
            flags.append(f"--rt {aspect_ratio}")
        if resolution := kwargs.get("resolution"):
            flags.append(f"--rs {resolution}")
        if seed := kwargs.get("seed"):
            flags.append(f"--seed {seed}")
        if watermark := kwargs.get("watermark"):
            flags.append(f"--wm {str(watermark).lower()}")
        if camerafixed := kwargs.get("camerafixed"):
            flags.append(f"--cf {str(camerafixed).lower()}")
        if flags:
            text = f"{text} {' '.join(flags)}"

        # content 数组：文本必选，图片可选（图生视频时附加）
        content: list[dict[str, Any]] = [{"type": "text", "text": text}]
        if mode == "image2video" and reference_images:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": reference_images[0]},
                }
            )

        body: dict[str, Any] = {
            "model": model,
            "content": content,
        }

        try:
            response = await client.post("/contents/generations/tasks", json=body)
        except Exception as e:
            logger.error(f"Seedance video create failed: {e}")
            raise

        self._handle_error(response)
        data = response.json()

        task_id = data.get("id", generate_id("vtask"))
        raw_status = data.get("status", "queued")

        return VideoTask(
            task_id=task_id,
            model=model,
            status=self._map_video_status(raw_status),
            created_at=current_timestamp(),
        )

    async def video_poll(
        self,
        task_id: str,
        model: str = "",
    ) -> VideoStatus:
        """
        查询视频生成任务状态

        对齐方舟 Video Generation API：GET /contents/generations/tasks/{task_id}

        Args:
            task_id: 任务 ID（方舟格式 cgt-xxxx）
            model: 模型名称（可选，用于返回信息）

        Returns:
            视频任务状态
        """
        client = self._get_client()

        try:
            response = await client.get(f"/contents/generations/tasks/{task_id}")
        except Exception as e:
            logger.error(f"Seedance video poll failed: {e}")
            raise

        self._handle_error(response)
        data = response.json()
        return self._parse_video_status(data, task_id)

    # ==================== 模型列表 ====================

    async def list_models(
        self,
        model_type: str | None = None,
    ) -> list[ModelInfo]:
        """
        列出支持的模型

        调用 GET /models 实时拉取用户在方舟控制台已开通的模型列表。
        返回的模型 ID 为方舟规范格式（如 doubao-seedream-4-0-250828），
        可直接用于 image_generate / video_create 的 model 参数。

        方舟为 OpenAI 兼容 API，/models 端点返回用户已开通的预置模型。
        若返回为空，需先在火山方舟控制台开通对应模型。

        官方模型列表参考：
        https://www.volcengine.com/docs/82379/1330310
        """
        client = self._get_client()
        response = await client.get(url="/models")
        return self._parse_models_response(
            data=response.json(),
            provider="volcengine_cv",
            model_type=model_type,
        )

    # ==================== 响应解析 ====================

    def _parse_image_response(
        self, data: dict[str, Any], model: str
    ) -> ImageGenerationResult:
        """解析图像生成响应"""
        images: list[ImageData] = []
        for item in data.get("data", []):
            images.append(
                ImageData(
                    url=item.get("url"),
                    b64_json=item.get("b64_json"),
                    revised_prompt=item.get("revised_prompt"),
                )
            )

        return ImageGenerationResult(
            id=data.get("id", generate_id("img")),
            created=data.get("created", current_timestamp()),
            model=data.get("model", model),
            data=images,
        )

    def _parse_video_status(self, data: dict[str, Any], task_id: str) -> VideoStatus:
        """解析视频任务状态响应

        方舟查询任务响应中视频 URL 在 content.video_url 字段，
        同时兼容旧版 video_url / output.video_url / url 路径。
        """
        raw_status = data.get("status", "")
        status = self._map_video_status(raw_status)

        video_url: str | None = None
        if status == "success":
            # 方舟 content.video_url 优先，兼容其他路径
            content = data.get("content") or {}
            if isinstance(content, dict):
                video_url = content.get("video_url")
            video_url = (
                video_url
                or data.get("video_url")
                or data.get("output", {}).get("video_url")
                or data.get("url")
            )

        error_msg: str | None = None
        if status == "failed":
            error_msg = (
                data.get("error", {}).get("message")
                or data.get("message")
                or data.get("error")
            )

        return VideoStatus(
            task_id=task_id,
            status=status,
            video_url=video_url,
            progress=data.get("progress"),
            error=error_msg,
            created_at=data.get("created"),
            updated_at=data.get("updated", current_timestamp()),
        )

    # ==================== 状态映射 ====================

    def _map_video_status(self, raw_status: str) -> str:
        """映射火山引擎视频状态到统一状态"""
        status_map = {
            "queued": "pending",
            "pending": "pending",
            "submitted": "pending",
            "processing": "processing",
            "running": "processing",
            "in_progress": "processing",
            "succeeded": "success",
            "success": "success",
            "completed": "success",
            "failed": "failed",
            "error": "failed",
            "cancelled": "failed",
        }
        return status_map.get(raw_status.lower(), "pending")

    # ==================== 错误处理 ====================

    def _handle_error(self, response: httpx.Response) -> None:
        """处理错误响应"""
        if response.status_code < 400:
            return

        if response.status_code == 401:
            raise AuthenticationError(
                message="Invalid Volcengine API key or access denied"
            )
        if response.status_code == 429:
            raise RateLimitError(message="Volcengine rate limit exceeded")
        if response.status_code == 404:
            raise APIError(
                message="Model endpoint not found. Check your endpoint ID in Volcengine Ark console.",
                status_code=404,
            )

        try:
            error_data = response.json()
            error_msg = (
                error_data.get("error", {}).get("message")
                or error_data.get("message")
                or error_data.get("error")
                or f"HTTP {response.status_code}"
            )
        except Exception:
            error_msg = f"HTTP {response.status_code}"

        raise APIError(message=error_msg, status_code=response.status_code)


# 注册适配器
AdapterFactory.register("volcengine_cv", VolcengineCVAdapter)
AdapterFactory.register("seedream", VolcengineCVAdapter)
AdapterFactory.register("seedance", VolcengineCVAdapter)
