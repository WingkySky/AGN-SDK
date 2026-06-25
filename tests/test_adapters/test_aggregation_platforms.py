"""
AGN-SDK 聚合平台适配器测试 (SiliconFlow/Together AI/Fireworks AI/Cloudflare)
"""

import pytest

from agn.adapters.aggregation_platforms import (
    SiliconFlowAdapter,
    TogetherAIAdapter,
    FireworksAIAdapter,
    CloudflareAIAdapter,
)
from agn.models.common import ProviderConfig


class TestSiliconFlowAdapter:
    """SiliconFlowAdapter (硅基流动) 类测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> SiliconFlowAdapter:
        config = ProviderConfig(provider_type="siliconflow", api_key=mock_api_key)
        return SiliconFlowAdapter(config=config)

    def test_adapter_init(self, adapter: SiliconFlowAdapter) -> None:
        assert adapter.provider_type == "siliconflow"
        assert "硅基流动" in adapter.provider_name
        assert "chat" in adapter.supported_capabilities

    def test_adapter_supports_capability(self, adapter: SiliconFlowAdapter) -> None:
        assert adapter.supports_capability("chat")
        assert adapter.supports_capability("vision")
        assert not adapter.supports_capability("video")

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: SiliconFlowAdapter) -> None:
        async with adapter as a:
            assert a._http_client is not None
            assert "siliconflow.cn" in str(a._http_client.base_url)

    @pytest.mark.asyncio
    async def test_video_not_supported(self, adapter: SiliconFlowAdapter) -> None:
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.video_create(model="test", prompt="A cat")

    @pytest.mark.asyncio
    async def test_list_all_models(self, adapter: SiliconFlowAdapter) -> None:
        models = await adapter.list_models()
        assert len(models) >= 9
        model_ids = {m.id for m in models}
        assert "Pro/zai-org/GLM-4.7" in model_ids
        assert "deepseek-ai/DeepSeek-V3.2" in model_ids
        assert "Qwen/Qwen3-8B" in model_ids


class TestTogetherAIAdapter:
    """TogetherAIAdapter 类测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> TogetherAIAdapter:
        config = ProviderConfig(provider_type="togetherai", api_key=mock_api_key)
        return TogetherAIAdapter(config=config)

    def test_adapter_init(self, adapter: TogetherAIAdapter) -> None:
        assert adapter.provider_type == "togetherai"
        assert adapter.provider_name == "Together AI"
        assert "chat" in adapter.supported_capabilities

    def test_adapter_supports_capability(self, adapter: TogetherAIAdapter) -> None:
        assert adapter.supports_capability("chat")
        assert not adapter.supports_capability("video")

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: TogetherAIAdapter) -> None:
        async with adapter as a:
            assert a._http_client is not None
            assert "together.xyz" in str(a._http_client.base_url)

    @pytest.mark.asyncio
    async def test_video_not_supported(self, adapter: TogetherAIAdapter) -> None:
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.video_create(model="test", prompt="A cat")

    @pytest.mark.asyncio
    async def test_list_all_models(self, adapter: TogetherAIAdapter) -> None:
        models = await adapter.list_models()
        assert len(models) >= 10
        model_ids = {m.id for m in models}
        assert "meta-llama/Llama-3-70b-chat-hf" in model_ids
        assert "Qwen/Qwen2.5-72B-Instruct-Turbo" in model_ids
        assert "deepseek-ai/DeepSeek-V3" in model_ids

    @pytest.mark.asyncio
    async def test_list_chat_models(self, adapter: TogetherAIAdapter) -> None:
        models = await adapter.list_models(model_type="chat")
        assert len(models) >= 10
        for model in models:
            assert model.type == "chat"


class TestFireworksAIAdapter:
    """FireworksAIAdapter 类测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> FireworksAIAdapter:
        config = ProviderConfig(provider_type="fireworksai", api_key=mock_api_key)
        return FireworksAIAdapter(config=config)

    def test_adapter_init(self, adapter: FireworksAIAdapter) -> None:
        assert adapter.provider_type == "fireworksai"
        assert adapter.provider_name == "Fireworks AI"
        assert "chat" in adapter.supported_capabilities

    def test_adapter_supports_capability(self, adapter: FireworksAIAdapter) -> None:
        assert adapter.supports_capability("chat")
        assert not adapter.supports_capability("video")

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: FireworksAIAdapter) -> None:
        async with adapter as a:
            assert a._http_client is not None
            assert "fireworks.ai" in str(a._http_client.base_url)

    @pytest.mark.asyncio
    async def test_video_not_supported(self, adapter: FireworksAIAdapter) -> None:
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.video_create(model="test", prompt="A cat")

    @pytest.mark.asyncio
    async def test_list_all_models(self, adapter: FireworksAIAdapter) -> None:
        models = await adapter.list_models()
        assert len(models) >= 9
        model_ids = {m.id for m in models}
        assert "accounts/fireworks/models/llama-v3p1-405b-instruct" in model_ids
        assert "accounts/fireworks/models/mixtral-8x22b-instruct" in model_ids
        assert "accounts/fireworks/models/deepseek-v3" in model_ids


class TestCloudflareAIAdapter:
    """CloudflareAIAdapter (Workers AI) 类测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> CloudflareAIAdapter:
        config = ProviderConfig(
            provider_type="cloudflareai",
            api_key=mock_api_key,
            extra={"account_id": "test-account-id"},
        )
        return CloudflareAIAdapter(config=config)

    def test_adapter_init(self, adapter: CloudflareAIAdapter) -> None:
        assert adapter.provider_type == "cloudflareai"
        assert adapter.provider_name == "Cloudflare Workers AI"
        assert "chat" in adapter.supported_capabilities

    def test_adapter_supports_capability(self, adapter: CloudflareAIAdapter) -> None:
        assert adapter.supports_capability("chat")
        assert not adapter.supports_capability("video")

    def test_format_model(self, adapter: CloudflareAIAdapter) -> None:
        """测试模型名称格式化"""
        assert adapter._format_model("@cf/llama-3.1-8b") == "@cf/llama-3.1-8b"
        assert adapter._format_model("llama-3.1-8b") == "@cf/llama-3.1-8b"

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: CloudflareAIAdapter) -> None:
        async with adapter as a:
            assert a._http_client is not None
            assert "cloudflare.com" in str(a._http_client.base_url)
            assert "test-account-id" in str(a._http_client.base_url)

    @pytest.mark.asyncio
    async def test_video_not_supported(self, adapter: CloudflareAIAdapter) -> None:
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.video_create(model="test", prompt="A cat")

    @pytest.mark.asyncio
    async def test_list_all_models(self, adapter: CloudflareAIAdapter) -> None:
        models = await adapter.list_models()
        assert len(models) >= 9
        model_ids = {m.id for m in models}
        assert "@cf/meta/llama-3.1-8b-instruct" in model_ids
        assert "@cf/meta/llama-3.1-70b-instruct" in model_ids
        assert "@cf/mistral/mistral-7b-instruct-v0.2" in model_ids
