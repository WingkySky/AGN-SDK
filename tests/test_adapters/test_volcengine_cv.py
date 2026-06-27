"""
AGN-SDK 火山引擎方舟 CV 适配器测试

测试 VolcengineCVAdapter 的各项功能，包括图像生成、视频创建、视频轮询等。
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agn.adapters.volcengine_cv import VolcengineCVAdapter
from agn.core.errors import UnsupportedCapabilityError
from agn.models.common import ProviderConfig
from agn.models.image import ImageGenerationResult
from agn.models.video import VideoStatus, VideoTask


class TestVolcengineCVAdapter:
    """VolcengineCVAdapter 类基础测试"""

    @pytest.fixture
    def adapter_config(self, mock_api_key: str) -> ProviderConfig:
        """创建适配器配置"""
        return ProviderConfig(
            provider_type="volcengine_cv",
            api_key=mock_api_key,
        )

    @pytest.fixture
    def adapter(self, adapter_config: ProviderConfig) -> VolcengineCVAdapter:
        """创建适配器实例"""
        return VolcengineCVAdapter(config=adapter_config)

    def test_adapter_init(self, adapter: VolcengineCVAdapter) -> None:
        """测试适配器初始化"""
        assert adapter.provider_type == "volcengine_cv"
        assert "image" in adapter.supported_capabilities
        assert "video" in adapter.supported_capabilities
        assert "chat" not in adapter.supported_capabilities

    def test_adapter_supports_capability(self, adapter: VolcengineCVAdapter) -> None:
        """测试能力检查"""
        assert adapter.supports_capability("image")
        assert adapter.supports_capability("video")
        assert not adapter.supports_capability("chat")

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: VolcengineCVAdapter) -> None:
        """测试异步上下文管理器"""
        async with adapter as a:
            assert a._http_client is not None

    @pytest.mark.asyncio
    async def test_chat_not_supported(self, adapter: VolcengineCVAdapter) -> None:
        """测试文本对话不支持"""
        with pytest.raises(UnsupportedCapabilityError):
            await adapter.chat(
                model="test",
                messages=[{"role": "user", "content": "Hello"}],
            )


class TestVolcengineCVAdapterListModels:
    """VolcengineCVAdapter 模型列表测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> VolcengineCVAdapter:
        """创建适配器实例"""
        config = ProviderConfig(provider_type="volcengine_cv", api_key=mock_api_key)
        return VolcengineCVAdapter(config=config)

    def _mock_response(self, json_data: dict) -> MagicMock:
        """创建模拟 HTTP 响应"""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json = MagicMock(return_value=json_data)
        return mock_resp

    @pytest.mark.asyncio
    async def test_list_all_models(self, adapter: VolcengineCVAdapter) -> None:
        """测试获取所有模型（方舟规范 ID 格式）"""
        await adapter.start()

        # 方舟 /models 返回用户已开通的预置模型，ID 为 doubao- 前缀 + 日期后缀格式
        mock_result = {
            "data": [
                {"id": "doubao-seedream-4-0-250828", "name": "Doubao Seedream 4.0"},
                {
                    "id": "doubao-seedance-1-0-pro-250528",
                    "name": "Doubao Seedance 1.0 Pro",
                },
            ]
        }

        with patch.object(
            adapter._http_client, "get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = self._mock_response(mock_result)

            models = await adapter.list_models()
            mock_get.assert_called_once_with(url="/models")

            assert len(models) == 2
            types = {m.type for m in models}
            assert "image" in types
            assert "video" in types
            # 验证 ID 为方舟规范格式（doubao- 前缀）
            ids = {m.id for m in models}
            assert "doubao-seedream-4-0-250828" in ids
            assert "doubao-seedance-1-0-pro-250528" in ids

        await adapter.close()

    @pytest.mark.asyncio
    async def test_list_image_models(self, adapter: VolcengineCVAdapter) -> None:
        """测试获取图像模型"""
        await adapter.start()

        mock_result = {
            "data": [
                {"id": "doubao-seedream-4-0-250828"},
                {"id": "doubao-seedream-3-0-t2i-250415"},
            ]
        }

        with patch.object(
            adapter._http_client, "get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = self._mock_response(mock_result)

            models = await adapter.list_models(model_type="image")
            assert len(models) == 2
            for model in models:
                assert model.type == "image"

        await adapter.close()

    @pytest.mark.asyncio
    async def test_list_video_models(self, adapter: VolcengineCVAdapter) -> None:
        """测试获取视频模型"""
        await adapter.start()

        mock_result = {
            "data": [
                {"id": "doubao-seedance-1-0-pro-250528"},
            ]
        }

        with patch.object(
            adapter._http_client, "get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = self._mock_response(mock_result)

            models = await adapter.list_models(model_type="video")
            assert len(models) == 1
            for model in models:
                assert model.type == "video"

        await adapter.close()


class TestVolcengineCVAdapterStatusMapping:
    """VolcengineCVAdapter 状态映射测试"""

    def test_map_pending_status(self) -> None:
        """测试 pending 状态映射"""
        adapter = VolcengineCVAdapter(
            config=ProviderConfig(provider_type="volcengine_cv", api_key="test")
        )
        assert adapter._map_video_status("queued") == "pending"
        assert adapter._map_video_status("pending") == "pending"
        assert adapter._map_video_status("submitted") == "pending"

    def test_map_processing_status(self) -> None:
        """测试 processing 状态映射"""
        adapter = VolcengineCVAdapter(
            config=ProviderConfig(provider_type="volcengine_cv", api_key="test")
        )
        assert adapter._map_video_status("processing") == "processing"
        assert adapter._map_video_status("running") == "processing"
        assert adapter._map_video_status("in_progress") == "processing"

    def test_map_success_status(self) -> None:
        """测试 success 状态映射"""
        adapter = VolcengineCVAdapter(
            config=ProviderConfig(provider_type="volcengine_cv", api_key="test")
        )
        assert adapter._map_video_status("succeeded") == "success"
        assert adapter._map_video_status("success") == "success"
        assert adapter._map_video_status("completed") == "success"

    def test_map_failed_status(self) -> None:
        """测试 failed 状态映射"""
        adapter = VolcengineCVAdapter(
            config=ProviderConfig(provider_type="volcengine_cv", api_key="test")
        )
        assert adapter._map_video_status("failed") == "failed"
        assert adapter._map_video_status("error") == "failed"
        assert adapter._map_video_status("cancelled") == "failed"


class TestVolcengineCVAdapterImageMockHTTP:
    """VolcengineCVAdapter 图像生成 Mock HTTP 测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> VolcengineCVAdapter:
        """创建适配器实例"""
        config = ProviderConfig(provider_type="volcengine_cv", api_key=mock_api_key)
        return VolcengineCVAdapter(config=config)

    def _mock_response(self, data: dict, status_code: int = 200) -> MagicMock:
        """创建模拟 HTTP 响应"""
        mock_resp = MagicMock()
        mock_resp.status_code = status_code
        mock_resp.json = MagicMock(return_value=data)
        mock_resp.headers = {}
        return mock_resp

    @pytest.mark.asyncio
    async def test_image_generate_basic(
        self, adapter: VolcengineCVAdapter, sample_image_prompt: str
    ) -> None:
        """测试基础图像生成请求和响应解析"""
        await adapter.start()

        mock_result = {
            "id": "img-abc123",
            "created": 1700000000,
            "model": "seedream-5.0",
            "data": [
                {
                    "url": "https://cdn.example.com/image.png",
                    "revised_prompt": "A beautiful sunset over the ocean",
                }
            ],
        }

        with patch.object(
            adapter._http_client, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = self._mock_response(mock_result)

            result = await adapter.image_generate(
                model="seedream-5.0",
                prompt=sample_image_prompt,
            )

            assert isinstance(result, ImageGenerationResult)
            assert result.model == "seedream-5.0"
            assert len(result.data) == 1
            assert result.data[0].url == "https://cdn.example.com/image.png"
            assert result.data[0].revised_prompt == "A beautiful sunset over the ocean"

            # 验证请求
            call_args = mock_post.call_args
            assert "/images/generations" in str(call_args)
            body = call_args.kwargs.get("json") or call_args.args[0]
            assert body["model"] == "seedream-5.0"
            assert body["prompt"] == sample_image_prompt

        await adapter.close()

    @pytest.mark.asyncio
    async def test_image_generate_with_params(
        self, adapter: VolcengineCVAdapter, sample_image_prompt: str
    ) -> None:
        """测试带参数的图像生成"""
        await adapter.start()

        mock_result = {
            "id": "img-xyz789",
            "created": 1700000000,
            "model": "seedream-4.0",
            "data": [
                {
                    "b64_json": "base64_image_data",
                }
            ],
        }

        with patch.object(
            adapter._http_client, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = self._mock_response(mock_result)

            result = await adapter.image_generate(
                model="seedream-4.0",
                prompt=sample_image_prompt,
                size="1024x1024",
                n=2,
                response_format="b64_json",
                negative_prompt="blurry",
                seed=42,
            )

            assert isinstance(result, ImageGenerationResult)

            # 验证请求参数
            call_args = mock_post.call_args
            body = call_args.kwargs.get("json") or call_args.args[0]
            # 1024x1024 会被归一化为方舟规范的 2K 推荐 1:1 尺寸 2048x2048
            assert body["size"] == "2048x2048"
            assert body["n"] == 2
            assert body["response_format"] == "b64_json"
            assert body["negative_prompt"] == "blurry"
            assert body["seed"] == 42

        await adapter.close()


class TestVolcengineCVAdapterSizeNormalization:
    """VolcengineCVAdapter size 归一化测试

    方舟 Seedream size 规范（官方文档 https://www.volcengine.com/docs/82379/1541523）：
    - 枚举值 2K/3K/4K 原样透传
    - 像素值 WIDTHxHEIGHT：总像素 ∈ [3686400, 16777216]、宽高比 ∈ [1/16, 16]
    - 不合法的小尺寸按最接近宽高比映射到 2K 推荐尺寸
    """

    @pytest.mark.parametrize(
        "raw, expected, reason",
        [
            # 枚举值原样透传
            ("2K", "2K", "枚举值 2K 原样透传"),
            ("3K", "3K", "枚举值 3K 原样透传"),
            ("4K", "4K", "枚举值 4K 原样透传"),
            ("2k", "2k", "枚举值小写也透传（原样返回）"),
            # 已合法的像素值原样透传
            ("2048x2048", "2048x2048", "2K 1:1 已合法"),
            ("2560x1440", "2560x1440", "16:9 边界值 3686400 已合法"),
            ("4096x4096", "4096x4096", "4K 上限值已合法"),
            ("2848x1600", "2848x1600", "官方 16:9 2K 推荐值已合法"),
            # 不合法的小尺寸按宽高比映射到 2K 推荐
            ("1024x1024", "2048x2048", "1:1 小尺寸 → 2K 1:1 推荐"),
            ("1280x720", "2848x1600", "16:9 小尺寸 → 2K 16:9 推荐"),
            ("720x1280", "1600x2848", "9:16 小尺寸 → 2K 9:16 推荐"),
            ("1024x768", "2304x1728", "4:3 小尺寸 → 2K 4:3 推荐"),
            ("768x1024", "1728x2304", "3:4 小尺寸 → 2K 3:4 推荐"),
            # 格式异常回退默认
            ("invalid", "2048x2048", "非法格式回退默认"),
            ("", "2048x2048", "空字符串回退默认"),
            ("0x0", "2048x2048", "0 值回退默认"),
        ],
    )
    def test_normalize_image_size(self, raw: str, expected: str, reason: str) -> None:
        """测试 size 归一化的各种场景"""
        actual = VolcengineCVAdapter._normalize_image_size(raw)
        assert (
            actual == expected
        ), f"{reason}: 输入 {raw!r} 期望 {expected!r} 实际 {actual!r}"

    def test_normalize_image_size_none(self) -> None:
        """None 输入回退默认"""
        assert VolcengineCVAdapter._normalize_image_size(None) == "2048x2048"  # type: ignore[arg-type]


class TestVolcengineCVAdapterVideoMockHTTP:
    """VolcengineCVAdapter 视频生成 Mock HTTP 测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> VolcengineCVAdapter:
        """创建适配器实例"""
        config = ProviderConfig(provider_type="volcengine_cv", api_key=mock_api_key)
        return VolcengineCVAdapter(config=config)

    def _mock_response(self, data: dict, status_code: int = 200) -> MagicMock:
        """创建模拟 HTTP 响应"""
        mock_resp = MagicMock()
        mock_resp.status_code = status_code
        mock_resp.json = MagicMock(return_value=data)
        mock_resp.headers = {}
        return mock_resp

    @pytest.mark.asyncio
    async def test_video_create_basic(self, adapter: VolcengineCVAdapter) -> None:
        """测试基础视频创建请求（方舟 content 结构）"""
        await adapter.start()

        mock_result = {
            "id": "cgt-2025-abc123",
            "status": "queued",
        }

        with patch.object(
            adapter._http_client, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = self._mock_response(mock_result)

            result = await adapter.video_create(
                model="doubao-seedance-1-0-pro-250528",
                prompt="A cat running in the park",
            )

            assert isinstance(result, VideoTask)
            assert result.task_id == "cgt-2025-abc123"
            assert result.model == "doubao-seedance-1-0-pro-250528"
            assert result.status == "pending"

            # 验证请求：方舟端点 /contents/generations/tasks，body 为 content 数组结构
            call_args = mock_post.call_args
            assert "/contents/generations/tasks" in str(call_args)
            body = call_args.kwargs.get("json") or call_args.args[0]
            assert body["model"] == "doubao-seedance-1-0-pro-250528"
            # content 是数组，首元素为 text 类型
            assert isinstance(body["content"], list)
            assert body["content"][0]["type"] == "text"
            assert "A cat running in the park" in body["content"][0]["text"]

        await adapter.close()

    @pytest.mark.asyncio
    async def test_video_create_with_params(self, adapter: VolcengineCVAdapter) -> None:
        """测试带参数的视频创建（参数转为方舟 flag）"""
        await adapter.start()

        mock_result = {
            "id": "cgt-2025-xyz789",
            "status": "queued",
        }

        with patch.object(
            adapter._http_client, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = self._mock_response(mock_result)

            result = await adapter.video_create(
                model="doubao-seedance-1-0-pro-250528",
                prompt="A beautiful sunset",
                duration=5,
                aspect_ratio="16:9",
                resolution="1080p",
                seed=42,
                watermark=True,
            )

            assert isinstance(result, VideoTask)

            # 验证请求：参数转换为方舟 flag 拼入 text
            call_args = mock_post.call_args
            body = call_args.kwargs.get("json") or call_args.args[0]
            text = body["content"][0]["text"]
            assert "--dur 5" in text
            assert "--rt 16:9" in text
            assert "--rs 1080p" in text
            assert "--seed 42" in text
            assert "--wm true" in text

        await adapter.close()

    @pytest.mark.asyncio
    async def test_video_create_image2video(self, adapter: VolcengineCVAdapter) -> None:
        """测试图生视频模式（content 数组含 image_url）"""
        await adapter.start()

        mock_result = {
            "id": "cgt-2025-img2vid-001",
            "status": "queued",
        }

        with patch.object(
            adapter._http_client, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = self._mock_response(mock_result)

            result = await adapter.video_create(
                model="doubao-seedance-1-0-pro-250528",
                prompt="Make this image move",
                mode="image2video",
                reference_images=["https://example.com/input.jpg"],
            )

            assert isinstance(result, VideoTask)

            # 验证请求 body：content 数组含 text + image_url 两个元素
            call_args = mock_post.call_args
            body = call_args.kwargs.get("json") or call_args.args[0]
            assert len(body["content"]) == 2
            assert body["content"][1]["type"] == "image_url"
            assert (
                body["content"][1]["image_url"]["url"]
                == "https://example.com/input.jpg"
            )

        await adapter.close()

    @pytest.mark.asyncio
    async def test_video_poll_pending(self, adapter: VolcengineCVAdapter) -> None:
        """测试查询视频状态（pending）"""
        await adapter.start()

        mock_result = {
            "id": "cgt-2025-abc123",
            "status": "queued",
            "progress": 0,
            "created": 1700000000,
            "updated": 1700000100,
        }

        with patch.object(
            adapter._http_client, "get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = self._mock_response(mock_result)

            result = await adapter.video_poll(task_id="cgt-2025-abc123")

            assert isinstance(result, VideoStatus)
            assert result.task_id == "cgt-2025-abc123"
            assert result.status == "pending"

            # 验证请求 URL：方舟端点 /contents/generations/tasks/{task_id}
            call_args = mock_get.call_args
            assert "/contents/generations/tasks/cgt-2025-abc123" in str(call_args)

        await adapter.close()

    @pytest.mark.asyncio
    async def test_video_poll_processing(self, adapter: VolcengineCVAdapter) -> None:
        """测试查询视频状态（processing）"""
        await adapter.start()

        mock_result = {
            "id": "vid-abc123",
            "status": "processing",
            "progress": 50,
        }

        with patch.object(
            adapter._http_client, "get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = self._mock_response(mock_result)

            result = await adapter.video_poll(task_id="vid-abc123")

            assert result.status == "processing"
            assert result.progress == 50

        await adapter.close()

    @pytest.mark.asyncio
    async def test_video_poll_success(self, adapter: VolcengineCVAdapter) -> None:
        """测试查询视频状态（success）"""
        await adapter.start()

        mock_result = {
            "id": "vid-abc123",
            "status": "succeeded",
            "video_url": "https://cdn.example.com/video.mp4",
            "progress": 100,
        }

        with patch.object(
            adapter._http_client, "get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = self._mock_response(mock_result)

            result = await adapter.video_poll(task_id="vid-abc123")

            assert result.status == "success"
            assert result.video_url == "https://cdn.example.com/video.mp4"

        await adapter.close()

    @pytest.mark.asyncio
    async def test_video_poll_failed(self, adapter: VolcengineCVAdapter) -> None:
        """测试查询视频状态（failed）"""
        await adapter.start()

        mock_result = {
            "id": "vid-abc123",
            "status": "failed",
            "error": {"message": "Insufficient credits"},
        }

        with patch.object(
            adapter._http_client, "get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = self._mock_response(mock_result)

            result = await adapter.video_poll(task_id="vid-abc123")

            assert result.status == "failed"
            assert result.error == "Insufficient credits"

        await adapter.close()
