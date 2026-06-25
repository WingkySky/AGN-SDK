"""
AGN-SDK 图像生成数据模型

定义图像生成相关的 Pydantic 模型。
"""

from typing import Literal

from pydantic import BaseModel, Field


class ImageData(BaseModel):
    """
    图像数据

    表示单张生成的图像。
    """

    url: str | None = Field(None, description="图像 URL")
    b64_json: str | None = Field(None, description="Base64 编码的图像")
    revised_prompt: str | None = Field(
        None, description="修改后的提示词（如模型优化过）"
    )

    model_config = {"extra": "allow"}


class ImageGenerationResult(BaseModel):
    """
    图像生成结果

    表示一次图像生成请求的响应。
    """

    id: str = Field(..., description="响应 ID")
    object: str = Field("image.generation", description="对象类型")
    created: int = Field(..., description="创建时间戳")
    model: str = Field(..., description="使用的模型")
    data: list[ImageData] = Field(..., description="生成的图像列表")

    model_config = {"extra": "allow"}


class ImageEditRequest(BaseModel):
    """
    图像编辑请求参数

    用于图生图或局部编辑的请求参数。
    """

    model: str = Field(..., description="模型名称")
    prompt: str = Field(..., description="提示词")
    image: str = Field(..., description="参考图像（URL 或 base64）")
    mask: str | None = Field(None, description="蒙版图像（URL 或 base64，局部编辑用）")
    size: Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"] = Field(
        "1024x1024",
        description="图像尺寸",
    )
    n: int = Field(1, ge=1, le=10, description="生成数量")
    response_format: Literal["url", "b64_json"] = Field("url", description="响应格式")

    model_config = {"extra": "allow"}


class ImageVariationRequest(BaseModel):
    """
    图像变体请求参数

    用于生成图像变体的请求参数。
    """

    model: str = Field(..., description="模型名称")
    image: str = Field(..., description="原图像（URL 或 base64）")
    size: Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"] = Field(
        "1024x1024",
        description="图像尺寸",
    )
    n: int = Field(1, ge=1, le=10, description="生成数量")
    response_format: Literal["url", "b64_json"] = Field("url", description="响应格式")

    model_config = {"extra": "allow"}


class ImageGenerationOptions(BaseModel):
    """
    图像生成选项

    通用的图像生成配置选项。
    """

    size: str = Field("1024x1024", description="图像尺寸")
    n: int = Field(1, ge=1, le=10, description="生成数量")
    quality: Literal["standard", "hd"] = Field("standard", description="图像质量")
    style: Literal["vivid", "natural"] | None = Field(
        None, description="图像风格（部分模型支持）"
    )
    response_format: Literal["url", "b64_json"] = Field("url", description="响应格式")

    model_config = {"extra": "allow"}
