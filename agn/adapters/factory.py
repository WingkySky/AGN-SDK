"""
AGN-SDK 适配器工厂

根据 provider_type 创建对应的适配器实例。
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agn.adapters.base import BaseAdapter
    from agn.models.common import ProviderConfig


class AdapterFactory:
    """
    适配器工厂

    负责注册和创建适配器实例。
    使用注册机制，支持动态添加新的 Provider 适配器。

    使用方式:
        # 注册适配器（通常在适配器文件末尾调用）
        AdapterFactory.register("agnes", AgnesAdapter)

        # 创建适配器实例
        config = ProviderConfig(provider_type="agnes", api_key="xxx")
        adapter = AdapterFactory.create(config)
    """

    _registry: dict[str, type["BaseAdapter"]] = {}

    @classmethod
    def register(
        cls,
        provider_type: str,
        adapter_class: type["BaseAdapter"],
    ) -> None:
        """
        注册适配器类

        Args:
            provider_type: Provider 类型标识
            adapter_class: 适配器类

        Raises:
            ValueError: 如果 provider_type 已注册
        """
        if provider_type in cls._registry:
            # 允许重复注册相同的类（幂等性）
            if cls._registry[provider_type] is not adapter_class:
                raise ValueError(
                    f"Provider type '{provider_type}' is already registered "
                    f"with class {cls._registry[provider_type].__name__}"
                )
            return

        cls._registry[provider_type] = adapter_class

    @classmethod
    def unregister(cls, provider_type: str) -> None:
        """
        注销适配器类

        Args:
            provider_type: Provider 类型标识
        """
        cls._registry.pop(provider_type, None)

    @classmethod
    def create(cls, config: "ProviderConfig") -> "BaseAdapter":
        """
        创建适配器实例

        Args:
            config: Provider 配置

        Returns:
            适配器实例

        Raises:
            ValueError: 如果 provider_type 不支持
        """
        provider_type = config.provider_type
        adapter_class = cls._registry.get(provider_type)

        if adapter_class is None:
            supported = ", ".join(sorted(cls._registry.keys()))
            raise ValueError(
                f"Unsupported provider type: '{provider_type}'. "
                f"Supported types: {supported if supported else 'none'}"
            )

        return adapter_class(config)

    @classmethod
    def list_providers(cls) -> dict[str, str]:
        """
        列出所有已注册的 Provider

        Returns:
            {provider_type: provider_name} 的字典
        """
        return {
            provider_type: adapter_class.provider_name
            for provider_type, adapter_class in cls._registry.items()
        }

    @classmethod
    def list_capabilities(cls) -> dict[str, list[str]]:
        """
        列出所有 Provider 支持的能力

        Returns:
            {provider_type: [capabilities]} 的字典
        """
        return {
            provider_type: adapter_class.supported_capabilities
            for provider_type, adapter_class in cls._registry.items()
        }

    @classmethod
    def get_adapter_class(cls, provider_type: str) -> type["BaseAdapter"] | None:
        """
        获取适配器类

        Args:
            provider_type: Provider 类型标识

        Returns:
            适配器类，如果不存在则返回 None
        """
        return cls._registry.get(provider_type)
