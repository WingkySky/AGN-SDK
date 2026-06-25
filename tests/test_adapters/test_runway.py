"""
AGN-SDK Runway 适配器测试
"""

import pytest

from agn.adapters.runway import RunwayAdapter
from agn.models.common import ProviderConfig


class TestRunwayAdapter:
    """RunwayAdapter 类测试"""

    @pytest.fixture
    def adapter_config(self, mock_api_key: str) -> ProviderConfig:
        """创建适配器配置"""
        return ProviderConfig(
            provider_type="runway",
            api_key=mock_api_key,
        )

    @pytest.fixture
    def adapter(self, adapter_config: ProviderConfig) -> RunwayAdapter:
        """创建适配器实例"""
        return RunwayAdapter(config=adapter_config)

    def test_adapter_init(self, adapter: RunwayAdapter) -> None:
        """测试适配器初始化"""
        assert adapter.provider_type == "runway"
        assert adapter.provider_name == "Runway"
        assert "video" in adapter.supported_capabilities
        assert "chat" not in adapter.supported_capabilities
        assert "image" not in adapter.supported_capabilities

    def test_adapter_supports_capability(self, adapter: RunwayAdapter) -> None:
        """测试能力检查"""
        assert adapter.supports_capability("video")
        assert not adapter.supports_capability("chat")
        assert not adapter.supports_capability("image")

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: RunwayAdapter) -> None:
        """测试异步上下文管理器"""
        async with adapter as a:
            assert a._http_client is not None

    @pytest.mark.asyncio
    async def test_chat_not_supported(self, adapter: RunwayAdapter) -> None:
        """测试文本对话不支持"""
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.chat(
                model="test",
                messages=[{"role": "user", "content": "Hello"}],
            )

    @pytest.mark.asyncio
    async def test_image_generate_not_supported(self, adapter: RunwayAdapter) -> None:
        """测试图像生成不支持"""
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.image_generate(
                model="test",
                prompt="A cat",
            )


class TestRunwayAdapterListModels:
    """RunwayAdapter 模型列表测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> RunwayAdapter:
        """创建适配器实例"""
        config = ProviderConfig(provider_type="runway", api_key=mock_api_key)
        return RunwayAdapter(config=config)

    @pytest.mark.asyncio
    async def test_list_all_models(self, adapter: RunwayAdapter) -> None:
        """测试获取所有模型"""
        models = await adapter.list_models()
        assert len(models) > 0

        types = {m.type for m in models}
        assert "video" in types
        assert "chat" not in types
        assert "image" not in types

    @pytest.mark.asyncio
    async def test_list_video_models(self, adapter: RunwayAdapter) -> None:
        """测试获取视频模型"""
        models = await adapter.list_models(model_type="video")
        assert len(models) > 0
        for model in models:
            assert model.type == "video"

    @pytest.mark.asyncio
    async def test_list_chat_models_empty(self, adapter: RunwayAdapter) -> None:
        """测试获取对话模型（空列表）"""
        models = await adapter.list_models(model_type="chat")
        assert len(models) == 0


class TestRunwayAdapterStatusMapping:
    """RunwayAdapter 状态映射测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> RunwayAdapter:
        """创建适配器实例"""
        config = ProviderConfig(provider_type="runway", api_key=mock_api_key)
        return RunwayAdapter(config=config)

    def test_map_pending_status(self, adapter: RunwayAdapter) -> None:
        """测试 pending 状态映射"""
        assert adapter._map_runway_status("pending") == "pending"
        assert adapter._map_runway_status("queued") == "pending"

    def test_map_processing_status(self, adapter: RunwayAdapter) -> None:
        """测试 processing 状态映射"""
        assert adapter._map_runway_status("processing") == "processing"
        assert adapter._map_runway_status("running") == "processing"
        assert adapter._map_runway_status("in_progress") == "processing"

    def test_map_success_status(self, adapter: RunwayAdapter) -> None:
        """测试 success 状态映射"""
        assert adapter._map_runway_status("completed") == "success"
        assert adapter._map_runway_status("succeeded") == "success"
        assert adapter._map_runway_status("success") == "success"

    def test_map_failed_status(self, adapter: RunwayAdapter) -> None:
        """测试 failed 状态映射"""
        assert adapter._map_runway_status("failed") == "failed"
        assert adapter._map_runway_status("error") == "failed"
        assert adapter._map_runway_status("cancelled") == "failed"

    def test_map_unknown_status(self, adapter: RunwayAdapter) -> None:
        """测试未知状态映射"""
        assert adapter._map_runway_status("unknown_status") == "pending"
