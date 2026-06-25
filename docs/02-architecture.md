# AGN-SDK - 技术架构设计

## 1. 整体架构

### 1.1 架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           AGN-SDK                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────┐                                               │
│  │       API 层         │  ── 对外统一接口（agn.Client）                   │
│  │  - chat()           │                                               │
│  │  - image_generate() │                                               │
│  │  - video_create()   │                                               │
│  │  - video_poll()     │                                               │
│  └──────────┬──────────┘                                               │
│             │                                                           │
│             ▼                                                           │
│  ┌─────────────────────┐                                               │
│  │     路由器层         │  ── 模型路由、负载均衡、Fallback                  │
│  │  - Router           │                                               │
│  │  - load_balance()   │                                               │
│  │  - fallback()       │                                               │
│  └──────────┬──────────┘                                               │
│             │                                                           │
│             ▼                                                           │
│  ┌─────────────────────┐                                               │
│  │     适配器层         │  ── 各模型提供商的适配器实现                      │
│  │  - AgnesAdapter     │                                               │
│  │  - OpenAIAdapter    │                                               │
│  │  - StabilityAdapter │                                               │
│  │  - RunwayAdapter    │                                               │
│  └──────────┬──────────┘                                               │
│             │                                                           │
│             ▼                                                           │
│  ┌─────────────────────┐                                               │
│  │     核心层           │  ── 通用能力、工具函数、数据模型                   │
│  │  - 重试机制         │                                               │
│  │  - 错误映射         │                                               │
│  │  - HTTP 客户端      │                                               │
│  │  - 数据模型         │                                               │
│  └─────────────────────┘                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 分层职责

| 层级 | 职责 | 文件位置 |
|------|------|---------|
| **API 层** | 对外统一接口，用户直接调用 | `agn/__init__.py`, `agn/client.py` |
| **路由器层** | 模型选择、路由分发、负载均衡 | `agn/router.py` |
| **适配器层** | 各模型提供商的具体实现 | `agn/adapters/` |
| **核心层** | 通用能力、工具函数、数据模型 | `agn/core/`, `agn/models/` |

---

## 2. 核心模块设计

### 2.1 模块总览

```
agn/
├── __init__.py              # SDK 入口，导出核心类
├── client.py                # 统一客户端（API 层）
├── router.py                # 路由器（路由层）
├── adapters/                # 适配器层
│   ├── __init__.py
│   ├── base.py              # 适配器基类（抽象接口）
│   ├── agnes.py             # Agnes AI 适配器
│   ├── openai.py            # OpenAI 适配器
│   ├── stability.py         # Stability AI 适配器
│   ├── runway.py            # Runway 适配器
│   └── factory.py           # 适配器工厂
├── core/                    # 核心层
│   ├── __init__.py
│   ├── http_client.py       # HTTP 客户端（连接池、重试）
│   ├── retry.py             # 重试机制封装
│   ├── errors.py            # 错误定义与映射
│   ├── config.py            # 配置管理
│   └── utils.py             # 工具函数
└── models/                  # 数据模型
    ├── __init__.py
    ├── common.py            # 通用数据结构
    ├── chat.py              # 文本对话相关模型
    ├── image.py             # 图像生成相关模型
    └── video.py             # 视频生成相关模型
```

### 2.2 API 层 - Client 设计

**类名**：`agn.Client`

**职责**：提供统一的对外接口，是用户使用 SDK 的唯一入口。

**核心方法**：

```python
class Client:
    def __init__(self, provider: str, api_key: str, **kwargs):
        """初始化客户端"""
        pass
    
    # 文本对话
    async def chat(
        self,
        model: str,
        messages: List[ChatMessage],
        stream: bool = False,
        **kwargs
    ) -> ChatCompletion | AsyncGenerator[ChatCompletionChunk, None]:
        """文本对话"""
        pass
    
    # 图像生成
    async def image_generate(
        self,
        model: str,
        prompt: str,
        size: str = "1024x1024",
        n: int = 1,
        negative_prompt: str | None = None,
        reference_images: List[str] | None = None,
        response_format: str = "url",
        **kwargs
    ) -> ImageGenerationResult:
        """图像生成"""
        pass
    
    # 视频生成 - 创建任务
    async def video_create(
        self,
        model: str,
        prompt: str,
        width: int = 1280,
        height: int = 720,
        num_frames: int | None = None,
        frame_rate: int = 24,
        mode: str = "text2video",
        reference_images: List[str] | None = None,
        negative_prompt: str | None = None,
        **kwargs
    ) -> VideoTask:
        """创建视频生成任务"""
        pass
    
    # 视频生成 - 查询状态
    async def video_poll(
        self,
        task_id: str,
        model: str = "",
    ) -> VideoStatus:
        """查询视频任务状态"""
        pass
    
    # 模型列表
    async def list_models(
        self,
        model_type: str | None = None,  # "chat" | "image" | "video"
    ) -> List[ModelInfo]:
        """获取可用模型列表"""
        pass
```

**设计要点**：
- 单一入口，所有方法都在一个 Client 类中
- 参数命名参考 OpenAI API，降低学习成本
- 返回类型使用 Pydantic 模型，类型安全
- 所有方法都是异步的
- `**kwargs` 透传各 Provider 的特有参数

### 2.3 路由器层 - Router 设计

**类名**：`agn.Router`

**职责**：根据配置自动选择合适的 Provider 和模型，支持负载均衡和 Fallback。

**核心方法**：

```python
class Router:
    def __init__(self, providers: List[ProviderConfig]):
        """初始化路由器"""
        pass
    
    async def chat(
        self,
        model: str,
        messages: List[ChatMessage],
        **kwargs
    ) -> ChatCompletion:
        """路由文本对话请求"""
        pass
    
    async def image_generate(
        self,
        model: str,
        prompt: str,
        **kwargs
    ) -> ImageGenerationResult:
        """路由图像生成请求"""
        pass
    
    async def video_create(
        self,
        model: str,
        prompt: str,
        **kwargs
    ) -> VideoTask:
        """路由视频创建请求"""
        pass
```

**路由策略**：
1. **按模型名路由**：根据 model 参数找到对应的 Provider
2. **负载均衡**：同一 Provider 多个实例时轮询
3. **Fallback**：主 Provider 失败时自动切换到备用 Provider
4. **成本优先**：根据配置的成本权重选择最低成本的 Provider

### 2.4 适配器层 - Adapter 设计

#### 2.4.1 适配器基类

**类名**：`agn.adapters.BaseAdapter`

**职责**：定义适配器的标准接口，所有具体适配器都必须实现这些方法。

```python
class BaseAdapter(ABC):
    # 元信息
    provider_type: ClassVar[str] = ""      # 唯一标识，如 "agnes"
    provider_name: ClassVar[str] = ""      # 显示名称，如 "Agnes AI"
    supported_capabilities: ClassVar[List[str]] = []  # 支持的能力
    
    def __init__(self, config: ProviderConfig):
        """初始化适配器"""
        pass
    
    @abstractmethod
    async def chat(
        self,
        model: str,
        messages: List[ChatMessage],
        **kwargs
    ) -> ChatCompletion:
        """文本对话"""
        pass
    
    @abstractmethod
    async def image_generate(
        self,
        model: str,
        prompt: str,
        **kwargs
    ) -> ImageGenerationResult:
        """图像生成"""
        pass
    
    @abstractmethod
    async def video_create(
        self,
        model: str,
        prompt: str,
        **kwargs
    ) -> VideoTask:
        """创建视频任务"""
        pass
    
    @abstractmethod
    async def video_poll(
        self,
        task_id: str,
        model: str = "",
    ) -> VideoStatus:
        """查询视频状态"""
        pass
    
    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """列出可用模型"""
        pass
    
    async def close(self) -> None:
        """关闭适配器，释放资源"""
        pass
```

#### 2.4.2 适配器工厂

**类名**：`agn.adapters.AdapterFactory`

**职责**：根据 provider_type 创建对应的适配器实例。

```python
class AdapterFactory:
    _registry: Dict[str, Type[BaseAdapter]] = {}
    
    @classmethod
    def register(cls, provider_type: str, adapter_class: Type[BaseAdapter]):
        """注册适配器类"""
        cls._registry[provider_type] = adapter_class
    
    @classmethod
    def create(cls, provider_type: str, config: ProviderConfig) -> BaseAdapter:
        """创建适配器实例"""
        adapter_class = cls._registry.get(provider_type)
        if adapter_class is None:
            raise ValueError(f"不支持的 Provider 类型: {provider_type}")
        return adapter_class(config)
    
    @classmethod
    def list_providers(cls) -> Dict[str, str]:
        """列出所有支持的 Provider"""
        return {k: v.provider_name for k, v in cls._registry.items()}
```

**使用方式**：每个适配器文件末尾调用 `AdapterFactory.register()` 注册。

### 2.5 核心层设计

#### 2.5.1 HTTP 客户端

**类名**：`agn.core.http_client.AsyncHttpClient`

**职责**：统一的 HTTP 客户端，管理连接池、重试、超时。

**特性**：
- 基于 httpx.AsyncClient 封装
- 自动重试（网络错误、5xx 错误）
- 指数退避策略
- 连接池复用
- 统一的错误处理

#### 2.5.2 错误处理

**文件**：`agn/core/errors.py`

**职责**：定义标准错误类型，映射各 Provider 的错误。

**错误类型**：

```python
class AGNError(Exception):
    """SDK 基础错误"""
    pass

class AuthenticationError(AGNError):
    """认证错误（API Key 无效）"""
    pass

class RateLimitError(AGNError):
    """限流错误"""
    pass

class ValidationError(AGNError):
    """参数校验错误"""
    pass

class ModelNotFoundError(AGNError):
    """模型不存在"""
    pass

class APIError(AGNError):
    """API 调用错误"""
    pass

class TimeoutError(AGNError):
    """超时错误"""
    pass
```

**错误映射**：每个适配器将 Provider 特定的错误映射到上述标准错误类型。

#### 2.5.3 配置管理

**类名**：`agn.core.config.Config`

**职责**：管理 SDK 配置，支持环境变量、配置文件、代码配置。

**配置来源优先级**：
1. 代码传入的参数（最高优先级）
2. `.env` 文件
3. 环境变量
4. 默认值（最低优先级）

---

## 3. 数据模型设计

### 3.1 通用模型

#### ProviderConfig

```python
class ProviderConfig(BaseModel):
    """Provider 配置"""
    provider_type: str                # Provider 类型
    api_key: str                      # API Key
    base_url: str | None = None       # API Base URL（可选，有默认值）
    poll_url: str | None = None       # 轮询 URL（视频生成用）
    timeout: int = 300               # 请求超时（秒）
    max_retries: int = 3             # 最大重试次数
    retry_delay: float = 2.0         # 重试延迟（秒）
    enabled: bool = True             # 是否启用
```

#### ModelInfo

```python
class ModelInfo(BaseModel):
    """模型信息"""
    id: str                          # 模型标识
    name: str                        # 显示名称
    type: str                        # 模型类型: "chat" | "image" | "video"
    provider: str                    # 提供商名称
    capabilities: List[str]          # 能力列表
    max_tokens: int | None = None    # 最大 token 数（仅 chat）
    supports_streaming: bool = False # 是否支持流式（仅 chat）
```

### 3.2 文本对话模型

#### ChatMessage

```python
class ChatMessage(BaseModel):
    """对话消息"""
    role: str                        # "system" | "user" | "assistant" | "tool"
    content: str                     # 消息内容
    name: str | None = None          # 消息发送者名称（可选）
```

#### ChatCompletion

```python
class ChatCompletion(BaseModel):
    """文本对话完成结果"""
    id: str                          # 响应 ID
    object: str = "chat.completion"
    created: int                     # 创建时间戳
    model: str                       # 使用的模型
    choices: List[ChatChoice]
    usage: ChatUsage | None = None
```

#### ChatChoice

```python
class ChatChoice(BaseModel):
    """对话选项"""
    index: int
    message: ChatMessage
    finish_reason: str | None = None
```

#### ChatUsage

```python
class ChatUsage(BaseModel):
    """使用统计"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
```

### 3.3 图像生成模型

#### ImageGenerationResult

```python
class ImageGenerationResult(BaseModel):
    """图像生成结果"""
    id: str
    object: str = "image.generation"
    created: int
    model: str
    data: List[ImageData]
```

#### ImageData

```python
class ImageData(BaseModel):
    """图像数据"""
    url: str | None = None           # 图像 URL
    b64_json: str | None = None      # Base64 编码的图像
    revised_prompt: str | None = None # 修改后的提示词
```

### 3.4 视频生成模型

#### VideoTask

```python
class VideoTask(BaseModel):
    """视频任务信息"""
    task_id: str                     # 任务 ID
    model: str                       # 使用的模型
    status: str = "pending"          # 初始状态
    created_at: int                  # 创建时间戳
```

#### VideoStatus

```python
class VideoStatus(BaseModel):
    """视频任务状态"""
    task_id: str
    status: str                      # "pending" | "processing" | "success" | "failed"
    video_url: str | None = None     # 视频 URL（成功时）
    progress: int | None = None      # 进度 0-100
    error: str | None = None         # 错误信息（失败时）
    created_at: int | None = None
    updated_at: int | None = None
```

---

## 4. 扩展机制

### 4.1 新增 Provider 适配器

**步骤**：

1. 创建文件 `agn/adapters/new_provider.py`
2. 继承 `BaseAdapter`
3. 实现所有抽象方法
4. 在文件末尾注册：`AdapterFactory.register("new_provider", NewProviderAdapter)`

**示例**：

```python
# agn/adapters/new_provider.py
from .base import BaseAdapter
from .factory import AdapterFactory
from agn.models.chat import ChatCompletion
from agn.models.image import ImageGenerationResult
from agn.models.video import VideoTask, VideoStatus
from agn.models.common import ModelInfo, ProviderConfig

class NewProviderAdapter(BaseAdapter):
    provider_type = "new_provider"
    provider_name = "New Provider"
    supported_capabilities = ["chat", "image", "video"]
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        # 初始化 HTTP 客户端等
    
    async def chat(self, model: str, messages: List[ChatMessage], **kwargs) -> ChatCompletion:
        # 实现调用逻辑
        pass
    
    async def image_generate(self, model: str, prompt: str, **kwargs) -> ImageGenerationResult:
        # 实现调用逻辑
        pass
    
    async def video_create(self, model: str, prompt: str, **kwargs) -> VideoTask:
        # 实现调用逻辑
        pass
    
    async def video_poll(self, task_id: str, model: str = "") -> VideoStatus:
        # 实现调用逻辑
        pass
    
    async def list_models(self) -> List[ModelInfo]:
        # 返回模型列表
        pass

AdapterFactory.register("new_provider", NewProviderAdapter)
```

### 4.2 插件化加载（可选）

未来可以支持从外部目录动态加载适配器插件：

```python
# 扫描指定目录，自动加载适配器
from importlib import import_module
import os

def load_plugins(plugins_dir: str):
    for filename in os.listdir(plugins_dir):
        if filename.endswith(".py") and not filename.startswith("_"):
            module_name = filename[:-3]
            import_module(f"{plugins_dir}.{module_name}")
```
