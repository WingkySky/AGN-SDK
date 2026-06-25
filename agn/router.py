"""
AGN-SDK 路由器

支持多 Provider 路由、负载均衡、Fallback、权重路由等高级功能。
"""

import logging
import random
from typing import Any, Literal, cast

from agn.adapters.factory import AdapterFactory
from agn.core.errors import ModelNotFoundError
from agn.models.audio import SpeechResult, TranscriptionResult
from agn.models.chat import ChatCompletion, ChatMessage
from agn.models.common import ModelInfo, ProviderConfig
from agn.models.image import ImageGenerationResult
from agn.models.video import VideoStatus, VideoTask

logger = logging.getLogger(__name__)


# 路由策略类型
RoutingStrategy = Literal["first", "round_robin", "random", "weighted", "latency"]


class Router:
    """
    多 Provider 路由器

    支持配置多个 Provider，自动选择合适的 Provider 处理请求。
    提供负载均衡、Fallback、权重路由等高级功能。

    使用方式:

        providers = [
            {"provider_type": "agnes", "api_key": "key1", "weight": 3},
            {"provider_type": "openai", "api_key": "key2", "weight": 2},
            {"provider_type": "runway", "api_key": "key3"},
        ]

        router = Router(providers=providers, strategy="weighted")

        # 自动选择 Provider
        response = await router.chat(model="claude-3-opus", messages=[...])
        result = await router.image_generate(model="dall-e-3", prompt="...")
        task = await router.video_create(model="gen-3", prompt="...")
    """

    # 模型到 Provider 的默认映射
    MODEL_PROVIDER_MAP: dict[str, str] = {
        # Agnes AI
        "claude-3-opus": "agnes",
        "claude-3-sonnet": "agnes",
        "claude-3-haiku": "agnes",
        "dall-e-3": "agnes",
        "video-gen-1": "agnes",
        "video-gen-2": "agnes",
        # OpenAI
        "gpt-4o": "openai",
        "gpt-4-turbo": "openai",
        "gpt-4": "openai",
        "gpt-3.5-turbo": "openai",
        # OpenAI 语音模型
        "whisper-1": "openai",
        "gpt-4o-transcribe": "openai",
        "gpt-4o-mini-transcribe": "openai",
        "tts-1": "openai",
        "tts-1-hd": "openai",
        # Runway
        "gen-3": "runway",
        "gen-3-turbo": "runway",
        # Pika
        "pika-1.0": "pika",
        "pika-2": "pika",
        # Stability AI
        "stable-diffusion-xl-1024-v1-1": "stability",
        "stable-diffusion-3-medium": "stability",
        "stable-diffusion-3-fast": "stability",
        "sdxl": "stability",
        "sd3": "stability",
        # 通义千问
        "qwen-turbo": "qwen",
        "qwen-plus": "qwen",
        "qwen-max": "qwen",
        "qwen-vl-max": "qwen",
        # 通义语音模型
        "sensevoice-v1": "qwen",
        "cosyvoice-v1": "qwen",
        # 智谱 AI
        "glm-4": "zhipu",
        "glm-4v": "zhipu",
        "glm-3-turbo": "zhipu",
        # Anthropic Claude
        "claude-3-opus-20240229": "anthropic",
        "claude-3-sonnet-20240229": "anthropic",
        "claude-3-haiku-20240307": "anthropic",
        "claude-3-5-sonnet-20241022": "anthropic",
        "claude-3-5-haiku-20241022": "anthropic",
        # Google Gemini
        "gemini-2.5-pro": "gemini",
        "gemini-2.5-flash": "gemini",
        "gemini-1.5-pro": "gemini",
        "gemini-1.5-flash": "gemini",
        # 豆包 (Doubao)
        "doubao-pro-4k": "doubao",
        "doubao-pro-32k": "doubao",
        "doubao-pro-128k": "doubao",
        "doubao-pro-256k": "doubao",
        "doubao-lite-4k": "doubao",
        "doubao-lite-32k": "doubao",
        "doubao-lite-128k": "doubao",
        "doubao-seed-2-0-lite-260215": "doubao",
        "doubao-seed-2-0-pro-260215": "doubao",
        "doubao-seed-2-0-mini-260428": "doubao",
        "doubao-2-1-pro": "doubao",
        # 豆包语音模型
        "doubao-asr": "doubao",
        "doubao-tts": "doubao",
        # 文心一言
        "completions_pro": "ernie",
        "completions": "ernie",
        "ernie-lite-8k": "ernie",
        # 可灵 Kling
        "kling-v1": "kling",
        "kling-v1-5": "kling",
        "kling-v2": "kling",
        # Kimi (月之暗面)
        "moonshot-v1-8k": "kimi",
        "moonshot-v1-32k": "kimi",
        "moonshot-v1-128k": "kimi",
        "kimi-k2.5": "kimi",
        "kimi-k2.6": "kimi",
        "kimi-k2.7-code": "kimi",
        # MiniMax
        "abab6.5s-chat": "minimax",
        "abab6.5-chat": "minimax",
        "MiniMax-Text-01": "minimax",
        "MiniMax-VL-01": "minimax",
        "MiniMax-M1": "minimax",
        # MiniMax 语音模型
        "abab-asr": "minimax",
        "abab-tts": "minimax",
        "speech-01": "minimax",
        # 火山引擎 Seedream/Seedance
        "seedream-5.0": "seedream",
        "seedream-4.0": "seedream",
        "seedream-3.0": "seedream",
        "seedance-2.0": "seedance",
        "seedance-2.0-mini": "seedance",
        "seedance-1.0": "seedance",
        # DeepSeek
        "deepseek-v4-pro": "deepseek",
        "deepseek-v4-flash": "deepseek",
        "deepseek-chat": "deepseek",
        "deepseek-reasoner": "deepseek",
        "deepseek-coder": "deepseek",
        # 阶跃星辰 StepFun
        "step-3-flash": "stepfun",
        "step-3-8k": "stepfun",
        "step-3-32k": "stepfun",
        "step-3-128k": "stepfun",
        "step-2-mini": "stepfun",
        "step-1o-turbo": "stepfun",
        "step-1o-mini": "stepfun",
        # Mistral AI
        "mistral-sonnet-4-2505": "mistral",
        "mistral-nemo-2407": "mistral",
        "mistral-small-2407": "mistral",
        "mixtral-8x22b-2404": "mistral",
        "mixtral-8x7b-2407": "mistral",
        "codestral-2405": "mistral",
        "mathstral-2407": "mistral",
        # Cohere
        "command-r-plus-08-2024": "cohere",
        "command-r-08-2024": "cohere",
        "command-plus": "cohere",
        "command": "cohere",
        "c4ai-aya-23-8b": "cohere",
        "c4ai-aya-23-35b": "cohere",
        # Perplexity AI
        "sonar-pro": "perplexity",
        "sonar": "perplexity",
        "sonar-pro-realtime": "perplexity",
        "sonar-reasoning-pro": "perplexity",
        "sonar-reasoning": "perplexity",
        "llama-3.1-sonar-small-128k-online": "perplexity",
        "llama-3.1-sonar-large-128k-online": "perplexity",
        "llama-3.1-sonar-huge-128k-online": "perplexity",
        # xAI Grok
        "grok-3": "grok",
        "grok-3-latest": "grok",
        "grok-3-mini": "grok",
        "grok-2": "grok",
        "grok-2-latest": "grok",
        # 零一万物 Yi
        "yi-lightning": "yi",
        "yi-medium": "yi",
        "yi-large": "yi",
        "yi-large-turbo": "yi",
        "yi-34b-chat-0205": "yi",
        "yi-34b-chat-200k": "yi",
        "yi-vl-plus": "yi",
        # 商汤日日新 SenseNova
        "sensechat": "sensenova",
        "sensechat-4.0": "sensenova",
        "sensechat-5": "sensenova",
        "sensenova-llm-v1": "sensenova",
        "sensenova-llm-v2": "sensenova",
        "sensenova-llm-v3": "sensenova",
        # 腾讯混元 Hunyuan
        "hunyuan-turbo": "hunyuan",
        "hunyuan-latest": "hunyuan",
        "hunyuan-pro": "hunyuan",
        "hunyuan-lite": "hunyuan",
        "hunyuan-standard": "hunyuan",
        "hunyuan-vision": "hunyuan",
        "hunyuan-code": "hunyuan",
        # Groq
        "llama-3.3-70b-versatile": "groq",
        "llama-3.1-70b-versatile": "groq",
        "llama-3.1-8b-instant": "groq",
        "llama3-70b-8192": "groq",
        "llama3-8b-8192": "groq",
        "mixtral-8x7b-32768": "groq",
        "gemma2-9b-it": "groq",
        "gemma-7b-it": "groq",
        # Groq Whisper 语音模型 (LPU 极速推理)
        "whisper-large-v3": "groq",
        "whisper-large-v3-turbo": "groq",
        "distil-whisper-large-v3-en": "groq",
        # SiliconFlow
        "GLM-4.7": "siliconflow",
        "deepseek-ai/DeepSeek-V3.2": "siliconflow",
        "Qwen3-8B": "siliconflow",
        "Qwen3-14B": "siliconflow",
        "Qwen3-32B": "siliconflow",
        # SiliconFlow 语音模型
        "FunAudioLLM/SenseVoiceSmall": "siliconflow",
        "iic/SenseVoiceSmall": "siliconflow",
        # Together AI
        "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8": "togetherai",
        "meta-llama/Llama-3-70b-chat-hf": "togetherai",
        "Qwen/Qwen2.5-72B-Instruct-Turbo": "togetherai",
        "deepseek-ai/DeepSeek-V3": "togetherai",
        # Together AI 语音模型
        "openai/whisper-large-v3": "togetherai",
        "openai/whisper-large-v3-turbo": "togetherai",
        # Fireworks AI
        "accounts/fireworks/models/llama-v3p1-405b-instruct": "fireworksai",
        "accounts/fireworks/models/mixtral-8x22b-instruct": "fireworksai",
        "accounts/fireworks/models/deepseek-v3": "fireworksai",
        # Fireworks AI 语音模型
        "accounts/fireworks/models/whisper-v3": "fireworksai",
        # Cloudflare Workers AI
        "@cf/meta/llama-3.1-8b-instruct": "cloudflareai",
        "@cf/meta/llama-3.1-70b-instruct": "cloudflareai",
        "@cf/mistral/mistral-7b-instruct-v0.2": "cloudflareai",
        "@cf/qwen/qwen2.5-7b-instruct": "cloudflareai",
        "@cf/google/gemma-2-7b-it": "cloudflareai",
        # ElevenLabs TTS 语音合成
        "eleven_multilingual_v2": "elevenlabs",
        "eleven_multilingual_v1": "elevenlabs",
        "eleven_monolingual_v1": "elevenlabs",
        "eleven_turbo_v2_5": "elevenlabs",
        "eleven_turbo_v2": "elevenlabs",
        "eleven_flash_v2_5": "elevenlabs",
        # Deepgram ASR 高速语音识别
        "nova-3": "deepgram",
        "nova-2": "deepgram",
        "nova-2-general": "deepgram",
        "nova-2-meeting": "deepgram",
        "nova-2-phonecall": "deepgram",
        "nova-2-conversationalai": "deepgram",
        "nova-2-video": "deepgram",
        "nova-2-medical": "deepgram",
        "nova-2-finance": "deepgram",
        "nova-2-drivethru": "deepgram",
        "whisper-large": "deepgram",
        "whisper-medium": "deepgram",
        "whisper-small": "deepgram",
        "enhanced": "deepgram",
        "base": "deepgram",
        # AssemblyAI 企业级语音识别
        "best": "assemblyai",
        "nano": "assemblyai",
        # Cartesia Sonic 超低延迟TTS
        "sonic-2": "cartesia",
        "sonic-2-2025-04-01": "cartesia",
        "sonic-turbo": "cartesia",
        "sonic-preview": "cartesia",
        # Edge TTS 微软免费神经语音合成
        "edge-tts": "edge-tts",
        "edge_tts": "edge-tts",
        "edge-neural": "edge-tts",
        "zh-CN-XiaoxiaoNeural": "edge-tts",
        "zh-CN-YunxiNeural": "edge-tts",
        "en-US-JennyNeural": "edge-tts",
        # Ideogram 图像生成（文字渲染最强）
        "V_2A": "ideogram",
        "V_2A_TURBO": "ideogram",
        "V_2": "ideogram",
        "V_1": "ideogram",
        "V_1_TURBO": "ideogram",
        "ideogram-v2a": "ideogram",
        "ideogram-v2a-turbo": "ideogram",
        # Luma Dream Machine 高质量视频生成
        "ray-2": "luma",
        "ray-2-flash": "luma",
        "dream-machine": "luma",
        "luma-ray-2": "luma",
        # Meta Llama 官方 API
        "llama-4-maverick": "llama",
        "llama-4-scout": "llama",
        "llama-3.3-70b-instruct": "llama",
        "llama-3.1-405b-instruct": "llama",
        "llama-3.1-70b-instruct": "llama",
        "llama-3.1-8b-instruct": "llama",
        "llama-guard-4": "llama",
    }

    def __init__(
        self,
        providers: list[dict[str, Any]],
        default_provider: str | None = None,
        strategy: RoutingStrategy = "first",
        enable_fallback: bool = True,
        max_retries: int = 2,
    ) -> None:
        """
        初始化路由器

        Args:
            providers: Provider 配置列表，每项包含：
                - provider_type: Provider 类型
                - api_key: API Key
                - weight: 权重（weighted 策略用，默认 1）
                - 其他 ProviderConfig 字段
            default_provider: 默认 Provider（当无法自动选择时使用）
            strategy: 路由策略
                - first: 按顺序选第一个可用的
                - round_robin: 轮询
                - random: 随机
                - weighted: 按权重随机
                - latency: 按延迟（暂未实现，fallback 到 first）
            enable_fallback: 是否启用 Fallback（主 Provider 失败时切换备用）
            max_retries: Fallback 最大重试次数
        """
        self.providers: dict[str, ProviderConfig] = {}
        self._adapters: dict[str, Any] = {}
        self._provider_order: list[str] = []
        self._weights: dict[str, int] = {}
        self._current_index: int = 0
        self.default_provider = default_provider
        self.strategy: RoutingStrategy = strategy
        self.enable_fallback = enable_fallback
        self.max_retries = max_retries

        # Provider 健康状态（用于故障转移）
        self._provider_health: dict[str, bool] = {}
        # Provider 延迟统计（用于 latency 策略）
        self._provider_latency: dict[str, float] = {}

        # 初始化每个 Provider
        for config_dict in providers:
            provider_type = config_dict.get("provider_type")
            if not provider_type:
                continue

            # 提取权重
            weight = config_dict.pop("weight", 1)
            self._weights[provider_type] = max(1, int(weight))

            config = ProviderConfig(**config_dict)
            self.providers[provider_type] = config
            self._provider_order.append(provider_type)
            self._provider_health[provider_type] = True
            self._provider_latency[provider_type] = 0.0

    async def start(self) -> None:
        """启动路由器（初始化所有适配器）"""
        for provider_type, config in self.providers.items():
            try:
                adapter = AdapterFactory.create(config)
                await adapter.start()
                self._adapters[provider_type] = adapter
            except Exception as e:
                logger.warning(f"Failed to start provider {provider_type}: {e}")
                self._provider_health[provider_type] = False

    async def close(self) -> None:
        """关闭路由器（释放所有资源）"""
        for adapter in self._adapters.values():
            try:
                await adapter.close()
            except Exception:
                pass
        self._adapters.clear()

    async def __aenter__(self) -> "Router":
        """异步上下文管理器入口"""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """异步上下文管理器出口"""
        await self.close()

    # ==================== Provider 选择 ====================

    def _select_provider(
        self,
        model: str,
        capability: str | None = None,
    ) -> str:
        """
        选择合适的 Provider

        Args:
            model: 模型名称
            capability: 能力类型

        Returns:
            Provider 类型

        Raises:
            ModelNotFoundError: 无法找到合适的 Provider
        """
        # 1. 尝试通过模型名自动映射
        mapped_provider = self.MODEL_PROVIDER_MAP.get(model)
        if mapped_provider and mapped_provider in self.providers:
            return mapped_provider

        # 2. 按策略选择支持该能力的 Provider
        candidates = self._get_capable_providers(capability)
        if not candidates:
            # 3. 使用默认 Provider
            if self.default_provider and self.default_provider in self.providers:
                return self.default_provider

            raise ModelNotFoundError(
                message=f"No suitable provider found for model '{model}'",
                details={
                    "model": model,
                    "capability": capability,
                    "available_providers": list(self.providers.keys()),
                },
            )

        # 根据策略选择
        return self._pick_by_strategy(candidates)

    def _get_capable_providers(self, capability: str | None = None) -> list[str]:
        """
        获取支持指定能力的健康 Provider 列表

        Args:
            capability: 能力类型

        Returns:
            Provider 类型列表
        """
        candidates: list[str] = []

        for provider_type in self._provider_order:
            # 跳过不健康的 Provider
            if not self._provider_health.get(provider_type, True):
                continue

            adapter = self._adapters.get(provider_type)
            if adapter is None:
                continue

            if capability is None or adapter.supports_capability(capability):
                candidates.append(provider_type)

        # 如果没有健康的，返回所有可用的
        if not candidates:
            for provider_type in self._provider_order:
                adapter = self._adapters.get(provider_type)
                if adapter and (
                    capability is None or adapter.supports_capability(capability)
                ):
                    candidates.append(provider_type)

        return candidates

    def _pick_by_strategy(self, candidates: list[str]) -> str:
        """
        根据路由策略从候选列表中选一个 Provider

        Args:
            candidates: 候选 Provider 列表

        Returns:
            选中的 Provider 类型
        """
        if not candidates:
            raise ModelNotFoundError(message="No candidates available")

        if len(candidates) == 1:
            return candidates[0]

        if self.strategy == "first":
            return candidates[0]

        elif self.strategy == "round_robin":
            provider = candidates[self._current_index % len(candidates)]
            self._current_index = (self._current_index + 1) % len(candidates)
            return provider

        elif self.strategy == "random":
            return random.choice(candidates)

        elif self.strategy == "weighted":
            # 按权重随机选择
            total_weight = sum(self._weights.get(p, 1) for p in candidates)
            pick = random.uniform(0, total_weight)
            current = 0
            for provider in candidates:
                current += self._weights.get(provider, 1)
                if current >= pick:
                    return provider
            return candidates[-1]

        elif self.strategy == "latency":
            # 按延迟排序，选延迟最低的
            # 如果没有延迟数据，fallback 到 first
            with_latency = [
                p for p in candidates if self._provider_latency.get(p, 0) > 0
            ]
            if with_latency:
                return min(with_latency, key=lambda p: self._provider_latency[p])
            return candidates[0]

        else:
            return candidates[0]

    def _get_fallback_providers(
        self,
        failed_provider: str,
        capability: str | None = None,
    ) -> list[str]:
        """
        获取 Fallback Provider 列表（排除失败的那个）

        Args:
            failed_provider: 失败的 Provider
            capability: 需要的能力

        Returns:
            Fallback Provider 列表
        """
        candidates = self._get_capable_providers(capability)
        return [p for p in candidates if p != failed_provider]

    # ==================== 带 Fallback 的执行 ====================

    async def _execute_with_fallback(
        self,
        model_name: str,
        capability: str,
        method_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        带 Fallback 的执行方法

        Args:
            model_name: 模型名称
            capability: 能力类型
            method_name: 要调用的方法名
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            方法执行结果
        """
        primary = self._select_provider(model_name, capability)
        last_error: Exception | None = None

        # 主 Provider + fallback
        providers_to_try = [primary]
        if self.enable_fallback:
            providers_to_try.extend(
                self._get_fallback_providers(primary, capability)[: self.max_retries]
            )

        for i, provider_type in enumerate(providers_to_try):
            adapter = self._adapters.get(provider_type)
            if adapter is None:
                continue

            try:
                import time

                start = time.perf_counter()
                method = getattr(adapter, method_name)
                result = await method(*args, **kwargs)
                elapsed = time.perf_counter() - start

                # 更新延迟统计（滑动平均）
                old_latency = self._provider_latency.get(provider_type, 0)
                if old_latency > 0:
                    self._provider_latency[provider_type] = (
                        old_latency * 0.7 + elapsed * 0.3
                    )
                else:
                    self._provider_latency[provider_type] = elapsed

                # 标记健康
                self._provider_health[provider_type] = True

                if i > 0:
                    logger.info(f"Fallback succeeded: {primary} -> {provider_type}")

                return result

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Provider {provider_type} failed (attempt {i + 1}): {e}"
                )
                # 标记不健康
                self._provider_health[provider_type] = False

        # 所有都失败了
        raise last_error or RuntimeError("All providers failed")

    async def _get_adapter(self, provider_type: str) -> Any:
        """
        获取适配器

        Args:
            provider_type: Provider 类型

        Returns:
            适配器实例

        Raises:
            ModelNotFoundError: Provider 不存在
        """
        adapter = self._adapters.get(provider_type)
        if adapter is None:
            raise ModelNotFoundError(
                message=f"Provider '{provider_type}' is not configured",
                details={"available_providers": list(self.providers.keys())},
            )
        return adapter

    # ==================== 文本对话 ====================

    async def chat(
        self,
        model: str,
        messages: list[ChatMessage] | list[dict[str, str]],
        **kwargs: Any,
    ) -> ChatCompletion:
        """
        文本对话（带 Fallback）

        Args:
            model: 模型名称
            messages: 消息列表
            **kwargs: 其他参数

        Returns:
            对话完成结果
        """
        return cast(
            ChatCompletion,
            await self._execute_with_fallback(
                model, "chat", "chat", model=model, messages=messages, **kwargs
            ),
        )

    async def chat_stream(
        self,
        model: str,
        messages: list[ChatMessage] | list[dict[str, str]],
        **kwargs: Any,
    ) -> Any:
        """
        流式文本对话

        注意：流式对话不支持 Fallback（因为流已经开始了）

        Args:
            model: 模型名称
            messages: 消息列表
            **kwargs: 其他参数

        Yields:
            ChatCompletionChunk: 流式响应块
        """
        provider_type = self._select_provider(model, "chat")
        adapter = await self._get_adapter(provider_type)

        async for chunk in adapter.chat_stream(
            model=model, messages=messages, **kwargs
        ):
            yield chunk

    # ==================== 图像生成 ====================

    async def image_generate(
        self,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> ImageGenerationResult:
        """
        图像生成（带 Fallback）

        Args:
            model: 模型名称
            prompt: 提示词
            **kwargs: 其他参数

        Returns:
            图像生成结果
        """
        return cast(
            ImageGenerationResult,
            await self._execute_with_fallback(
                model, "image", "image_generate", model=model, prompt=prompt, **kwargs
            ),
        )

    # ==================== 视频生成 ====================

    async def video_create(
        self,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> VideoTask:
        """
        创建视频生成任务（带 Fallback）

        Args:
            model: 模型名称
            prompt: 提示词
            **kwargs: 其他参数

        Returns:
            视频任务信息
        """
        return cast(
            VideoTask,
            await self._execute_with_fallback(
                model, "video", "video_create", model=model, prompt=prompt, **kwargs
            ),
        )

    async def video_poll(
        self,
        task_id: str,
        model: str = "",
        provider_type: str | None = None,
    ) -> VideoStatus:
        """
        查询视频任务状态

        Args:
            task_id: 任务 ID
            model: 模型名称
            provider_type: 指定 Provider（可选，优先使用）

        Returns:
            视频任务状态
        """
        # 优先使用指定的 Provider
        if provider_type:
            adapter = await self._get_adapter(provider_type)
            return cast(
                VideoStatus, await adapter.video_poll(task_id=task_id, model=model)
            )

        # 根据模型名找到对应的 Provider
        if model:
            mapped = self.MODEL_PROVIDER_MAP.get(model)
            if mapped and mapped in self._adapters:
                adapter = self._adapters[mapped]
                return cast(
                    VideoStatus, await adapter.video_poll(task_id=task_id, model=model)
                )

        # 尝试所有支持 video 的 Provider
        for provider in self._get_capable_providers("video"):
            adapter = self._adapters.get(provider)
            if adapter:
                try:
                    return cast(
                        VideoStatus,
                        await adapter.video_poll(task_id=task_id, model=model),
                    )
                except Exception:
                    continue

        raise ModelNotFoundError(
            message="Cannot determine provider for video poll",
            details={"task_id": task_id, "model": model},
        )

    # ==================== 语音转文字 ====================

    async def transcribe(
        self,
        model: str,
        file: Any,
        **kwargs: Any,
    ) -> TranscriptionResult:
        """
        语音转文字（带 Fallback）

        Args:
            model: 模型名称
            file: 音频文件
            **kwargs: 其他参数

        Returns:
            转写结果
        """
        return cast(
            TranscriptionResult,
            await self._execute_with_fallback(
                model,
                "audio_transcribe",
                "transcribe",
                model=model,
                file=file,
                **kwargs,
            ),
        )

    async def translate(
        self,
        model: str,
        file: Any,
        **kwargs: Any,
    ) -> TranscriptionResult:
        """
        语音翻译（带 Fallback）

        Args:
            model: 模型名称
            file: 音频文件
            **kwargs: 其他参数

        Returns:
            翻译结果
        """
        return cast(
            TranscriptionResult,
            await self._execute_with_fallback(
                model, "audio_translate", "translate", model=model, file=file, **kwargs
            ),
        )

    # ==================== 文字转语音 ====================

    async def speech(
        self,
        model: str,
        input: str,
        voice: str,
        **kwargs: Any,
    ) -> SpeechResult:
        """
        文字转语音（带 Fallback）

        Args:
            model: 模型名称
            input: 要合成的文本
            voice: 音色
            **kwargs: 其他参数

        Returns:
            语音合成结果
        """
        return cast(
            SpeechResult,
            await self._execute_with_fallback(
                model,
                "audio_speech",
                "speech",
                model=model,
                input=input,
                voice=voice,
                **kwargs,
            ),
        )

    # ==================== 模型信息 ====================

    async def list_models(
        self,
        model_type: Literal["chat", "image", "video", "audio"] | None = None,
    ) -> list[ModelInfo]:
        """
        获取可用模型列表（聚合所有 Provider）

        Args:
            model_type: 模型类型过滤

        Returns:
            模型信息列表
        """
        all_models: list[ModelInfo] = []
        seen_ids: set[str] = set()

        for provider_type, adapter in self._adapters.items():
            if not self._provider_health.get(provider_type, True):
                continue
            models = await adapter.list_models(model_type=model_type)
            for model in models:
                if model.id not in seen_ids:
                    all_models.append(model)
                    seen_ids.add(model.id)

        return all_models

    # ==================== 健康检查 ====================

    def get_health_status(self) -> dict[str, bool]:
        """
        获取所有 Provider 的健康状态

        Returns:
            {provider_type: is_healthy}
        """
        return dict(self._provider_health)

    def get_latency_stats(self) -> dict[str, float]:
        """
        获取所有 Provider 的延迟统计

        Returns:
            {provider_type: avg_latency_seconds}
        """
        return dict(self._provider_latency)

    def register_model_mapping(self, model_name: str, provider_type: str) -> None:
        """
        注册自定义模型映射

        Args:
            model_name: 模型名称
            provider_type: Provider 类型
        """
        self.MODEL_PROVIDER_MAP[model_name] = provider_type
