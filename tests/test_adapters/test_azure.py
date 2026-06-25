"""
AGN-SDK Azure 适配器测试
"""

import pytest

from agn.adapters.azure import AzureAdapter
from agn.models.common import ProviderConfig


class TestAzureAdapter:
    """AzureAdapter 类测试"""

    @pytest.fixture
    def adapter_config(self, mock_api_key: str) -> ProviderConfig:
        """创建适配器配置"""
        return ProviderConfig(
            provider_type="azure",
            api_key=mock_api_key,
            resource_name="test-resource",
            deployment_id="test-deployment",
        )

    @pytest.fixture
    def adapter(self, adapter_config: ProviderConfig) -> AzureAdapter:
        """创建适配器实例"""
        return AzureAdapter(config=adapter_config)

    def test_adapter_init(self, adapter: AzureAdapter) -> None:
        """测试适配器初始化"""
        assert adapter.provider_type == "azure"
        assert adapter.provider_name == "Azure OpenAI"
        assert adapter.resource_name == "test-resource"
        assert adapter.deployment_id == "test-deployment"

    def test_adapter_base_url(self, adapter: AzureAdapter) -> None:
        """测试 Base URL 构建"""
        expected_url = "https://test-resource.openai.azure.com/openai/deployments/test-deployment"
        assert adapter.base_url == expected_url

    def test_adapter_init_with_base_url(self, mock_api_key: str) -> None:
        """测试使用自定义 Base URL"""
        config = ProviderConfig(
            provider_type="azure",
            api_key=mock_api_key,
            base_url="https://custom.azure.com/openai/deployments/custom",
        )
        adapter = AzureAdapter(config=config)
        assert adapter.base_url == "https://custom.azure.com/openai/deployments/custom"

    def test_adapter_init_missing_config(self, mock_api_key: str) -> None:
        """测试缺少必要配置时抛出错误"""
        config = ProviderConfig(
            provider_type="azure",
            api_key=mock_api_key,
            resource_name="test-resource",
        )
        with pytest.raises(ValueError):
            AzureAdapter(config=config)

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, adapter: AzureAdapter) -> None:
        """测试异步上下文管理器"""
        async with adapter as a:
            assert a._http_client is not None


class TestAzureAdapterListModels:
    """AzureAdapter 模型列表测试"""

    @pytest.fixture
    def adapter(self, mock_api_key: str) -> AzureAdapter:
        """创建适配器实例"""
        config = ProviderConfig(
            provider_type="azure",
            api_key=mock_api_key,
            resource_name="test-resource",
            deployment_id="test-deployment",
        )
        return AzureAdapter(config=config)

    @pytest.mark.asyncio
    async def test_list_models(self, adapter: AzureAdapter) -> None:
        """测试获取模型列表"""
        models = await adapter.list_models()
        assert len(models) > 0

        types = {m.type for m in models}
        assert "chat" in types
        assert "image" in types
