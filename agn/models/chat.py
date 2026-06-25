"""
AGN-SDK 文本对话数据模型

定义文本对话相关的 Pydantic 模型。
"""

from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """
    对话消息

    表示单条对话消息，包含角色和内容。
    """

    role: Literal["system", "user", "assistant", "tool"] = Field(
        ...,
        description="消息角色：system（系统）、user（用户）、assistant（助手）、tool（工具）",
    )
    content: str = Field(..., description="消息内容")
    name: str | None = Field(None, description="消息发送者名称（可选）")
    tool_calls: list[dict[str, Any]] | None = Field(
        None,
        description="工具调用列表（可选）",
    )
    tool_call_id: str | None = Field(None, description="工具调用 ID（可选）")

    model_config = {"extra": "allow"}


class ChatFunction(BaseModel):
    """
    对话函数定义

    用于定义可被模型调用的函数。
    """

    name: str = Field(..., description="函数名称")
    description: str | None = Field(None, description="函数描述")
    parameters: dict[str, Any] | None = Field(None, description="函数参数模式")

    model_config = {"extra": "allow"}


class ChatChoice(BaseModel):
    """
    对话选项

    表示对话完成的一个选项。
    """

    index: int = Field(..., description="选项索引")
    message: ChatMessage = Field(..., description="生成的回复消息")
    finish_reason: str | None = Field(
        None,
        description="结束原因：stop、length、content_filter、function_call",
    )

    model_config = {"extra": "allow"}


class ChatUsage(BaseModel):
    """
    使用统计

    记录 token 使用量。
    """

    prompt_tokens: int = Field(..., description="提示词 token 数")
    completion_tokens: int = Field(..., description="完成回复 token 数")
    total_tokens: int = Field(..., description="总 token 数")

    model_config = {"extra": "allow"}


class ChatCompletion(BaseModel):
    """
    文本对话完成结果

    表示一次完整的文本对话响应。
    """

    id: str = Field(..., description="响应 ID")
    object: str = Field("chat.completion", description="对象类型")
    created: int = Field(..., description="创建时间戳")
    model: str = Field(..., description="使用的模型")
    choices: list[ChatChoice] = Field(..., description="回复选项列表")
    usage: ChatUsage | None = Field(None, description="Token 使用统计")
    service_tier: str | None = Field(None, description="服务层级")
    system_fingerprint: str | None = Field(None, description="系统指纹")

    model_config = {"extra": "allow"}


class ChatCompletionDelta(BaseModel):
    """
    流式增量数据

    表示流式输出时的单个增量内容。
    """

    index: int = Field(..., description="增量索引")
    delta: ChatMessage = Field(..., description="增量消息内容")
    finish_reason: str | None = Field(None, description="结束原因")

    model_config = {"extra": "allow"}


class ChatCompletionChunk(BaseModel):
    """
    流式对话块

    用于流式输出时的单个数据块。
    """

    id: str = Field(..., description="响应 ID")
    object: str = Field("chat.completion.chunk", description="对象类型")
    created: int = Field(..., description="创建时间戳")
    model: str = Field(..., description="使用的模型")
    choices: list[ChatCompletionDelta] = Field(..., description="增量选项列表")

    model_config = {"extra": "allow"}


class ChatCompletionRequest(BaseModel):
    """
    对话请求参数

    用于构建对话请求的参数集合。
    """

    model: str = Field(..., description="模型名称")
    messages: list[ChatMessage] = Field(..., description="消息列表")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="温度系数")
    top_p: float | None = Field(None, ge=0.0, le=1.0, description="核采样概率")
    n: int = Field(1, ge=1, le=128, description="生成选项数量")
    stream: bool = Field(False, description="是否流式输出")
    stop: str | list[str] | None = Field(None, description="停止词")
    max_tokens: int | None = Field(None, ge=1, description="最大 token 数")
    presence_penalty: float = Field(0.0, ge=-2.0, le=2.0, description="存在惩罚")
    frequency_penalty: float = Field(0.0, ge=-2.0, le=2.0, description="频率惩罚")
    user: str | None = Field(None, description="用户标识")

    model_config = {"extra": "allow"}
