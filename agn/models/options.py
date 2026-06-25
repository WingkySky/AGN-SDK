"""
AGN-SDK 统一请求选项模型

定义所有 AI 能力的标准化请求参数，用户使用同一套参数调用不同模型，
适配器内部自动映射到各厂商的特定字段名。

设计原则：
1. 通用参数标准化（temperature、max_tokens、tools 等统一命名）
2. 厂商特有参数通过 extra_params 透传
3. 能力（function calling、vision、reasoning）通过 capabilities 声明
4. 参数自动映射（在适配器内部完成通用名 → 厂商特定名转换）
"""

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

# ==================== 通用枚举 ====================


class ReasoningEffort(str, Enum):
    """推理努力程度（统一思考模式）"""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    AUTO = "auto"


class ImageStyle(str, Enum):
    """图像风格"""

    NATURAL = "natural"
    VIVID = "vivid"
    ANIME = "anime"
    PHOTOREALISTIC = "photorealistic"
    DIGITAL_ART = "digital_art"
    OIL_PAINTING = "oil_painting"
    WATERCOLOR = "watercolor"
    SKETCH = "sketch"
    THREE_D = "3d"
    CYBERPUNK = "cyberpunk"


class VideoDuration(str, Enum):
    """视频时长"""

    DURATION_4S = "4s"
    DURATION_5S = "5s"
    DURATION_8S = "8s"
    DURATION_10S = "10s"
    DURATION_15S = "15s"
    DURATION_20S = "20s"


class AspectRatio(str, Enum):
    """画面比例"""

    SQUARE = "1:1"
    LANDSCAPE_16_9 = "16:9"
    PORTRAIT_9_16 = "9:16"
    LANDSCAPE_4_3 = "4:3"
    PORTRAIT_3_4 = "3:4"
    CINEMA_21_9 = "21:9"
    ULTRAWIDE = "32:9"


class ResponseFormat(str, Enum):
    """响应格式"""

    TEXT = "text"
    JSON_OBJECT = "json_object"
    JSON_SCHEMA = "json_schema"


# ==================== 工具/函数定义 ====================


class FunctionParameter(BaseModel):
    """函数参数定义（OpenAPI Schema 子集）"""

    type: str = Field(..., description="参数类型：string/number/boolean/object/array")
    description: str | None = Field(None, description="参数描述")
    enum: list[Any] | None = Field(None, description="枚举值")
    properties: dict[str, "FunctionParameter"] | None = Field(
        None, description="对象属性"
    )
    required: list[str] | None = Field(None, description="必填参数列表")
    items: "FunctionParameter | None" = Field(None, description="数组元素类型")

    model_config = {"extra": "allow"}


class FunctionDefinition(BaseModel):
    """函数定义（统一格式）"""

    name: str = Field(..., description="函数名称")
    description: str | None = Field(None, description="函数描述")
    parameters: dict[str, Any] | None = Field(
        None, description="函数参数（JSON Schema）"
    )

    model_config = {"extra": "allow"}


class ToolDefinition(BaseModel):
    """工具定义（统一格式）"""

    type: Literal["function", "web_search", "code_interpreter", "retrieval"] = Field(
        default="function",
        description="工具类型",
    )
    function: FunctionDefinition | None = Field(
        None, description="函数定义（type=function 时必填）"
    )

    model_config = {"extra": "allow"}


class ToolCall(BaseModel):
    """工具调用结果"""

    id: str = Field(..., description="工具调用 ID")
    type: str = Field("function", description="工具类型")
    function: dict[str, Any] = Field(..., description="函数调用信息：name + arguments")

    model_config = {"extra": "allow"}


class ToolChoice(str, Enum):
    """工具选择策略"""

    NONE = "none"
    AUTO = "auto"
    REQUIRED = "required"


# ==================== 对话请求选项 ====================


class ChatOptions(BaseModel):
    """
    统一对话请求选项

    所有模型通用的对话参数，适配器内部自动映射到各厂商的字段名。
    厂商特有参数通过 extra_params 透传。
    """

    # 基础生成参数
    temperature: float | None = Field(
        None, ge=0.0, le=2.0, description="温度系数（0-2，越高越随机）"
    )
    top_p: float | None = Field(None, ge=0.0, le=1.0, description="核采样（0-1）")
    top_k: int | None = Field(None, ge=1, description="Top-K 采样")
    max_tokens: int | None = Field(None, ge=1, description="最大生成 token 数")
    stop: str | list[str] | None = Field(None, description="停止词")
    n: int = Field(1, ge=1, le=16, description="生成回复数量")
    presence_penalty: float | None = Field(
        None, ge=-2.0, le=2.0, description="存在惩罚（-2到2）"
    )
    frequency_penalty: float | None = Field(
        None, ge=-2.0, le=2.0, description="频率惩罚（-2到2）"
    )
    repetition_penalty: float | None = Field(
        None, ge=0.0, description="重复惩罚（部分模型用）"
    )
    min_p: float | None = Field(None, ge=0.0, le=1.0, description="Min-P 采样")
    seed: int | None = Field(None, description="随机种子（可复现）")

    # 响应格式
    response_format: ResponseFormat | dict[str, Any] | None = Field(
        None, description="响应格式"
    )
    json_schema: dict[str, Any] | None = Field(None, description="JSON Schema 约束")

    # 工具/函数调用
    tools: list[ToolDefinition] | None = Field(None, description="可用工具列表")
    tool_choice: ToolChoice | str | None = Field(None, description="工具选择策略")
    parallel_tool_calls: bool | None = Field(None, description="是否允许并行工具调用")

    # 深度推理/思考模式
    reasoning: bool = Field(False, description="是否启用深度思考/推理模式")
    reasoning_effort: ReasoningEffort | None = Field(None, description="推理努力程度")
    thinking_budget: int | None = Field(None, ge=0, description="思考 token 预算")

    # 联网搜索
    web_search: bool = Field(False, description="是否启用联网搜索")
    search_recency_filter: str | None = Field(
        None, description="搜索时间过滤：day/week/month/year"
    )
    search_domain_filter: list[str] | None = Field(None, description="搜索域名白名单")

    # 多模态
    images: list[str] | None = Field(
        None, description="图片 URL/data URI 列表（视觉理解）"
    )
    detail: Literal["low", "high", "auto"] | None = Field(
        "auto", description="图片细节级别"
    )

    # 流式输出
    stream: bool = Field(False, description="是否流式输出")
    stream_options: dict[str, Any] | None = Field(
        None, description="流式选项（如 include_usage）"
    )

    # 用户标识
    user: str | None = Field(None, description="用户标识（用于风控/限流）")

    # 厂商特有参数透传
    extra_params: dict[str, Any] = Field(
        default_factory=dict,
        description="厂商特有参数透传（不会被映射，直接加入请求体）",
    )

    model_config = {"extra": "allow"}

    def to_kwargs(self) -> dict[str, Any]:
        """转换为 kwargs 字典（排除 None 值和默认值）"""
        result: dict[str, Any] = {}
        for key, value in self.model_dump(exclude_none=True).items():
            if key == "extra_params":
                result.update(value or {})
                continue
            if key == "tools" and value:
                result["tools"] = value
                continue
            result[key] = value
        return result


# ==================== 图像生成请求选项 ====================


class ImageOptions(BaseModel):
    """
    统一图像生成请求选项

    所有图像模型通用参数，适配器内部自动映射。
    """

    # 基础参数
    n: int = Field(1, ge=1, le=10, description="生成图片数量")
    size: str | None = Field(
        None, description="尺寸（如 1024x1024），或使用 width/height"
    )
    width: int | None = Field(None, ge=64, le=4096, description="宽度（像素）")
    height: int | None = Field(None, ge=64, le=4096, description="高度（像素）")
    aspect_ratio: AspectRatio | str | None = Field(None, description="画面比例")

    # 风格和质量
    style: ImageStyle | str | None = Field(None, description="图像风格")
    quality: Literal["standard", "hd", "ultra"] | None = Field(
        None, description="生成质量"
    )

    # 负面提示词
    negative_prompt: str | None = Field(None, description="负面提示词")
    negative_prompts: list[str] | None = Field(None, description="负面提示词列表")

    # 高级参数
    seed: int | None = Field(None, description="随机种子")
    steps: int | None = Field(None, ge=1, le=100, description="推理步数")
    cfg_scale: float | None = Field(
        None, ge=1.0, le=20.0, description="CFG Scale（提示词相关性）"
    )
    sampler: str | None = Field(None, description="采样器名称")
    scheduler: str | None = Field(None, description="调度器")

    # 输出格式
    response_format: Literal["url", "b64_json"] = Field("url", description="返回格式")
    output_format: Literal["png", "jpeg", "webp"] | None = Field(
        None, description="输出图片格式"
    )

    # 参考图
    reference_images: list[str] | None = Field(
        None, description="参考图 URL/data URI（图生图/IP-Adapter）"
    )
    reference_strength: float | None = Field(
        None, ge=0.0, le=1.0, description="参考图强度"
    )

    # 图像编辑
    mask: str | None = Field(None, description="遮罩图片 data URI（局部重绘）")
    edit_mode: Literal["inpaint", "outpaint", "variation"] | None = Field(
        None, description="编辑模式"
    )

    # 厂商特有参数
    extra_params: dict[str, Any] = Field(
        default_factory=dict, description="厂商特有参数透传"
    )

    model_config = {"extra": "allow"}

    def to_kwargs(self) -> dict[str, Any]:
        """转换为 kwargs 字典（排除 None 值和默认值）"""
        result: dict[str, Any] = {}
        for key, value in self.model_dump(exclude_none=True).items():
            if key == "extra_params":
                result.update(value or {})
                continue
            result[key] = value
        return result


# ==================== 视频生成请求选项 ====================


class VideoOptions(BaseModel):
    """
    统一视频生成请求选项
    """

    # 基础参数
    duration: VideoDuration | int | None = Field(None, description="视频时长")
    fps: int | None = Field(None, ge=1, le=60, description="帧率")
    aspect_ratio: AspectRatio | str | None = Field(None, description="画面比例")
    resolution: str | None = Field(None, description="分辨率（如 720p、1080p）")
    width: int | None = Field(None, description="宽度")
    height: int | None = Field(None, description="高度")

    # 模式
    mode: Literal["text2video", "image2video", "video2video", "keyframes"] | str = (
        Field("text2video", description="生成模式")
    )

    # 参考素材
    reference_images: list[str] | None = Field(
        None, description="参考图片 URL（图生视频）"
    )
    reference_videos: list[str] | None = Field(
        None, description="参考视频 URL（视频生视频）"
    )
    keyframes: list[dict[str, Any]] | None = Field(None, description="关键帧列表")
    first_frame: str | None = Field(None, description="首帧图片")
    last_frame: str | None = Field(None, description="尾帧图片")

    # 风格和运动
    style: str | None = Field(None, description="视频风格")
    camera_motion: str | None = Field(None, description="镜头运动")
    motion_strength: float | None = Field(None, ge=0.0, le=10.0, description="运动强度")

    # 负面提示词
    negative_prompt: str | None = Field(None, description="负面提示词")

    # 高级参数
    seed: int | None = Field(None, description="随机种子")
    steps: int | None = Field(None, ge=1, description="推理步数")
    cfg_scale: float | None = Field(None, ge=1.0, description="CFG Scale")

    # 输出
    with_audio: bool | None = Field(None, description="是否生成音频")
    watermark: bool | None = Field(None, description="是否添加水印")

    # 厂商特有参数
    extra_params: dict[str, Any] = Field(
        default_factory=dict, description="厂商特有参数透传"
    )

    model_config = {"extra": "allow"}

    def to_kwargs(self) -> dict[str, Any]:
        """转换为 kwargs 字典（排除 None 值和默认值）"""
        result: dict[str, Any] = {}
        for key, value in self.model_dump(exclude_none=True).items():
            if key == "extra_params":
                result.update(value or {})
                continue
            result[key] = value
        return result


# ==================== 嵌入请求选项 ====================


class EmbedOptions(BaseModel):
    """
    统一文本嵌入请求选项
    """

    model: str | None = Field(
        None, description="嵌入模型名称（可选，使用 Provider 默认）"
    )
    dimensions: int | None = Field(None, ge=1, description="输出向量维度")
    encoding_format: Literal["float", "base64"] | None = Field(
        None, description="编码格式"
    )
    user: str | None = Field(None, description="用户标识")

    extra_params: dict[str, Any] = Field(
        default_factory=dict, description="厂商特有参数透传"
    )

    model_config = {"extra": "allow"}

    def to_kwargs(self) -> dict[str, Any]:
        """转换为 kwargs 字典（排除 None 值和默认值）"""
        result: dict[str, Any] = {}
        for key, value in self.model_dump(exclude_none=True).items():
            if key == "extra_params":
                result.update(value or {})
                continue
            result[key] = value
        return result


# ==================== 嵌入结果 ====================


class EmbeddingResult(BaseModel):
    """嵌入结果"""

    object: str = Field("list", description="对象类型")
    data: list[dict[str, Any]] = Field(..., description="嵌入向量列表")
    model: str = Field(..., description="使用的模型")
    usage: dict[str, int] | None = Field(None, description="使用统计")

    model_config = {"extra": "allow"}

    def get_embeddings(self) -> list[list[float]]:
        """获取所有嵌入向量"""
        return [item.get("embedding", []) for item in self.data]


# ==================== 语音转文字请求选项 ====================


class TranscribeOptions(BaseModel):
    """
    统一语音转文字（ASR）请求选项
    """

    # 基础参数
    file: str | bytes | None = Field(
        None, description="音频文件（文件路径、URL、base64 或二进制数据）"
    )
    model: str | None = Field(None, description="模型名称")
    language: str | None = Field(None, description="语言代码（如 'zh'、'en'）")
    prompt: str | None = Field(
        None, description="提示词（改善专有名词识别、纠正错别字）"
    )

    # 响应格式
    response_format: Literal["json", "text", "srt", "vtt", "verbose_json"] = Field(
        "json", description="响应格式"
    )

    # 高级参数
    temperature: float | None = Field(
        None, ge=0.0, le=1.0, description="温度系数（0-1）"
    )
    timestamp_granularities: list[Literal["word", "segment"]] | None = Field(
        None, description="时间戳精度"
    )

    # 翻译模式（将音频翻译为英文，仅部分模型支持）
    translate: bool = Field(False, description="是否翻译为英文")

    # 流式输出
    stream: bool = Field(False, description="是否流式输出（仅部分模型支持）")

    # 厂商特有参数
    extra_params: dict[str, Any] = Field(
        default_factory=dict, description="厂商特有参数透传"
    )

    model_config = {"extra": "allow"}

    def to_kwargs(self) -> dict[str, Any]:
        """转换为 kwargs 字典（排除 None 值和默认值）"""
        result: dict[str, Any] = {}
        for key, value in self.model_dump(exclude_none=True).items():
            if key == "extra_params":
                result.update(value or {})
                continue
            result[key] = value
        return result


# ==================== 文字转语音请求选项 ====================


class SpeechOptions(BaseModel):
    """
    统一文字转语音（TTS）请求选项
    """

    # 基础参数
    input: str | None = Field(None, description="要合成的文本")
    model: str | None = Field(None, description="模型名称")
    voice: str | None = Field(None, description="音色（如 'alloy'、'echo'、'nova'）")

    # 输出格式
    response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] = Field(
        "mp3", description="音频输出格式"
    )

    # 音频参数
    speed: float | None = Field(
        None, ge=0.25, le=4.0, description="语速（0.25-4.0，默认 1.0）"
    )
    volume: float | None = Field(
        None, ge=0.0, le=2.0, description="音量（0-2，默认 1.0）"
    )
    pitch: float | None = Field(
        None, ge=-1.0, le=1.0, description="音调（-1 到 1，默认 0）"
    )

    # 情感/风格（部分厂商支持）
    emotion: str | None = Field(
        None, description="情感风格（如 'happy'、'sad'、'neutral'）"
    )
    style: str | None = Field(None, description="说话风格")

    # 厂商特有参数
    extra_params: dict[str, Any] = Field(
        default_factory=dict, description="厂商特有参数透传"
    )

    model_config = {"extra": "allow"}

    def to_kwargs(self) -> dict[str, Any]:
        """转换为 kwargs 字典（排除 None 值和默认值）"""
        result: dict[str, Any] = {}
        for key, value in self.model_dump(exclude_none=True).items():
            if key == "extra_params":
                result.update(value or {})
                continue
            result[key] = value
        return result


# ==================== 参数映射规则 ====================


class ParameterMapping:
    """
    参数映射规则

    定义通用参数名 → 厂商特定参数名的映射关系。
    支持：
    - 简单重命名: {"temperature": "temp"}
    - 值映射: {"reasoning_effort": {"high": {"thinking": "high"}}}
    - 条件映射: 根据 model 选择不同映射
    """

    def __init__(
        self,
        rename_map: dict[str, str | None] | None = None,
        value_map: dict[str, dict[Any, Any]] | None = None,
        extra_headers: dict[str, str] | None = None,
        remove_when_none: bool = True,
    ):
        self.rename_map = rename_map or {}
        self.value_map = value_map or {}
        self.extra_headers = extra_headers or {}
        self.remove_when_none = remove_when_none

    def apply(self, params: dict[str, Any]) -> dict[str, Any]:
        """应用映射规则"""
        result: dict[str, Any] = {}

        for key, value in params.items():
            if self.remove_when_none and value is None:
                continue

            # 键名重命名
            target_key = self.rename_map.get(key, key)
            if target_key is None:
                # None 表示移除该参数
                continue

            # 值映射
            if key in self.value_map and value in self.value_map[key]:
                mapped = self.value_map[key][value]
                if isinstance(mapped, dict):
                    # 值映射为 dict 时展开到结果
                    result.update(mapped)
                    continue
                else:
                    value = mapped

            result[target_key] = value

        return result


# ==================== 预定义映射规则（供适配器使用）====================


# OpenAI 兼容映射（大部分厂商用这个）
OPENAI_COMPATIBLE_MAPPING = ParameterMapping(
    rename_map={
        "web_search": None,
        "search_recency_filter": None,
        "search_domain_filter": None,
        "repetition_penalty": "repetition_penalty",
        "parallel_tool_calls": "parallel_tool_calls",
    },
    value_map={
        "reasoning": {
            True: {"reasoning_effort": "medium"},
            False: None,
        },
    },
)

# Anthropic 映射
ANTHROPIC_MAPPING = ParameterMapping(
    rename_map={
        "max_tokens": "max_tokens",
        "top_p": "top_p",
        "top_k": "top_k",
        "temperature": "temperature",
        "stop": "stop_sequences",
        "tools": "tools",
        "system": "system",
    },
    value_map={
        "reasoning": {
            True: {"thinking": {"type": "enabled"}},
            False: {"thinking": {"type": "disabled"}},
        },
        "reasoning_effort": {
            ReasoningEffort.LOW: {
                "thinking": {"type": "enabled", "budget_tokens": 1024}
            },
            ReasoningEffort.MEDIUM: {
                "thinking": {"type": "enabled", "budget_tokens": 4096}
            },
            ReasoningEffort.HIGH: {
                "thinking": {"type": "enabled", "budget_tokens": 16384}
            },
        },
    },
)

# Google Gemini 映射
GEMINI_MAPPING = ParameterMapping(
    rename_map={
        "max_tokens": "maxOutputTokens",
        "top_p": "topP",
        "top_k": "topK",
        "stop": "stopSequences",
        "response_format": "response_mime_type",
    },
    value_map={
        "reasoning": {
            True: {"thinkingConfig": {"thinkingBudget": -1}},
        },
        "web_search": {
            True: {"tools": [{"google_search": {}}]},
        },
    },
)

# Cohere 映射
COHERE_MAPPING = ParameterMapping(
    rename_map={
        "max_tokens": "max_tokens",
        "temperature": "temperature",
        "top_p": "p",
        "top_k": "k",
        "tools": "tools",
        "system": "preamble",
    },
)
