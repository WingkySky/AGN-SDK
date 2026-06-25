"""
AGN-SDK OpenAI 适配器测试
"""

import pytest

from agn.adapters.openai import OpenAIAdapter
from agn.models.common import ProviderConfig


class TestOpenAIAdapter:
    """OpenAIAdapter 类测试"""

    @pytest.fixture
    def adapter_config(self, mock_api_key: str) -> ProviderConfig:
        """创建适配器配置"""
        return ProviderConfig(
            provider_type="openai",
            api_key=mock_api_key,
        )

    @pytest.fixture
    def adapter(self, adapter_config: ProviderConfig) -> OpenAIAdapter:
        """创建适配器实例"""
        return OpenAIAdapter(config=adapter_config)

    def test_adapter_init(self, adapter: OpenAIAdapter, mock_api_key: str) -> None:
        """测试适配器初始化"""
        assert adapter.provider_type == "openai"
        assert adapter.provider_name == "OpenAI"
        assert "chat" in adapter.supported_capabilities
        assert "image" in adapter.supported_capabilities
        assert "video" not in adapter.supported_capabilities
        assert adapter.api_key == mock_api_key

    def test_adapter_supports_capability(self, adapter: OpenAIAdapter) -> None:
        """测试能力检查"""
        assert adapter.supports_capability("chat")
        assert adapter.supports_capability("image")
        assert not adapter.supports_capability("video")

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: OpenAIAdapter) -> None:
        """测试异步上下文管理器"""
        async with adapter as a:
            assert a._http_client is not None


class TestOpenAIAdapterListModels:
    """OpenAIAdapter 模型列表测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> OpenAIAdapter:
        """创建适配器实例"""
        config = ProviderConfig(provider_type="openai", api_key=mock_api_key)
        return OpenAIAdapter(config=config)

    @pytest.mark.asyncio
    async def test_list_all_models(self, adapter: OpenAIAdapter) -> None:
        """测试获取所有模型"""
        models = await adapter.list_models()
        assert len(models) > 0

        types = {m.type for m in models}
        assert "chat" in types
        assert "image" in types

    @pytest.mark.asyncio
    async def test_list_chat_models(self, adapter: OpenAIAdapter) -> None:
        """测试获取对话模型"""
        models = await adapter.list_models(model_type="chat")
        for model in models:
            assert model.type == "chat"

    @pytest.mark.asyncio
    async def test_list_image_models(self, adapter: OpenAIAdapter) -> None:
        """测试获取图像模型"""
        models = await adapter.list_models(model_type="image")
        for model in models:
            assert model.type == "image"

    @pytest.mark.asyncio
    async def test_video_not_supported(self, adapter: OpenAIAdapter) -> None:
        """测试视频生成不支持"""
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.video_create(
                model="test",
                prompt="A video",
            )
