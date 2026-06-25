"""
AGN-SDK 额外模型适配器测试 (Grok/Yi/SenseNova/Hunyuan/Groq)
"""

import pytest

from agn.adapters.additional_models import (
    GrokAdapter,
    YiAdapter,
    SenseNovaAdapter,
    HunyuanAdapter,
    GroqAdapter,
)
from agn.models.common import ProviderConfig


class TestGrokAdapter:
    """GrokAdapter (xAI) 类测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> GrokAdapter:
        config = ProviderConfig(provider_type="grok", api_key=mock_api_key)
        return GrokAdapter(config=config)

    def test_adapter_init(self, adapter: GrokAdapter) -> None:
        assert adapter.provider_type == "grok"
        assert adapter.provider_name == "xAI Grok"
        assert "chat" in adapter.supported_capabilities
        assert "vision" in adapter.supported_capabilities

    def test_adapter_supports_capability(self, adapter: GrokAdapter) -> None:
        assert adapter.supports_capability("chat")
        assert adapter.supports_capability("vision")
        assert not adapter.supports_capability("video")

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: GrokAdapter) -> None:
        async with adapter as a:
            assert a._http_client is not None
            assert "api.x.ai" in str(a._http_client.base_url)

    @pytest.mark.asyncio
    async def test_video_not_supported(self, adapter: GrokAdapter) -> None:
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.video_create(model="test", prompt="A cat")

    @pytest.mark.asyncio
    async def test_list_all_models(self, adapter: GrokAdapter) -> None:
        models = await adapter.list_models()
        assert len(models) >= 5
        model_ids = {m.id for m in models}
        assert "grok-3" in model_ids
        assert "grok-3-latest" in model_ids
        assert "grok-2" in model_ids


class TestYiAdapter:
    """YiAdapter (零一万物) 类测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> YiAdapter:
        config = ProviderConfig(provider_type="yi", api_key=mock_api_key)
        return YiAdapter(config=config)

    def test_adapter_init(self, adapter: YiAdapter) -> None:
        assert adapter.provider_type == "yi"
        assert adapter.provider_name == "零一万物 Yi"
        assert "chat" in adapter.supported_capabilities

    def test_adapter_supports_capability(self, adapter: YiAdapter) -> None:
        assert adapter.supports_capability("chat")
        assert adapter.supports_capability("vision")
        assert not adapter.supports_capability("video")

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: YiAdapter) -> None:
        async with adapter as a:
            assert a._http_client is not None
            assert "lingyiwanwu.com" in str(a._http_client.base_url)

    @pytest.mark.asyncio
    async def test_video_not_supported(self, adapter: YiAdapter) -> None:
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.video_create(model="test", prompt="A cat")

    @pytest.mark.asyncio
    async def test_list_all_models(self, adapter: YiAdapter) -> None:
        models = await adapter.list_models()
        assert len(models) >= 7
        model_ids = {m.id for m in models}
        assert "yi-large" in model_ids
        assert "yi-34b-chat-200k" in model_ids
        assert "yi-vl-plus" in model_ids

    @pytest.mark.asyncio
    async def test_list_chat_models(self, adapter: YiAdapter) -> None:
        models = await adapter.list_models(model_type="chat")
        assert len(models) >= 7
        for model in models:
            assert model.type == "chat"


class TestSenseNovaAdapter:
    """SenseNovaAdapter (商汤日日新) 类测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> SenseNovaAdapter:
        config = ProviderConfig(provider_type="sensenova", api_key=mock_api_key)
        return SenseNovaAdapter(config=config)

    def test_adapter_init(self, adapter: SenseNovaAdapter) -> None:
        assert adapter.provider_type == "sensenova"
        assert "日日新" in adapter.provider_name
        assert "chat" in adapter.supported_capabilities

    def test_adapter_supports_capability(self, adapter: SenseNovaAdapter) -> None:
        assert adapter.supports_capability("chat")
        assert not adapter.supports_capability("video")

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: SenseNovaAdapter) -> None:
        async with adapter as a:
            assert a._http_client is not None
            assert "sensenova.cn" in str(a._http_client.base_url)

    @pytest.mark.asyncio
    async def test_video_not_supported(self, adapter: SenseNovaAdapter) -> None:
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.video_create(model="test", prompt="A cat")

    @pytest.mark.asyncio
    async def test_list_all_models(self, adapter: SenseNovaAdapter) -> None:
        models = await adapter.list_models()
        assert len(models) >= 7
        model_ids = {m.id for m in models}
        assert "sensechat" in model_ids
        assert "sensechat-5" in model_ids
        assert "sensenova-llm-v3" in model_ids


class TestHunyuanAdapter:
    """HunyuanAdapter (腾讯混元) 类测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> HunyuanAdapter:
        config = ProviderConfig(provider_type="hunyuan", api_key=mock_api_key)
        return HunyuanAdapter(config=config)

    def test_adapter_init(self, adapter: HunyuanAdapter) -> None:
        assert adapter.provider_type == "hunyuan"
        assert "混元" in adapter.provider_name
        assert "chat" in adapter.supported_capabilities

    def test_adapter_supports_capability(self, adapter: HunyuanAdapter) -> None:
        assert adapter.supports_capability("chat")
        assert adapter.supports_capability("vision")
        assert not adapter.supports_capability("video")

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: HunyuanAdapter) -> None:
        async with adapter as a:
            assert a._http_client is not None
            assert "tencentcloudapi.com" in str(a._http_client.base_url)

    @pytest.mark.asyncio
    async def test_video_not_supported(self, adapter: HunyuanAdapter) -> None:
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.video_create(model="test", prompt="A cat")

    @pytest.mark.asyncio
    async def test_list_all_models(self, adapter: HunyuanAdapter) -> None:
        models = await adapter.list_models()
        assert len(models) >= 7
        model_ids = {m.id for m in models}
        assert "hunyuan-turbo" in model_ids
        assert "hunyuan-lite" in model_ids
        assert "hunyuan-vision" in model_ids

    @pytest.mark.asyncio
    async def test_list_chat_models(self, adapter: HunyuanAdapter) -> None:
        models = await adapter.list_models(model_type="chat")
        assert len(models) >= 7
        for model in models:
            assert model.type == "chat"


class TestGroqAdapter:
    """GroqAdapter 类测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> GroqAdapter:
        config = ProviderConfig(provider_type="groq", api_key=mock_api_key)
        return GroqAdapter(config=config)

    def test_adapter_init(self, adapter: GroqAdapter) -> None:
        assert adapter.provider_type == "groq"
        assert adapter.provider_name == "Groq"
        assert "chat" in adapter.supported_capabilities

    def test_adapter_supports_capability(self, adapter: GroqAdapter) -> None:
        assert adapter.supports_capability("chat")
        assert not adapter.supports_capability("video")

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: GroqAdapter) -> None:
        async with adapter as a:
            assert a._http_client is not None
            assert "api.groq.com" in str(a._http_client.base_url)

    @pytest.mark.asyncio
    async def test_video_not_supported(self, adapter: GroqAdapter) -> None:
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.video_create(model="test", prompt="A cat")

    @pytest.mark.asyncio
    async def test_list_all_models(self, adapter: GroqAdapter) -> None:
        models = await adapter.list_models()
        assert len(models) >= 8
        model_ids = {m.id for m in models}
        assert "llama-3.3-70b-versatile" in model_ids
        assert "llama3-70b-8192" in model_ids
        assert "mixtral-8x7b-32768" in model_ids
        assert "gemma2-9b-it" in model_ids

    @pytest.mark.asyncio
    async def test_list_chat_models(self, adapter: GroqAdapter) -> None:
        models = await adapter.list_models(model_type="chat")
        assert len(models) >= 8
        for model in models:
            assert model.type == "chat"
