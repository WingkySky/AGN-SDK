"""
AGN-SDK Stability AI 适配器测试
"""

import pytest

from agn.adapters.stability import StabilityAdapter
from agn.models.common import ProviderConfig


class TestStabilityAdapter:
    """StabilityAdapter 类测试"""

    @pytest.fixture
    def adapter_config(self, mock_api_key: str) -> ProviderConfig:
        """创建适配器配置"""
        return ProviderConfig(
            provider_type="stability",
            api_key=mock_api_key,
        )

    @pytest.fixture
    def adapter(self, adapter_config: ProviderConfig) -> StabilityAdapter:
        """创建适配器实例"""
        return StabilityAdapter(config=adapter_config)

    def test_adapter_init(self, adapter: StabilityAdapter) -> None:
        """测试适配器初始化"""
        assert adapter.provider_type == "stability"
        assert adapter.provider_name == "Stability AI"
        assert "image" in adapter.supported_capabilities
        assert "chat" not in adapter.supported_capabilities
        assert "video" not in adapter.supported_capabilities

    def test_adapter_supports_capability(self, adapter: StabilityAdapter) -> None:
        """测试能力检查"""
        assert adapter.supports_capability("image")
        assert not adapter.supports_capability("chat")
        assert not adapter.supports_capability("video")

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: StabilityAdapter) -> None:
        """测试异步上下文管理器"""
        async with adapter as a:
            assert a._http_client is not None

    @pytest.mark.asyncio
    async def test_chat_not_supported(self, adapter: StabilityAdapter) -> None:
        """测试文本对话不支持"""
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.chat(
                model="test",
                messages=[{"role": "user", "content": "Hello"}],
            )

    @pytest.mark.asyncio
    async def test_video_not_supported(self, adapter: StabilityAdapter) -> None:
        """测试视频生成不支持"""
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.video_create(
                model="test",
                prompt="A cat",
            )


class TestStabilityAdapterListModels:
    """StabilityAdapter 模型列表测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> StabilityAdapter:
        """创建适配器实例"""
        config = ProviderConfig(provider_type="stability", api_key=mock_api_key)
        return StabilityAdapter(config=config)

    @pytest.mark.asyncio
    async def test_list_all_models(self, adapter: StabilityAdapter) -> None:
        """测试获取所有模型"""
        models = await adapter.list_models()
        assert len(models) > 0

        types = {m.type for m in models}
        assert "image" in types
        assert "chat" not in types
        assert "video" not in types

    @pytest.mark.asyncio
    async def test_list_image_models(self, adapter: StabilityAdapter) -> None:
        """测试获取图像模型"""
        models = await adapter.list_models(model_type="image")
        assert len(models) > 0
        for model in models:
            assert model.type == "image"

    @pytest.mark.asyncio
    async def test_model_capabilities(self, adapter: StabilityAdapter) -> None:
        """测试模型能力"""
        models = await adapter.list_models(model_type="image")
        for model in models:
            assert "text2image" in model.capabilities or "image2image" in model.capabilities


class TestStabilityAdapterStatusMapping:
    """StabilityAdapter 状态映射测试（图像生成无异步状态）"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> StabilityAdapter:
        """创建适配器实例"""
        config = ProviderConfig(provider_type="stability", api_key=mock_api_key)
        return StabilityAdapter(config=config)

    def test_adapter_has_default_engine(self, mock_api_key: str) -> None:
        """测试默认引擎配置"""
        config = ProviderConfig(provider_type="stability", api_key=mock_api_key)
        adapter = StabilityAdapter(config=config)
        assert adapter.default_engine == "stable-diffusion-xl-1024-v1-1"

    def test_adapter_custom_engine(self, mock_api_key: str) -> None:
        """测试自定义引擎配置"""
        config = ProviderConfig(provider_type="stability", api_key=mock_api_key)
        adapter = StabilityAdapter(config=config, default_engine="stable-diffusion-3-medium")
        assert adapter.default_engine == "stable-diffusion-3-medium"
