"""
AGN-SDK 配置管理

支持从环境变量、.env 文件加载配置。
"""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


def load_env(env_file: str | Path | None = None) -> None:
    """
    加载 .env 文件中的环境变量

    Args:
        env_file: .env 文件路径，默认从当前目录和项目根目录查找
    """
    if env_file is None:
        # 尝试从当前目录和多个可能的路径查找 .env 文件
        possible_paths = [
            Path.cwd() / ".env",
            Path(__file__).parent.parent.parent / ".env",
        ]
        for path in possible_paths:
            if path.exists():
                load_dotenv(path)
                return
    else:
        load_dotenv(env_file)


def get_env(
    key: str,
    default: str | None = None,
    required: bool = False,
) -> str | None:
    """
    获取环境变量值

    Args:
        key: 环境变量名
        default: 默认值
        required: 是否为必需字段

    Returns:
        环境变量值

    Raises:
        ValueError: 如果 required=True 但环境变量未设置
    """
    value = os.getenv(key, default)

    if required and value is None:
        raise ValueError(f"Required environment variable '{key}' is not set")

    return value


def get_provider_config(
    provider_type: str,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    获取 Provider 配置

    优先使用传入的配置，其次使用环境变量，最后使用默认值。

    Args:
        provider_type: Provider 类型（如 'agnes'、'openai'）
        config: 直接传入的配置（最高优先级）

    Returns:
        合并后的配置字典
    """
    # 环境变量前缀
    prefix = f"AGN_{provider_type.upper()}"

    # 从环境变量构建配置
    env_config: dict[str, Any] = {}

    api_key = os.getenv(f"{prefix}_API_KEY")
    if api_key:
        env_config["api_key"] = api_key

    base_url = os.getenv(f"{prefix}_BASE_URL")
    if base_url:
        env_config["base_url"] = base_url

    # 合并配置（优先级：config > env_config）
    result = {
        "provider_type": provider_type,
        "api_key": env_config.get("api_key", ""),
        "base_url": env_config.get("base_url"),
    }

    if config:
        result.update(config)

    return result


class Config:
    """
    SDK 配置类

    用于管理 SDK 的全局配置。
    """

    def __init__(
        self,
        timeout: int = 300,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        default_provider: str | None = None,
    ) -> None:
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.default_provider = default_provider

    def update(self, **kwargs: Any) -> None:
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
