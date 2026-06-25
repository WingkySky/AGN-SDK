"""
AGN-SDK Pika 适配器测试
"""

import pytest

from agn.adapters.pika import PikaAdapter
from agn.models.common import ProviderConfig


class TestPikaAdapter:
    """PikaAdapter 类测试"""

    @pytest.fixture
    def adapter_config(self, mock_api_key: str) -> ProviderConfig:
        """创建适配器配置"""
        return ProviderConfig(
            provider_type="pika",
            api_key=mock_api_key,
        )

    @pytest.fixture
    def adapter(self, adapter_config: ProviderConfig) -> PikaAdapter:
        """创建适配器实例"""
        return PikaAdapter(config=adapter_config)

    def test_adapter_init(self, adapter: PikaAdapter) -> None:
        """测试适配器初始化"""
        assert adapter.provider_type == "pika"
        assert adapter.provider_name == "Pika"
        assert "video" in adapter.supported_capabilities
        assert "chat" not in adapter.supported_capabilities
        assert "image" not in adapter.supported_capabilities

    def test_adapter_supports_capability(self, adapter: PikaAdapter) -> None:
        """测试能力检查"""
        assert adapter.supports_capability("video")
        assert not adapter.supports_capability("chat")
        assert not adapter.supports_capability("image")

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: PikaAdapter) -> None:
        """测试异步上下文管理器"""
        async with adapter as a:
            assert a._http_client is not None

    @pytest.mark.asyncio
    async def test_chat_not_supported(self, adapter: PikaAdapter) -> None:
        """测试文本对话不支持"""
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.chat(
                model="test",
                messages=[{"role": "user", "content": "Hello"}],
            )

    @pytest.mark.asyncio
    async def test_image_generate_not_supported(self, adapter: PikaAdapter) -> None:
        """测试图像生成不支持"""
        from agn.core.errors import UnsupportedCapabilityError

        with pytest.raises(UnsupportedCapabilityError):
            await adapter.image_generate(
                model="test",
                prompt="A cat",
            )


class TestPikaAdapterListModels:
    """PikaAdapter 模型列表测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> PikaAdapter:
        """创建适配器实例"""
        config = ProviderConfig(provider_type="pika", api_key=mock_api_key)
        return PikaAdapter(config=config)

    @pytest.mark.asyncio
    async def test_list_all_models(self, adapter: PikaAdapter) -> None:
        """测试获取所有模型"""
        models = await adapter.list_models()
        assert len(models) > 0

        types = {m.type for m in models}
        assert "video" in types
        assert "chat" not in types
        assert "image" not in types

    @pytest.mark.asyncio
    async def test_list_video_models(self, adapter: PikaAdapter) -> None:
        """测试获取视频模型"""
        models = await adapter.list_models(model_type="video")
        assert len(models) > 0
        for model in models:
            assert model.type == "video"

    @pytest.mark.asyncio
    async def test_list_chat_models_empty(self, adapter: PikaAdapter) -> None:
        """测试获取对话模型（空列表）"""
        models = await adapter.list_models(model_type="chat")
        assert len(models) == 0


class TestPikaAdapterStatusMapping:
    """PikaAdapter 状态映射测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> PikaAdapter:
        """创建适配器实例"""
        config = ProviderConfig(provider_type="pika", api_key=mock_api_key)
        return PikaAdapter(config=config)

    def test_map_pending_status(self, adapter: PikaAdapter) -> None:
        """测试 pending 状态映射"""
        assert adapter._map_pika_status("pending") == "pending"
        assert adapter._map_pika_status("queued") == "pending"
        assert adapter._map_pika_status("in_queue") == "pending"

    def test_map_processing_status(self, adapter: PikaAdapter) -> None:
        """测试 processing 状态映射"""
        assert adapter._map_pika_status("processing") == "processing"
        assert adapter._map_pika_status("in_progress") == "processing"
        assert adapter._map_pika_status("generating") == "processing"

    def test_map_success_status(self, adapter: PikaAdapter) -> None:
        """测试 success 状态映射"""
        assert adapter._map_pika_status("completed") == "success"
        assert adapter._map_pika_status("finished") == "success"
        assert adapter._map_pika_status("succeeded") == "success"
        assert adapter._map_pika_status("success") == "success"

    def test_map_failed_status(self, adapter: PikaAdapter) -> None:
        """测试 failed 状态映射"""
        assert adapter._map_pika_status("failed") == "failed"
        assert adapter._map_pika_status("error") == "failed"
        assert adapter._map_pika_status("failure") == "failed"
        assert adapter._map_pika_status("cancelled") == "failed"

    def test_map_unknown_status(self, adapter: PikaAdapter) -> None:
        """测试未知状态映射"""
        assert adapter._map_pika_status("unknown_status") == "pending"
