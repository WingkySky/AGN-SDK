"""
AGN-SDK 工具函数

通用的工具函数集合。
"""

import base64
import hashlib
import time
import uuid
from typing import Any


def generate_id(prefix: str = "") -> str:
    """
    生成唯一 ID

    Args:
        prefix: ID 前缀

    Returns:
        唯一 ID 字符串
    """
    unique_id = uuid.uuid4().hex[:12]
    if prefix:
        return f"{prefix}_{unique_id}"
    return unique_id


def current_timestamp() -> int:
    """
    获取当前时间戳（秒）

    Returns:
        当前 Unix 时间戳
    """
    return int(time.time())


def current_timestamp_ms() -> int:
    """
    获取当前时间戳（毫秒）

    Returns:
        当前 Unix 时间戳（毫秒）
    """
    return int(time.time() * 1000)


def normalize_image_input(image: str) -> dict[str, Any]:
    """
    归一化图像输入

    将各种格式的图像输入（URL、base64、data URI）转换为统一格式。

    Args:
        image: 图像输入（URL、base64、data URI）

    Returns:
        归一化后的图像数据字典
    """
    image = image.strip()

    # Data URI 格式
    if image.startswith("data:"):
        return {"type": "data_uri", "data": image}

    # Base64 格式（可能带或不带前缀）
    if is_base64(image):
        # 检查是否包含头部
        if "," in image:
            header, data = image.split(",", 1)
            return {"type": "base64", "header": header, "data": data}
        return {"type": "base64", "data": image}

    # URL 格式
    if image.startswith("http://") or image.startswith("https://"):
        return {"type": "url", "url": image}

    # 文件路径（尝试作为本地文件读取）
    if not image.startswith("http"):
        return {"type": "file", "path": image}

    return {"type": "unknown", "data": image}


def is_base64(s: str) -> bool:
    """
    检查字符串是否为 base64 编码

    Args:
        s: 待检查的字符串

    Returns:
        是否为 base64
    """
    if not s:
        return False

    # 移除可能的 data URI 前缀
    if "," in s:
        s = s.split(",", 1)[1]

    # 检查字符集
    try:
        base64.b64decode(s, validate=True)
        return True
    except Exception:
        return False


def encode_base64(data: bytes) -> str:
    """
    将字节数据编码为 base64 字符串

    Args:
        data: 原始字节数据

    Returns:
        base64 编码字符串
    """
    return base64.b64encode(data).decode("utf-8")


def decode_base64(data: str) -> bytes:
    """
    将 base64 字符串解码为字节数据

    Args:
        data: base64 编码字符串

    Returns:
        原始字节数据
    """
    # 移除可能的 data URI 前缀
    if "," in data:
        data = data.split(",", 1)[1]
    return base64.b64decode(data)


def md5_hash(data: str | bytes) -> str:
    """
    计算 MD5 哈希

    Args:
        data: 输入数据

    Returns:
        MD5 哈希值（十六进制字符串）
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.md5(data).hexdigest()


def validate_video_dimensions(width: int, height: int) -> tuple[int, int]:
    """
    验证并修正视频尺寸

    视频宽高必须是 8 的倍数。

    Args:
        width: 视频宽度
        height: 视频高度

    Returns:
        修正后的 (width, height)
    """
    # 向上取整到最近的 8 的倍数
    width = ((width + 7) // 8) * 8
    height = ((height + 7) // 8) * 8

    return width, height


def parse_size(size: str) -> tuple[int, int]:
    """
    解析图像尺寸字符串

    Args:
        size: 尺寸字符串，如 "1024x1024"

    Returns:
        (width, height) 元组

    Raises:
        ValueError: 格式不正确
    """
    try:
        parts = size.lower().split("x")
        if len(parts) != 2:
            raise ValueError(f"Invalid size format: {size}")
        return int(parts[0]), int(parts[1])
    except ValueError as e:
        raise ValueError(f"Invalid size format: {size}") from e


def build_size_string(width: int, height: int) -> str:
    """
    构建图像尺寸字符串

    Args:
        width: 宽度
        height: 高度

    Returns:
        尺寸字符串，如 "1024x1024"
    """
    return f"{width}x{height}"


def merge_dicts(base: dict[str, Any], *overrides: dict[str, Any]) -> dict[str, Any]:
    """
    合并字典

    后续字典的值会覆盖前面字典的值。

    Args:
        base: 基础字典
        *overrides: 覆盖字典

    Returns:
        合并后的字典
    """
    result = base.copy()
    for override in overrides:
        if override:
            result.update(override)
    return result
