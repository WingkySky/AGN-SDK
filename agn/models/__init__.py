"""
AGN-SDK 数据模型

包含通用模型、文本对话模型、图像生成模型、视频生成模型、语音模型、统一请求选项。
"""

from agn.models.audio import (
    AudioResponseFormat,
    SpeechResult,
    SpeechVoice,
    TranscriptionResult,
    TranscriptionSegment,
    TranscriptionWord,
)
from agn.models.chat import (
    ChatChoice,
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionDelta,
    ChatCompletionRequest,
    ChatFunction,
    ChatMessage,
    ChatUsage,
)
from agn.models.common import (
    ImageSize,
    ModelInfo,
    ModelType,
    ProviderConfig,
    ProviderInfo,
    TaskStatus,
    VideoMode,
)
from agn.models.image import (
    ImageData,
    ImageEditRequest,
    ImageGenerationOptions,
    ImageGenerationResult,
    ImageVariationRequest,
)
from agn.models.options import (
    ANTHROPIC_MAPPING,
    AspectRatio,
    ChatOptions,
    COHERE_MAPPING,
    EmbedOptions,
    EmbeddingResult,
    FunctionDefinition,
    FunctionParameter,
    GEMINI_MAPPING,
    ImageOptions,
    ImageStyle,
    OPENAI_COMPATIBLE_MAPPING,
    ParameterMapping,
    ReasoningEffort,
    ResponseFormat,
    SpeechOptions,
    ToolCall,
    ToolChoice,
    ToolDefinition,
    TranscribeOptions,
    VideoDuration,
    VideoOptions,
)
from agn.models.video import (
    VideoGenerationOptions,
    VideoStatus,
    VideoTask,
    VideoTaskCreate,
)

__all__ = [
    # 通用模型
    "ProviderConfig",
    "ModelInfo",
    "ProviderInfo",
    "ModelType",
    "VideoMode",
    "ImageSize",
    "TaskStatus",
    # 文本对话模型
    "ChatMessage",
    "ChatFunction",
    "ChatChoice",
    "ChatUsage",
    "ChatCompletion",
    "ChatCompletionChunk",
    "ChatCompletionDelta",
    "ChatCompletionRequest",
    # 图像生成模型
    "ImageData",
    "ImageGenerationResult",
    "ImageEditRequest",
    "ImageVariationRequest",
    "ImageGenerationOptions",
    # 视频生成模型
    "VideoTask",
    "VideoStatus",
    "VideoGenerationOptions",
    "VideoTaskCreate",
    # 语音模型
    "TranscriptionResult",
    "TranscriptionSegment",
    "TranscriptionWord",
    "SpeechResult",
    "AudioResponseFormat",
    "SpeechVoice",
    # 统一请求选项
    "ChatOptions",
    "ImageOptions",
    "VideoOptions",
    "EmbedOptions",
    "EmbeddingResult",
    "TranscribeOptions",
    "SpeechOptions",
    "ToolDefinition",
    "ToolCall",
    "ToolChoice",
    "FunctionDefinition",
    "FunctionParameter",
    "ReasoningEffort",
    "ImageStyle",
    "VideoDuration",
    "AspectRatio",
    "ResponseFormat",
    "ParameterMapping",
    "OPENAI_COMPATIBLE_MAPPING",
    "ANTHROPIC_MAPPING",
    "GEMINI_MAPPING",
    "COHERE_MAPPING",
]
