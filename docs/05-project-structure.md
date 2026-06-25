# AGN-SDK - 项目目录结构与开发计划

## 1. 目录结构

### 1.1 完整目录树

```
agn-sdk/                              # SDK 项目根目录
├── agn/                              # SDK 核心代码
│   ├── __init__.py                   # SDK 入口，导出核心类
│   ├── client.py                     # 统一客户端（API 层）
│   ├── router.py                     # 路由器（路由层）
│   ├── adapters/                     # 适配器层
│   │   ├── __init__.py
│   │   ├── base.py                   # 适配器基类（抽象接口）
│   │   ├── factory.py                # 适配器工厂
│   │   ├── agnes.py                  # Agnes AI 适配器
│   │   ├── openai.py                 # OpenAI 适配器
│   │   ├── azure.py                  # Azure OpenAI 适配器
│   │   ├── runway.py                 # Runway 适配器
│   │   ├── pika.py                   # Pika 适配器
│   │   ├── stability.py              # Stability AI 适配器
│   │   ├── qianfan.py                # 百度千帆适配器
│   │   ├── tongyi.py                 # 阿里通义适配器
│   │   └── ollama.py                 # Ollama 适配器
│   ├── core/                         # 核心层
│   │   ├── __init__.py
│   │   ├── http_client.py            # HTTP 客户端（连接池、重试）
│   │   ├── retry.py                  # 重试机制封装
│   │   ├── errors.py                 # 错误定义与映射
│   │   ├── config.py                 # 配置管理
│   │   └── utils.py                  # 工具函数
│   └── models/                       # 数据模型
│       ├── __init__.py
│       ├── common.py                 # 通用数据结构（ProviderConfig, ModelInfo）
│       ├── chat.py                   # 文本对话相关模型
│       ├── image.py                  # 图像生成相关模型
│       └── video.py                  # 视频生成相关模型
├── docs/                             # 文档目录
│   ├── 01-overview.md                # 项目概述与目标
│   ├── 02-architecture.md            # 技术架构设计
│   ├── 03-api-reference.md           # API 设计规范与使用示例
│   ├── 04-models-roadmap.md          # 兼容模型规划与路线图
│   └── 05-project-structure.md       # 项目目录结构与开发计划
├── tests/                            # 测试目录
│   ├── __init__.py
│   ├── test_client.py                # Client 测试
│   ├── test_router.py                # Router 测试
│   ├── test_adapters/                # 适配器测试
│   │   ├── test_agnes.py
│   │   ├── test_openai.py
│   │   └── test_runway.py
│   ├── test_core/                    # 核心层测试
│   │   ├── test_http_client.py
│   │   ├── test_retry.py
│   │   └── test_errors.py
│   └── conftest.py                   # 测试配置
├── examples/                         # 示例代码
│   ├── basic_usage.py                # 基础用法示例
│   ├── chat_example.py               # 文本对话示例
│   ├── image_generation_example.py   # 图像生成示例
│   ├── video_generation_example.py   # 视频生成示例
│   └── router_example.py             # 路由器示例
├── pyproject.toml                    # Python 项目配置
├── setup.py                          # 安装脚本
├── README.md                         # 项目说明
├── CHANGELOG.md                      # 变更日志
└── .env.example                      # 环境变量示例
```

### 1.2 目录职责说明

| 目录 | 职责 | 说明 |
|------|------|------|
| `agn/` | SDK 核心代码 | 用户直接使用的代码 |
| `agn/adapters/` | 适配器层 | 各模型提供商的具体实现 |
| `agn/core/` | 核心层 | 通用能力、工具函数 |
| `agn/models/` | 数据模型 | Pydantic 模型定义 |
| `docs/` | 文档 | 项目文档 |
| `tests/` | 测试 | 单元测试和集成测试 |
| `examples/` | 示例 | 使用示例代码 |

---

## 2. 文件详细说明

### 2.1 入口文件

#### `agn/__init__.py`

**职责**：SDK 入口，导出核心类，简化用户导入。

**导出内容**：

```python
# 核心类
from .client import Client
from .router import Router

# 数据模型
from .models.common import ProviderConfig, ModelInfo
from .models.chat import ChatMessage, ChatCompletion, ChatChoice, ChatUsage
from .models.image import ImageGenerationResult, ImageData
from .models.video import VideoTask, VideoStatus

# 错误类型
from .core.errors import (
    AGNError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    ModelNotFoundError,
    APIError,
    TimeoutError,
)

# 配置工具
from .core.config import load_env

__version__ = "1.0.0"
__all__ = [
    "Client",
    "Router",
    "ProviderConfig",
    "ModelInfo",
    "ChatMessage",
    "ChatCompletion",
    "ChatChoice",
    "ChatUsage",
    "ImageGenerationResult",
    "ImageData",
    "VideoTask",
    "VideoStatus",
    "AGNError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "ModelNotFoundError",
    "APIError",
    "TimeoutError",
    "load_env",
    "__version__",
]
```

### 2.2 客户端文件

#### `agn/client.py`

**职责**：统一客户端，用户使用 SDK 的唯一入口。

**核心内容**：
- `Client` 类定义
- 所有对外方法（`chat`, `image_generate`, `video_create`, `video_poll`, `list_models`）
- 内部调用适配器执行实际请求

### 2.3 路由器文件

#### `agn/router.py`

**职责**：多 Provider 路由，支持自动选择、负载均衡、Fallback。

**核心内容**：
- `Router` 类定义
- 路由策略实现
- 模型到 Provider 的映射

### 2.4 适配器层

#### `agn/adapters/base.py`

**职责**：适配器基类，定义标准接口。

**核心内容**：
- `BaseAdapter` 抽象基类
- 所有必须实现的抽象方法
- 能力声明机制

#### `agn/adapters/factory.py`

**职责**：适配器工厂，根据 provider_type 创建适配器实例。

**核心内容**：
- `AdapterFactory` 类
- 注册表机制
- 创建和注册方法

#### `agn/adapters/agnes.py`

**职责**：Agnes AI 适配器实现。

**核心内容**：
- `AgnesAdapter` 类
- 实现所有抽象方法（chat, image_generate, video_create, video_poll, list_models）
- 参数转换和响应归一化

### 2.5 核心层

#### `agn/core/http_client.py`

**职责**：统一 HTTP 客户端，管理连接池和重试。

**核心内容**：
- `AsyncHttpClient` 类
- 基于 httpx.AsyncClient 的封装
- 自动重试机制

#### `agn/core/retry.py`

**职责**：重试机制封装。

**核心内容**：
- `retry_decorator` 装饰器
- 指数退避策略
- 可配置重试条件

#### `agn/core/errors.py`

**职责**：错误定义与映射。

**核心内容**：
- 标准错误类型定义
- 错误映射函数

#### `agn/core/config.py`

**职责**：配置管理。

**核心内容**：
- `Config` 类
- 环境变量加载
- 配置优先级处理

#### `agn/core/utils.py`

**职责**：工具函数。

**核心内容**：
- 通用工具函数
- 图像 URL/base64 归一化
- 时间戳处理

### 2.6 数据模型

#### `agn/models/common.py`

**职责**：通用数据结构。

**核心内容**：
- `ProviderConfig` - Provider 配置
- `ModelInfo` - 模型信息

#### `agn/models/chat.py`

**职责**：文本对话相关模型。

**核心内容**：
- `ChatMessage` - 对话消息
- `ChatCompletion` - 对话完成结果
- `ChatChoice` - 对话选项
- `ChatUsage` - 使用统计

#### `agn/models/image.py`

**职责**：图像生成相关模型。

**核心内容**：
- `ImageGenerationResult` - 图像生成结果
- `ImageData` - 图像数据

#### `agn/models/video.py`

**职责**：视频生成相关模型。

**核心内容**：
- `VideoTask` - 视频任务信息
- `VideoStatus` - 视频任务状态

---

## 3. 开发计划

### 3.1 阶段划分

| 阶段 | 版本 | 时间 | 目标 |
|------|------|------|------|
| **Phase 1** | V0.1 | 1周 | 核心架构搭建，BaseAdapter + 数据模型 |
| **Phase 2** | V0.2 | 1周 | 核心层实现（HTTP 客户端、重试、错误处理） |
| **Phase 3** | V0.3 | 1周 | Client 客户端实现 |
| **Phase 4** | V1.0 | 2周 | Agnes AI 适配器 + 测试 + 文档 |
| **Phase 5** | V1.1 | 1周 | OpenAI 适配器 + Azure 适配器 |
| **Phase 6** | V1.2 | 2周 | Runway 适配器 + Pika 适配器 |
| **Phase 7** | V1.3 | 2周 | Stability AI 适配器 + 中文模型适配器 |
| **Phase 8** | V1.4 | 2周 | Router 路由器 + 性能优化 |

### 3.2 Phase 1：核心架构搭建（V0.1）

**时间**：1周

**任务**：

| 任务 | 描述 | 负责人 |
|------|------|--------|
| 创建项目结构 | 创建所有目录和基础文件 | 开发 |
| 定义适配器基类 | 实现 `BaseAdapter` 抽象基类 | 开发 |
| 定义数据模型 | 实现所有 Pydantic 模型 | 开发 |
| 定义错误类型 | 实现标准错误类型 | 开发 |

**交付物**：
- `agn/adapters/base.py`
- `agn/models/common.py`
- `agn/models/chat.py`
- `agn/models/image.py`
- `agn/models/video.py`
- `agn/core/errors.py`

### 3.3 Phase 2：核心层实现（V0.2）

**时间**：1周

**任务**：

| 任务 | 描述 | 负责人 |
|------|------|--------|
| 实现 HTTP 客户端 | 封装 httpx.AsyncClient，支持连接池和重试 | 开发 |
| 实现重试机制 | 封装 tenacity，支持指数退避 | 开发 |
| 实现配置管理 | 支持环境变量、.env 文件、代码配置 | 开发 |
| 实现工具函数 | 图像归一化、时间戳处理等 | 开发 |

**交付物**：
- `agn/core/http_client.py`
- `agn/core/retry.py`
- `agn/core/config.py`
- `agn/core/utils.py`

### 3.4 Phase 3：Client 客户端实现（V0.3）

**时间**：1周

**任务**：

| 任务 | 描述 | 负责人 |
|------|------|--------|
| 实现 Client 类 | 统一对外接口 | 开发 |
| 实现适配器工厂 | 注册表机制 + 创建方法 | 开发 |
| 实现入口文件 | 导出核心类 | 开发 |

**交付物**：
- `agn/client.py`
- `agn/adapters/factory.py`
- `agn/__init__.py`

### 3.5 Phase 4：Agnes AI 适配器（V1.0）

**时间**：2周

**任务**：

| 任务 | 描述 | 负责人 |
|------|------|--------|
| 实现 AgnesAdapter | 完成所有方法实现 | 开发 |
| 编写单元测试 | 测试所有方法 | 开发 |
| 编写文档 | API 文档、使用示例 | 开发 |
| 完善项目配置 | pyproject.toml、README | 开发 |

**交付物**：
- `agn/adapters/agnes.py`
- `tests/test_adapters/test_agnes.py`
- 完整文档
- `pyproject.toml`

### 3.6 Phase 5：OpenAI + Azure 适配器（V1.1）

**时间**：1周

**任务**：

| 任务 | 描述 | 负责人 |
|------|------|--------|
| 实现 OpenAIAdapter | 文本对话 + 图像生成 | 开发 |
| 实现 AzureAdapter | 基于 OpenAIAdapter 扩展 | 开发 |
| 编写测试 | 单元测试 | 开发 |

**交付物**：
- `agn/adapters/openai.py`
- `agn/adapters/azure.py`

### 3.7 Phase 6：视频适配器扩展（V1.2）

**时间**：2周

**任务**：

| 任务 | 描述 | 负责人 |
|------|------|--------|
| 实现 RunwayAdapter | 视频生成 | 开发 |
| 实现 PikaAdapter | 视频生成 | 开发 |
| 编写测试 | 单元测试 | 开发 |

**交付物**：
- `agn/adapters/runway.py`
- `agn/adapters/pika.py`

### 3.8 Phase 7：图像 + 中文模型（V1.3）

**时间**：2周

**任务**：

| 任务 | 描述 | 负责人 |
|------|------|--------|
| 实现 StabilityAdapter | 图像生成 | 开发 |
| 实现 QianfanAdapter | 文本对话 + 图像 + 视频 | 开发 |
| 实现 TongyiAdapter | 文本对话 + 图像 + 视频 | 开发 |
| 编写测试 | 单元测试 | 开发 |

**交付物**：
- `agn/adapters/stability.py`
- `agn/adapters/qianfan.py`
- `agn/adapters/tongyi.py`

### 3.9 Phase 8：Router + 性能优化（V1.4）

**时间**：2周

**任务**：

| 任务 | 描述 | 负责人 |
|------|------|--------|
| 实现 Router | 多 Provider 路由、负载均衡、Fallback | 开发 |
| 性能优化 | 连接池、缓存、并发限制 | 开发 |
| 集成测试 | 测试 Router 和完整流程 | 开发 |
| 文档完善 | 完整文档和示例 | 开发 |

**交付物**：
- `agn/router.py`
- 性能优化代码
- 集成测试

---

## 4. 编码规范

### 4.1 Python 版本

- Python 3.10+
- 使用 PEP 604 类型提示语法（`str | None` 而不是 `Optional[str]`）

### 4.2 代码格式化

- 使用 `black` 进行代码格式化
- 行宽限制：88 字符
- 导入顺序：标准库 → 第三方库 → 项目内部

### 4.3 类型检查

- 使用 `mypy` 进行类型检查
- 所有函数和方法必须有完整的类型提示
- Pydantic 模型使用 `model_config` 配置

### 4.4 测试规范

- 使用 `pytest` 进行单元测试
- 使用 `pytest-asyncio` 进行异步测试
- 测试覆盖率目标：≥ 80%
- 测试文件放在 `tests/` 目录下

### 4.5 日志规范

- 使用 Python 标准 `logging` 模块
- 日志级别：DEBUG、INFO、WARNING、ERROR
- 日志格式：`[%(asctime)s] %(levelname)s %(name)s: %(message)s`

---

## 5. 发布流程

### 5.1 版本号规范

使用语义化版本（Semantic Versioning）：

```
MAJOR.MINOR.PATCH
```

- **MAJOR**：不兼容的 API 变更
- **MINOR**：向后兼容的功能新增
- **PATCH**：向后兼容的 bug 修复

### 5.2 发布步骤

1. 更新 `CHANGELOG.md`
2. 更新 `pyproject.toml` 中的版本号
3. 更新 `agn/__init__.py` 中的 `__version__`
4. 运行测试确保通过
5. 构建包：`flit build`
6. 发布到 PyPI：`flit publish`

### 5.3 开发版本

使用 `-dev` 后缀标识开发版本：

```
1.0.0-dev.1
1.0.0-dev.2
```

---

## 6. 依赖管理

### 6.1 核心依赖

```toml
[project.dependencies]
httpx = ">=0.27.0"
pydantic = ">=2.0.0"
python-dotenv = ">=1.0.0"
tenacity = ">=8.0.0"
async-timeout = ">=4.0.0"
```

### 6.2 开发依赖

```toml
[project.group.dependencies.dev]
pytest = ">=7.0.0"
pytest-asyncio = ">=0.23.0"
ruff = ">=0.1.0"
mypy = ">=1.0.0"
black = ">=23.0.0"
flit = ">=3.0.0"
```

---

## 7. 项目配置文件

### 7.1 pyproject.toml 关键配置

```toml
[project]
name = "agn-sdk"
version = "1.0.0"
description = "多模型统一接口 SDK"
authors = ["Your Name <your@email.com>"]
license = "MIT"
readme = "README.md"
requires-python = ">=3.10"
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

[project.urls]
Homepage = "https://github.com/your-org/agn-sdk"
Repository = "https://github.com/your-org/agn-sdk"

[tool.flit.module]
name = "agn"

[tool.flit.sdist]
include = ["agn/", "docs/", "examples/", "tests/", "README.md", "CHANGELOG.md"]
exclude = ["*.pyc", "__pycache__", ".git"]

[tool.black]
line-length = 88
target-version = ["py310"]

[tool.mypy]
python_version = "3.10"
disallow_untyped_defs = true
disallow_incomplete_defs = true
warn_redundant_casts = true
warn_unused_configs = true
```

### 7.2 .env.example

```bash
# Agnes AI
AGN_AGNES_API_KEY=your-agnes-api-key
AGN_AGNES_BASE_URL=https://api.agnes.ai/v1

# OpenAI
AGN_OPENAI_API_KEY=your-openai-api-key

# Azure OpenAI
AGN_AZURE_API_KEY=your-azure-api-key
AGN_AZURE_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment

# Runway
AGN_RUNWAY_API_KEY=your-runway-api-key

# Stability AI
AGN_STABILITY_API_KEY=your-stability-api-key

# 百度千帆
AGN_QIANFAN_API_KEY=your-qianfan-api-key
AGN_QIANFAN_SECRET_KEY=your-qianfan-secret-key

# 阿里通义
AGN_TONGYI_API_KEY=your-tongyi-api-key
```

---

## 8. 开发环境搭建

### 8.1 安装依赖

```bash
# 克隆项目
git clone https://github.com/your-org/agn-sdk.git
cd agn-sdk

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装开发依赖
pip install -e ".[dev]"

# 安装 pre-commit（可选）
pip install pre-commit
pre-commit install
```

### 8.2 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_client.py

# 运行测试并生成覆盖率报告
pytest --cov=agn --cov-report=html

# 运行异步测试
pytest tests/test_adapters/test_agnes.py -v
```

### 8.3 代码检查

```bash
# 运行 ruff 代码检查
ruff check agn/

# 运行 mypy 类型检查
mypy agn/

# 运行 black 代码格式化
black agn/
```

### 8.4 构建包

```bash
# 构建源代码包和 wheel
flit build

# 安装到本地
flit install --symlink
```

---

## 9. 贡献指南

### 9.1 提交规范

使用 Conventional Commits 规范：

```
<type>(<scope>): <description>

<body>

<footer>
```

**类型**：
- `feat`：新功能
- `fix`：bug 修复
- `docs`：文档更新
- `style`：代码格式化
- `refactor`：重构
- `test`：测试更新
- `chore`：构建/工具更新

**示例**：

```
feat(adapters): add OpenAI adapter

- Implement OpenAIAdapter for chat and image generation
- Add support for GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo
- Add support for DALL-E 3 image generation
```

### 9.2 分支策略

- `main`：主分支，稳定版本
- `develop`：开发分支，最新功能
- `feature/xxx`：功能分支
- `fix/xxx`：bug 修复分支
- `release/xxx`：发布分支

### 9.3 PR 流程

1. Fork 项目
2. 创建分支
3. 提交代码
4. 运行测试确保通过
5. 创建 PR
6. 代码审查
7. 合并到 develop

---

## 10. 许可证

MIT License

```
MIT License

Copyright (c) 2025 Your Organization

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
