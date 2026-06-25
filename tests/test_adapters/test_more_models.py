"""
AGN-SDK 更多模型适配器测试 (DeepSeek/StepFun/Mistral/Cohere/Perplexity)
"""

import pytest

from agn.adapters.more_models import (
    DeepSeekAdapter,
    StepFunAdapter,
    MistralAdapter,
    CohereAdapter,
    PerplexityAdapter,
)
from agn.models.common import ProviderConfig


class TestDeepSeekAdapter:
    """DeepSeekAdapter 类测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> DeepSeekAdapter:
        config = ProviderConfig(provider_type="deepseek", api_key=mock_api_key)
        return DeepSeekAdapter(config=config)

    def test_adapter_init(self, adapter: DeepSeekAdapter) -> None:
        assert adapter.provider_type == "deepseek"
        assert adapter.provider_name == "DeepSeek"
        assert "chat" in adapter.supported_capabilities

    def test_adapter_supports_capability(self, adapter: DeepSeekAdapter) -> None:
        assert adapter.supports_capability("chat")
        assert adapter.supports_capability("vision")
        assert not adapter.supports_capability("video")

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: DeepSeekAdapter) -> None:
        async with adapter as a:
            assert a._http_client is not None
            assert "api.deepseek.com" in str(a._http_client.base_url)

    @pytest.mark.asyncio
    async def test_video_not_supported(self, adapter: DeepSeekAdapter) -> None:
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.video_create(model="test", prompt="A cat")

    @pytest.mark.asyncio
    async def test_list_all_models(self, adapter: DeepSeekAdapter) -> None:
        models = await adapter.list_models()
        assert len(models) >= 5
        model_ids = {m.id for m in models}
        assert "deepseek-v4-pro" in model_ids
        assert "deepseek-v4-flash" in model_ids
        assert "deepseek-coder" in model_ids

    @pytest.mark.asyncio
    async def test_list_chat_models(self, adapter: DeepSeekAdapter) -> None:
        models = await adapter.list_models(model_type="chat")
        assert len(models) >= 5
        for model in models:
            assert model.type == "chat"


class TestStepFunAdapter:
    """StepFunAdapter (阶跃星辰) 类测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> StepFunAdapter:
        config = ProviderConfig(provider_type="stepfun", api_key=mock_api_key)
        return StepFunAdapter(config=config)

    def test_adapter_init(self, adapter: StepFunAdapter) -> None:
        assert adapter.provider_type == "stepfun"
        assert adapter.provider_name == "阶跃星辰 StepFun"
        assert "chat" in adapter.supported_capabilities

    def test_adapter_supports_capability(self, adapter: StepFunAdapter) -> None:
        assert adapter.supports_capability("chat")
        assert adapter.supports_capability("vision")
        assert not adapter.supports_capability("video")

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: StepFunAdapter) -> None:
        async with adapter as a:
            assert a._http_client is not None
            assert "stepfun.com" in str(a._http_client.base_url)

    @pytest.mark.asyncio
    async def test_video_not_supported(self, adapter: StepFunAdapter) -> None:
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.video_create(model="test", prompt="A cat")

    @pytest.mark.asyncio
    async def test_list_all_models(self, adapter: StepFunAdapter) -> None:
        models = await adapter.list_models()
        assert len(models) >= 7
        model_ids = {m.id for m in models}
        assert "step-3-flash" in model_ids
        assert "step-3-128k" in model_ids
        assert "step-1o-turbo" in model_ids


class TestMistralAdapter:
    """MistralAdapter 类测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> MistralAdapter:
        config = ProviderConfig(provider_type="mistral", api_key=mock_api_key)
        return MistralAdapter(config=config)

    def test_adapter_init(self, adapter: MistralAdapter) -> None:
        assert adapter.provider_type == "mistral"
        assert adapter.provider_name == "Mistral AI"
        assert "chat" in adapter.supported_capabilities

    def test_adapter_supports_capability(self, adapter: MistralAdapter) -> None:
        assert adapter.supports_capability("chat")
        assert not adapter.supports_capability("video")

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: MistralAdapter) -> None:
        async with adapter as a:
            assert a._http_client is not None
            assert "api.mistral.ai" in str(a._http_client.base_url)

    @pytest.mark.asyncio
    async def test_video_not_supported(self, adapter: MistralAdapter) -> None:
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.video_create(model="test", prompt="A cat")

    @pytest.mark.asyncio
    async def test_list_all_models(self, adapter: MistralAdapter) -> None:
        models = await adapter.list_models()
        assert len(models) >= 7
        model_ids = {m.id for m in models}
        assert "mistral-sonnet-4-2505" in model_ids
        assert "mixtral-8x22b-2404" in model_ids
        assert "codestral-2405" in model_ids

    @pytest.mark.asyncio
    async def test_list_chat_models(self, adapter: MistralAdapter) -> None:
        models = await adapter.list_models(model_type="chat")
        assert len(models) >= 7
        for model in models:
            assert model.type == "chat"


class TestCohereAdapter:
    """CohereAdapter 类测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> CohereAdapter:
        config = ProviderConfig(provider_type="cohere", api_key=mock_api_key)
        return CohereAdapter(config=config)

    def test_adapter_init(self, adapter: CohereAdapter) -> None:
        assert adapter.provider_type == "cohere"
        assert adapter.provider_name == "Cohere"
        assert "chat" in adapter.supported_capabilities

    def test_adapter_supports_capability(self, adapter: CohereAdapter) -> None:
        assert adapter.supports_capability("chat")
        assert not adapter.supports_capability("video")

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: CohereAdapter) -> None:
        async with adapter as a:
            assert a._http_client is not None
            assert "api.cohere.ai" in str(a._http_client.base_url)

    @pytest.mark.asyncio
    async def test_video_not_supported(self, adapter: CohereAdapter) -> None:
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.video_create(model="test", prompt="A cat")

    def test_message_conversion_system(self, adapter: CohereAdapter) -> None:
        """测试消息格式转换 - system 消息被提取到 system_prompt"""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        converted, system = adapter._convert_messages(messages)
        assert system == "You are a helpful assistant."
        # system 消息被提取到 system_prompt，不计入 converted
        assert len(converted) == 2
        # role 被转换为 Cohere 格式
        assert converted[0]["role"] == "USER"
        assert converted[0]["content"] == "Hello"
        assert converted[1]["role"] == "CHATBOT"
        assert converted[1]["content"] == "Hi there!"

    @pytest.mark.asyncio
    async def test_list_all_models(self, adapter: CohereAdapter) -> None:
        models = await adapter.list_models()
        assert len(models) >= 6
        model_ids = {m.id for m in models}
        assert "command-r-plus-08-2024" in model_ids
        assert "command-r-08-2024" in model_ids
        assert "c4ai-aya-23-35b" in model_ids


class TestPerplexityAdapter:
    """PerplexityAdapter 类测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> PerplexityAdapter:
        config = ProviderConfig(provider_type="perplexity", api_key=mock_api_key)
        return PerplexityAdapter(config=config)

    def test_adapter_init(self, adapter: PerplexityAdapter) -> None:
        assert adapter.provider_type == "perplexity"
        assert adapter.provider_name == "Perplexity AI"
        assert "chat" in adapter.supported_capabilities

    def test_adapter_supports_capability(self, adapter: PerplexityAdapter) -> None:
        assert adapter.supports_capability("chat")
        assert not adapter.supports_capability("video")

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: PerplexityAdapter) -> None:
        async with adapter as a:
            assert a._http_client is not None
            assert "api.perplexity.ai" in str(a._http_client.base_url)

    @pytest.mark.asyncio
    async def test_video_not_supported(self, adapter: PerplexityAdapter) -> None:
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.video_create(model="test", prompt="A cat")

    @pytest.mark.asyncio
    async def test_list_all_models(self, adapter: PerplexityAdapter) -> None:
        models = await adapter.list_models()
        assert len(models) >= 8
        model_ids = {m.id for m in models}
        assert "sonar-pro" in model_ids
        assert "sonar" in model_ids
        assert "sonar-reasoning" in model_ids
        assert "llama-3.1-sonar-huge-128k-online" in model_ids
