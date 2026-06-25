"""
AGN-SDK 适配器层

包含适配器基类和所有 Provider 适配器实现。
"""

from agn.adapters.additional_models import (
    GrokAdapter,
    GroqAdapter,
    HunyuanAdapter,
    SenseNovaAdapter,
    YiAdapter,
)
from agn.adapters.aggregation_platforms import (
    CloudflareAIAdapter,
    FireworksAIAdapter,
    SiliconFlowAdapter,
    TogetherAIAdapter,
)

# 导入所有适配器（自动注册）
from agn.adapters.agnes import AgnesAdapter
from agn.adapters.anthropic import AnthropicAdapter
from agn.adapters.audio_adapters import (
    AssemblyAIAdapter,
    CartesiaAdapter,
    DeepgramAdapter,
    EdgeTTSAdapter,
    ElevenLabsAdapter,
)
from agn.adapters.azure import AzureAdapter
from agn.adapters.base import BaseAdapter, Capabilities
from agn.adapters.chinese import (
    DoubaoAdapter,
    ErnieAdapter,
    KimiAdapter,
    MiniMaxAdapter,
    QwenAdapter,
    ZhipuAdapter,
)
from agn.adapters.emerging_models import (
    IdeogramAdapter,
    LlamaAdapter,
    LumaAdapter,
)
from agn.adapters.factory import AdapterFactory
from agn.adapters.gemini import GeminiAdapter
from agn.adapters.kling import KlingAdapter
from agn.adapters.more_models import (
    CohereAdapter,
    DeepSeekAdapter,
    MistralAdapter,
    PerplexityAdapter,
    StepFunAdapter,
)
from agn.adapters.openai import OpenAIAdapter
from agn.adapters.pika import PikaAdapter
from agn.adapters.runway import RunwayAdapter
from agn.adapters.stability import StabilityAdapter
from agn.adapters.volcengine_cv import VolcengineCVAdapter

__all__ = [
    "BaseAdapter",
    "Capabilities",
    "AdapterFactory",
    "AgnesAdapter",
    "OpenAIAdapter",
    "AzureAdapter",
    "RunwayAdapter",
    "PikaAdapter",
    "StabilityAdapter",
    "QwenAdapter",
    "ZhipuAdapter",
    "DoubaoAdapter",
    "ErnieAdapter",
    "KimiAdapter",
    "MiniMaxAdapter",
    "AnthropicAdapter",
    "GeminiAdapter",
    "KlingAdapter",
    "VolcengineCVAdapter",
    "DeepSeekAdapter",
    "StepFunAdapter",
    "MistralAdapter",
    "CohereAdapter",
    "PerplexityAdapter",
    "GrokAdapter",
    "YiAdapter",
    "SenseNovaAdapter",
    "HunyuanAdapter",
    "GroqAdapter",
    "SiliconFlowAdapter",
    "TogetherAIAdapter",
    "FireworksAIAdapter",
    "CloudflareAIAdapter",
    "ElevenLabsAdapter",
    "DeepgramAdapter",
    "AssemblyAIAdapter",
    "CartesiaAdapter",
    "EdgeTTSAdapter",
    "IdeogramAdapter",
    "LumaAdapter",
    "LlamaAdapter",
]
