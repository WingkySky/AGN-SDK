"""
AGN-SDK 测试配置

pytest 配置文件。
"""

import pytest


@pytest.fixture
def mock_api_key() -> str:
    """模拟 API Key"""
    return "test-api-key-12345"


@pytest.fixture
def mock_provider_config(mock_api_key: str) -> dict:
    """模拟 Provider 配置"""
    return {
        "provider_type": "agnes",
        "api_key": mock_api_key,
        "base_url": "https://api.test.agnes.ai/v1",
    }


@pytest.fixture
def sample_chat_messages() -> list[dict]:
    """模拟对话消息"""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ]


@pytest.fixture
def sample_image_prompt() -> str:
    """模拟图像提示词"""
    return "A beautiful sunset over the ocean"


@pytest.fixture
def sample_video_prompt() -> str:
    """模拟视频提示词"""
    return "A cat walking through a forest"
