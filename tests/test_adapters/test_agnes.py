"""
AGN-SDK Agnes 适配器测试
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agn.adapters.agnes import AgnesAdapter
from agn.models.chat import ChatMessage
from agn.models.common import ProviderConfig


class TestAgnesAdapter:
    """AgnesAdapter 类测试"""

    @pytest.fixture
    def adapter_config(self, mock_api_key: str) -> ProviderConfig:
        """创建适配器配置"""
        return ProviderConfig(
            provider_type="agnes",
            api_key=mock_api_key,
            base_url="https://api.test.agnes.ai/v1",
        )

    @pytest.fixture
    def adapter(self, adapter_config: ProviderConfig) -> AgnesAdapter:
        """创建适配器实例"""
        return AgnesAdapter(config=adapter_config)

    def test_adapter_init(self, adapter: AgnesAdapter, mock_api_key: str) -> None:
        """测试适配器初始化"""
        assert adapter.provider_type == "agnes"
        assert adapter.provider_name == "Agnes AI"
        assert "chat" in adapter.supported_capabilities
        assert "image" in adapter.supported_capabilities
        assert "video" in adapter.supported_capabilities
        assert adapter.api_key == mock_api_key

    def test_adapter_supports_capability(self, adapter: AgnesAdapter) -> None:
        """测试能力检查"""
        assert adapter.supports_capability("chat")
        assert adapter.supports_capability("image")
        assert adapter.supports_capability("video")
        assert not adapter.supports_capability("audio")

    def test_adapter_supports_model_type(self, adapter: AgnesAdapter) -> None:
        """测试模型类型检查"""
        assert adapter.supports_model_type("chat")
        assert adapter.supports_model_type("image")
        assert adapter.supports_model_type("video")

    @pytest.mark.asyncio
    async def test_adapter_start(self, adapter: AgnesAdapter) -> None:
        """测试适配器启动"""
        await adapter.start()
        assert adapter._http_client is not None
        await adapter.close()

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: AgnesAdapter) -> None:
        """测试异步上下文管理器"""
        async with adapter as a:
            assert a._http_client is not None


class TestAgnesAdapterListModels:
    """AgnesAdapter 模型列表测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> AgnesAdapter:
        """创建适配器实例"""
        config = ProviderConfig(
            provider_type="agnes",
            api_key=mock_api_key,
        )
        return AgnesAdapter(config=config)

    @pytest.mark.asyncio
    async def test_list_all_models(self, adapter: AgnesAdapter) -> None:
        """测试获取所有模型"""
        models = await adapter.list_models()
        assert len(models) > 0

        # 检查模型类型覆盖
        types = {m.type for m in models}
        assert "chat" in types
        assert "image" in types
        assert "video" in types

    @pytest.mark.asyncio
    async def test_list_chat_models(self, adapter: AgnesAdapter) -> None:
        """测试获取对话模型"""
        models = await adapter.list_models(model_type="chat")
        for model in models:
            assert model.type == "chat"

    @pytest.mark.asyncio
    async def test_list_image_models(self, adapter: AgnesAdapter) -> None:
        """测试获取图像模型"""
        models = await adapter.list_models(model_type="image")
        for model in models:
            assert model.type == "image"

    @pytest.mark.asyncio
    async def test_list_video_models(self, adapter: AgnesAdapter) -> None:
        """测试获取视频模型"""
        models = await adapter.list_models(model_type="video")
        for model in models:
            assert model.type == "video"
