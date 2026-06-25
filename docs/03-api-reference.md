# AGN-SDK - API 设计规范与使用示例

## 1. API 设计规范

### 1.1 设计目标

| 目标 | 说明 |
|------|------|
| **一致性** | 所有方法风格统一，参数命名一致 |
| **易用性** | 简单直观，学习成本低 |
| **扩展性** | 支持各 Provider 的特有参数透传 |
| **类型安全** | 全程使用 Pydantic 模型 |
| **异步优先** | 所有 I/O 操作都是异步的 |

### 1.2 命名规范

**类名**：PascalCase（首字母大写，每个单词首字母大写）
```python
# 正确
class Client:
    pass

# 正确
class AgnesAdapter:
    pass

# 错误
class agnes_adapter:
    pass
```

**方法名**：snake_case（全小写，下划线分隔）
```python
# 正确
async def image_generate(self, prompt: str) -> ImageGenerationResult:
    pass

# 错误
async def ImageGenerate(self, prompt: str) -> ImageGenerationResult:
    pass
```

**参数名**：snake_case
```python
# 正确
async def chat(self, model: str, messages: List[ChatMessage]) -> ChatCompletion:
    pass

# 错误
async def chat(self, Model: str, Messages: List[ChatMessage]) -> ChatCompletion:
    pass
```

**常量名**：UPPER_SNAKE_CASE
```python
# 正确
DEFAULT_TIMEOUT = 300

# 错误
default_timeout = 300
```

### 1.3 参数设计规范

1. **位置参数**：必要参数放在前面，可选参数放在后面
2. **默认值**：合理的默认值，减少用户配置负担
3. **类型提示**：所有参数必须有类型提示
4. **可变参数**：使用 `**kwargs` 透传各 Provider 的特有参数
5. **枚举参数**：使用 `Literal` 类型限制可选值

```python
async def image_generate(
    self,
    model: str,                    # 必要参数
    prompt: str,                   # 必要参数
    size: str = "1024x1024",       # 可选参数，有默认值
    n: int = 1,                    # 可选参数，有默认值
    negative_prompt: str | None = None,  # 可选参数，默认 None
    reference_images: List[str] | None = None,
    response_format: Literal["url", "b64_json"] = "url",  # 枚举参数
    **kwargs,                      # 透传参数
) -> ImageGenerationResult:
    pass
```

### 1.4 返回值设计规范

1. **统一结构**：所有模型返回相同的数据结构
2. **包含元数据**：包含 ID、时间戳、模型名称等元信息
3. **原始响应**：可选包含原始响应（用于排查问题）
4. **错误处理**：抛出标准错误类型

### 1.5 错误处理规范

1. **标准错误类型**：使用 `agn.core.errors` 中定义的标准错误类型
2. **错误信息清晰**：包含原因和解决方案建议
3. **错误链**：保留原始错误信息，便于排查

---

## 2. 快速开始

### 2.1 安装

```bash
# 安装 SDK
pip install agn-sdk

# 或者从源码安装（开发模式）
pip install -e .
```

### 2.2 基础用法

```python
import asyncio
from agn import Client

async def main():
    # 创建客户端
    client = Client(
        provider="agnes",
        api_key="your-api-key",
        base_url="https://api.agnes.ai/v1",
    )
    
    # 文本对话
    response = await client.chat(
        model="claude-3-opus",
        messages=[
            {"role": "user", "content": "Hello!"}
        ]
    )
    print(response.choices[0].message.content)
    
    # 图像生成
    result = await client.image_generate(
        model="dall-e-3",
        prompt="A beautiful sunset over the ocean",
        size="1024x1024",
        n=1,
    )
    print(result.data[0].url)
    
    # 视频生成
    task = await client.video_create(
        model="video-gen-1",
        prompt="A cat walking on the street",
        width=1280,
        height=720,
    )
    
    # 轮询视频状态
    status = await client.video_poll(task.task_id)
    print(f"Status: {status.status}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 3. API 详细参考

### 3.1 Client 类

**构造函数**：

```python
Client(
    provider: str,                # Provider 类型，如 "agnes"、"openai"、"runway"
    api_key: str,                 # API Key
    base_url: str | None = None,  # API Base URL（可选，有默认值）
    poll_url: str | None = None,  # 轮询 URL（视频生成用，可选）
    timeout: int = 300,           # 请求超时（秒），默认 300
    max_retries: int = 3,         # 最大重试次数，默认 3
    retry_delay: float = 2.0,     # 重试延迟（秒），默认 2.0
)
```

**方法**：

| 方法 | 描述 |
|------|------|
| `chat()` | 文本对话 |
| `image_generate()` | 图像生成 |
| `video_create()` | 创建视频生成任务 |
| `video_poll()` | 查询视频任务状态 |
| `list_models()` | 获取可用模型列表 |
| `close()` | 关闭客户端，释放资源 |

---

### 3.2 chat() - 文本对话

**签名**：

```python
async def chat(
    self,
    model: str,
    messages: List[Dict[str, str]] | List[ChatMessage],
    temperature: float = 0.7,
    max_tokens: int | None = None,
    stream: bool = False,
    stop: List[str] | None = None,
    **kwargs,
) -> ChatCompletion | AsyncGenerator[ChatCompletionChunk, None]:
```

**参数**：

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `model` | `str` | 模型名称，如 `"claude-3-opus"` | 必填 |
| `messages` | `List[Dict] \| List[ChatMessage]` | 消息列表 | 必填 |
| `temperature` | `float` | 温度系数，控制输出随机性 | `0.7` |
| `max_tokens` | `int \| None` | 最大输出 token 数 | `None` |
| `stream` | `bool` | 是否流式输出 | `False` |
| `stop` | `List[str] \| None` | 停止词列表 | `None` |

**返回值**：

- `stream=False`：返回 `ChatCompletion` 对象
- `stream=True`：返回 `AsyncGenerator[ChatCompletionChunk, None]`

**示例**：

```python
# 简单对话
response = await client.chat(
    model="claude-3-opus",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ]
)
print(response.choices[0].message.content)

# 流式输出
async for chunk in client.chat(
    model="claude-3-opus",
    messages=[{"role": "user", "content": "Tell me a story."}],
    stream=True
):
    print(chunk.choices[0].delta.content, end="")
```

---

### 3.3 image_generate() - 图像生成

**签名**：

```python
async def image_generate(
    self,
    model: str,
    prompt: str,
    size: str = "1024x1024",
    n: int = 1,
    negative_prompt: str | None = None,
    reference_images: List[str] | None = None,
    mask: str | None = None,
    response_format: Literal["url", "b64_json"] = "url",
    **kwargs,
) -> ImageGenerationResult:
```

**参数**：

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `model` | `str` | 模型名称 | 必填 |
| `prompt` | `str` | 提示词 | 必填 |
| `size` | `str` | 图像尺寸，如 `"1024x1024"` | `"1024x1024"` |
| `n` | `int` | 生成数量 | `1` |
| `negative_prompt` | `str \| None` | 负面提示词 | `None` |
| `reference_images` | `List[str] \| None` | 参考图像列表（URL 或 base64） | `None` |
| `mask` | `str \| None` | 蒙版图像（局部编辑用） | `None` |
| `response_format` | `"url" \| "b64_json"` | 响应格式 | `"url"` |

**返回值**：`ImageGenerationResult`

**示例**：

```python
# 文本生图
result = await client.image_generate(
    model="dall-e-3",
    prompt="A cyberpunk city at night with neon lights",
    size="1024x1024",
    n=1,
)
print(result.data[0].url)

# 图生图
result = await client.image_generate(
    model="dall-e-3",
    prompt="Make this photo more colorful",
    reference_images=["https://example.com/photo.jpg"],
)

# 局部编辑（Inpaint）
result = await client.image_generate(
    model="dall-e-3",
    prompt="Replace the sky with a beautiful sunset",
    reference_images=["https://example.com/photo.jpg"],
    mask="https://example.com/mask.png",
)
```

---

### 3.4 video_create() - 创建视频生成任务

**签名**：

```python
async def video_create(
    self,
    model: str,
    prompt: str,
    width: int = 1280,
    height: int = 720,
    num_frames: int | None = None,
    frame_rate: int = 24,
    mode: Literal["text2video", "image2video", "keyframes", "multiimage"] = "text2video",
    reference_images: List[str] | None = None,
    negative_prompt: str | None = None,
    seed: int | None = None,
    **kwargs,
) -> VideoTask:
```

**参数**：

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `model` | `str` | 模型名称 | 必填 |
| `prompt` | `str` | 提示词 | 必填 |
| `width` | `int` | 视频宽度（必须是 8 的倍数） | `1280` |
| `height` | `int` | 视频高度（必须是 8 的倍数） | `720` |
| `num_frames` | `int \| None` | 帧数（部分模型需要） | `None` |
| `frame_rate` | `int` | 帧率 | `24` |
| `mode` | `"text2video" \| "image2video" \| "keyframes" \| "multiimage"` | 生成模式 | `"text2video"` |
| `reference_images` | `List[str] \| None` | 参考图像列表 | `None` |
| `negative_prompt` | `str \| None` | 负面提示词 | `None` |
| `seed` | `int \| None` | 随机种子 | `None` |

**返回值**：`VideoTask`

**示例**：

```python
# 文本生视频
task = await client.video_create(
    model="runway-gen3",
    prompt="A cat walking through a forest",
    width=1280,
    height=720,
    num_frames=81,
    frame_rate=24,
)
print(f"Task ID: {task.task_id}")

# 图生视频（关键帧模式）
task = await client.video_create(
    model="runway-gen3",
    prompt="A person walking from left to right",
    mode="keyframes",
    reference_images=[
        "https://example.com/start.png",
        "https://example.com/end.png",
    ],
    width=1280,
    height=720,
)

# 多图模式（2-8 张参考图）
task = await client.video_create(
    model="agnes-video",
    prompt="Create a video from these images",
    mode="multiimage",
    reference_images=[
        "https://example.com/img1.png",
        "https://example.com/img2.png",
        "https://example.com/img3.png",
    ],
)
```

---

### 3.5 video_poll() - 查询视频任务状态

**签名**：

```python
async def video_poll(
    self,
    task_id: str,
    model: str = "",
) -> VideoStatus:
```

**参数**：

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `task_id` | `str` | 任务 ID | 必填 |
| `model` | `str` | 模型名称（部分 Provider 需要） | `""` |

**返回值**：`VideoStatus`

**状态值说明**：

| 状态 | 说明 |
|------|------|
| `"pending"` | 任务等待中 |
| `"processing"` | 任务处理中 |
| `"success"` | 任务成功 |
| `"failed"` | 任务失败 |

**示例**：

```python
import time

# 创建任务
task = await client.video_create(
    model="runway-gen3",
    prompt="A cat walking",
)

# 轮询状态
while True:
    status = await client.video_poll(task.task_id)
    print(f"Status: {status.status}, Progress: {status.progress}%")
    
    if status.status == "success":
        print(f"Video URL: {status.video_url}")
        break
    elif status.status == "failed":
        print(f"Error: {status.error}")
        break
    
    await asyncio.sleep(5)  # 每 5 秒轮询一次
```

---

### 3.6 list_models() - 获取可用模型列表

**签名**：

```python
async def list_models(
    self,
    model_type: str | None = None,
) -> List[ModelInfo]:
```

**参数**：

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `model_type` | `"chat" \| "image" \| "video" \| None` | 模型类型过滤 | `None` |

**返回值**：`List[ModelInfo]`

**示例**：

```python
# 获取所有模型
models = await client.list_models()
for model in models:
    print(f"{model.id} - {model.name} ({model.type})")

# 只获取图像生成模型
image_models = await client.list_models(model_type="image")

# 只获取视频生成模型
video_models = await client.list_models(model_type="video")
```

---

## 4. 高级用法

### 4.1 错误处理

```python
from agn import Client
from agn.core.errors import (
    AGNError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
)

async def safe_chat():
    client = Client(provider="agnes", api_key="your-key")
    
    try:
        response = await client.chat(
            model="claude-3-opus",
            messages=[{"role": "user", "content": "Hello"}]
        )
        return response
    except AuthenticationError:
        print("API Key 无效，请检查")
    except RateLimitError:
        print("请求被限流，请稍后重试")
    except ValidationError as e:
        print(f"参数校验失败: {e}")
    except AGNError as e:
        print(f"SDK 错误: {e}")
```

### 4.2 配置管理

**方式一：代码配置（推荐）**

```python
client = Client(
    provider="agnes",
    api_key="your-key",
    base_url="https://api.agnes.ai/v1",
    timeout=600,
    max_retries=5,
)
```

**方式二：环境变量**

```bash
export AGN_PROVIDER=agnes
export AGN_API_KEY=your-key
export AGN_BASE_URL=https://api.agnes.ai/v1
```

```python
from agn import Client

client = Client()  # 自动从环境变量读取配置
```

**方式三：.env 文件**

```bash
# .env 文件
AGN_PROVIDER=agnes
AGN_API_KEY=your-key
AGN_BASE_URL=https://api.agnes.ai/v1
```

```python
from agn import Client
from agn.core.config import load_env

load_env()  # 加载 .env 文件
client = Client()
```

### 4.3 透传 Provider 特有参数

```python
# 透传 Agnes AI 特有参数
result = await client.image_generate(
    model="agnes-image",
    prompt="A beautiful sunset",
    size="1024x1024",
    # 以下是 Agnes AI 特有参数
    style="photorealistic",
    quality="hd",
)

# 透传 Runway 特有参数
task = await client.video_create(
    model="runway-gen3",
    prompt="A cat walking",
    width=1280,
    height=720,
    # 以下是 Runway 特有参数
    aspect_ratio="16:9",
    motion="slow",
)
```

### 4.4 Router 使用（多 Provider 路由）

```python
from agn import Router

# 配置多个 Provider
providers = [
    {"provider_type": "agnes", "api_key": "key1", "enabled": True},
    {"provider_type": "openai", "api_key": "key2", "enabled": True},
    {"provider_type": "runway", "api_key": "key3", "enabled": True},
]

router = Router(providers=providers)

# 自动路由到合适的 Provider
response = await router.chat(model="claude-3-opus", messages=[{"role": "user", "content": "Hello"}])
result = await router.image_generate(model="dall-e-3", prompt="A cat")
task = await router.video_create(model="runway-gen3", prompt="A dog running")
```
