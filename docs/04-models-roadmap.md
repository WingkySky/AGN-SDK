# AGN-SDK - 兼容模型规划与路线图

## 1. 模型兼容性总览

### 1.1 支持的能力类型

| 能力类型 | 说明 | 优先级 |
|---------|------|--------|
| **文本对话** | 文本生成、聊天、问答 | P0 |
| **图像生成** | 文本生图、图生图、局部编辑 | P0 |
| **视频生成** | 文本生视频、图生视频、关键帧、多图模式 | P0 |
| **语音合成** | 文本转语音 | P2 |
| **语音识别** | 语音转文本 | P2 |
| **Embedding** | 文本/图像嵌入 | P1 |

### 1.2 模型提供商分类

| 分类 | 提供商 | 特点 |
|------|--------|------|
| **通用 AI** | OpenAI、Azure、Anthropic、Google | 能力全面，API 规范成熟 |
| **图像专用** | Stability AI、Midjourney、Leonardo AI | 图像生成能力强 |
| **视频专用** | Runway、Pika、Sora、可灵、即梦 | 视频生成能力强 |
| **中文模型** | 百度千帆、阿里通义、腾讯混元、字节豆包、智谱 AI | 中文优化，本地化部署 |
| **开源模型** | Hugging Face、Ollama | 自托管，隐私保护 |

---

## 2. 模型兼容路线图

### 2.1 V1.0 版本（核心能力，必做）

| 提供商 | Provider Type | 文本对话 | 图像生成 | 视频生成 | 预估工作量 |
|--------|--------------|---------|---------|---------|-----------|
| **Agnes AI** | `agnes` | ✅ | ✅ | ✅ | 中 |
| **OpenAI** | `openai` | ✅ | ✅ | ❌ | 低 |
| **Azure OpenAI** | `azure` | ✅ | ✅ | ❌ | 低 |

**目标**：完成核心架构，支持 Agnes AI 和 OpenAI 两大主流 Provider，覆盖文本对话和图像生成。

### 2.2 V1.1 版本（视频扩展）

| 提供商 | Provider Type | 文本对话 | 图像生成 | 视频生成 | 预估工作量 |
|--------|--------------|---------|---------|---------|-----------|
| **Runway** | `runway` | ❌ | ❌ | ✅ | 中 |
| **Pika** | `pika` | ❌ | ❌ | ✅ | 中 |
| **可灵** | `kling` | ❌ | ❌ | ✅ | 中 |

**目标**：覆盖主流视频生成平台，支持文本生视频、图生视频、关键帧模式。

### 2.3 V1.2 版本（图像扩展）

| 提供商 | Provider Type | 文本对话 | 图像生成 | 视频生成 | 预估工作量 |
|--------|--------------|---------|---------|---------|-----------|
| **Stability AI** | `stability` | ❌ | ✅ | ❌ | 低 |
| **Midjourney** | `midjourney` | ❌ | ✅ | ❌ | 中 |
| **Leonardo AI** | `leonardo` | ❌ | ✅ | ❌ | 低 |

**目标**：覆盖主流图像生成平台，支持多种风格和分辨率。

### 2.4 V1.3 版本（中文模型）

| 提供商 | Provider Type | 文本对话 | 图像生成 | 视频生成 | 预估工作量 |
|--------|--------------|---------|---------|---------|-----------|
| **百度千帆** | `qianfan` | ✅ | ✅ | ✅ | 中 |
| **阿里通义** | `tongyi` | ✅ | ✅ | ✅ | 中 |
| **腾讯混元** | `hunyuan` | ✅ | ✅ | ✅ | 中 |
| **智谱 AI** | `zhipu` | ✅ | ✅ | ❌ | 低 |

**目标**：支持主流中文大模型，满足国内用户需求。

### 2.5 V1.4 版本（开源模型与其他）

| 提供商 | Provider Type | 文本对话 | 图像生成 | 视频生成 | 预估工作量 |
|--------|--------------|---------|---------|---------|-----------|
| **Ollama** | `ollama` | ✅ | ❌ | ❌ | 低 |
| **Hugging Face** | `hf` | ✅ | ✅ | ❌ | 高 |
| **Anthropic** | `anthropic` | ✅ | ❌ | ❌ | 低 |
| **Google Gemini** | `gemini` | ✅ | ✅ | ❌ | 低 |

**目标**：支持本地部署的开源模型，满足隐私保护需求。

---

## 3. 各 Provider 详细规划

### 3.1 Agnes AI

**Provider Type**: `agnes`

**API Base URL**: `https://api.agnes.ai/v1`

**支持的模型**：

| 模型 ID | 模型名称 | 类型 | 能力 |
|---------|---------|------|------|
| `claude-3-opus` | Claude 3 Opus | chat | 文本对话 |
| `claude-3-sonnet` | Claude 3 Sonnet | chat | 文本对话 |
| `dall-e-3` | DALL-E 3 | image | 文本生图、图生图 |
| `video-gen-1` | Video Gen 1 | video | 文本生视频 |
| `video-gen-2` | Video Gen 2 | video | 文本生视频、关键帧 |

**特殊参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `extra_body` | `Dict` | 透传给底层 API 的额外参数 |

---

### 3.2 OpenAI

**Provider Type**: `openai`

**API Base URL**: `https://api.openai.com/v1`

**支持的模型**：

| 模型 ID | 模型名称 | 类型 | 能力 |
|---------|---------|------|------|
| `gpt-4o` | GPT-4o | chat | 文本对话、多模态理解 |
| `gpt-4-turbo` | GPT-4 Turbo | chat | 文本对话 |
| `gpt-3.5-turbo` | GPT-3.5 Turbo | chat | 文本对话 |
| `dall-e-3` | DALL-E 3 | image | 文本生图、图生图、局部编辑 |

**特殊参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `response_format` | `str` | `"url"` 或 `"b64_json"` |
| `style` | `str` | `"vivid"` 或 `"natural"` |
| `quality` | `str` | `"standard"` 或 `"hd"` |

---

### 3.3 Azure OpenAI

**Provider Type**: `azure`

**API Base URL**: `https://{resource-name}.openai.azure.com/openai/deployments/{deployment-id}`

**支持的模型**：同 OpenAI

**特殊参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `resource_name` | `str` | Azure 资源名称 |
| `deployment_id` | `str` | 部署 ID |
| `api_version` | `str` | API 版本，如 `"2024-02-15-preview"` |

---

### 3.4 Runway

**Provider Type**: `runway`

**API Base URL**: `https://api.runwayml.com/v1`

**支持的模型**：

| 模型 ID | 模型名称 | 类型 | 能力 |
|---------|---------|------|------|
| `gen-3` | Gen-3 Alpha | video | 文本生视频、图生视频 |
| `gen-3-turbo` | Gen-3 Turbo | video | 文本生视频 |
| `inpainting` | Inpainting | video | 视频局部编辑 |

**特殊参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `aspect_ratio` | `str` | 宽高比，如 `"16:9"` |
| `motion` | `str` | 运动风格，如 `"slow"`、`"fast"` |
| `seed` | `int` | 随机种子 |
| `negative_prompt` | `str` | 负面提示词 |

---

### 3.5 Pika

**Provider Type**: `pika`

**API Base URL**: `https://api.pika.art/v1`

**支持的模型**：

| 模型 ID | 模型名称 | 类型 | 能力 |
|---------|---------|------|------|
| `pika-1.0` | Pika 1.0 | video | 文本生视频、图生视频 |

**特殊参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `aspect_ratio` | `str` | 宽高比 |
| `duration` | `int` | 视频时长（秒） |

---

### 3.6 Stability AI

**Provider Type**: `stability`

**API Base URL**: `https://api.stability.ai/v2beta`

**支持的模型**：

| 模型 ID | 模型名称 | 类型 | 能力 |
|---------|---------|------|------|
| `sd3` | Stable Diffusion 3 | image | 文本生图、图生图 |
| `sd3-turbo` | Stable Diffusion 3 Turbo | image | 文本生图 |
| `sdxl` | Stable Diffusion XL | image | 文本生图、图生图 |

**特殊参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `output_format` | `str` | `"png"` 或 `"jpeg"` |
| `output_quality` | `int` | 输出质量 1-100 |
| `num_inference_steps` | `int` | 推理步数 |

---

### 3.7 百度千帆

**Provider Type**: `qianfan`

**API Base URL**: `https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop`

**支持的模型**：

| 模型 ID | 模型名称 | 类型 | 能力 |
|---------|---------|------|------|
| `ernie-4.0` | 文心一言 4.0 | chat | 文本对话 |
| `ernie-vilg-v2` | 文心一格 | image | 文本生图、图生图 |
| `ernie-video` | 文心视频 | video | 文本生视频 |

---

### 3.8 阿里通义

**Provider Type**: `tongyi`

**API Base URL**: `https://dashscope.aliyuncs.com/api/v1`

**支持的模型**：

| 模型 ID | 模型名称 | 类型 | 能力 |
|---------|---------|------|------|
| `qwen-2-max` | 通义千问 2.0 | chat | 文本对话 |
| `qwen-vl-plus` | 通义千问 VL | image | 图像理解、图像生成 |
| `qwen-video` | 通义视频 | video | 文本生视频 |

---

## 4. API Key 配置规范

### 4.1 环境变量命名规范

| Provider | API Key 环境变量 | Base URL 环境变量 |
|----------|-----------------|------------------|
| Agnes AI | `AGN_AGNES_API_KEY` | `AGN_AGNES_BASE_URL` |
| OpenAI | `AGN_OPENAI_API_KEY` | `AGN_OPENAI_BASE_URL` |
| Azure | `AGN_AZURE_API_KEY` | `AGN_AZURE_BASE_URL` |
| Runway | `AGN_RUNWAY_API_KEY` | `AGN_RUNWAY_BASE_URL` |
| Pika | `AGN_PIKA_API_KEY` | `AGN_PIKA_BASE_URL` |
| Stability AI | `AGN_STABILITY_API_KEY` | `AGN_STABILITY_BASE_URL` |
| 百度千帆 | `AGN_QIANFAN_API_KEY` | `AGN_QIANFAN_BASE_URL` |
| 阿里通义 | `AGN_TONGYI_API_KEY` | `AGN_TONGYI_BASE_URL` |

### 4.2 .env 文件示例

```bash
# Agnes AI
AGN_AGNES_API_KEY=your-agnes-api-key
AGN_AGNES_BASE_URL=https://api.agnes.ai/v1

# OpenAI
AGN_OPENAI_API_KEY=your-openai-api-key

# Runway
AGN_RUNWAY_API_KEY=your-runway-api-key

# Stability AI
AGN_STABILITY_API_KEY=your-stability-api-key
```

---

## 5. 模型选择策略

### 5.1 自动选择

SDK 支持根据模型 ID 自动选择对应的 Provider：

```python
from agn import Router

router = Router(providers=[
    {"provider_type": "agnes", "api_key": "key1"},
    {"provider_type": "openai", "api_key": "key2"},
    {"provider_type": "runway", "api_key": "key3"},
])

# 自动选择 Provider（claude-3-opus → Agnes AI）
response = await router.chat(model="claude-3-opus", messages=[{"role": "user", "content": "Hello"}])

# 自动选择 Provider（dall-e-3 → OpenAI）
result = await router.image_generate(model="dall-e-3", prompt="A cat")

# 自动选择 Provider（gen-3 → Runway）
task = await router.video_create(model="gen-3", prompt="A dog running")
```

### 5.2 模型映射表

| 模型 ID | 推荐 Provider | 备选 Provider |
|---------|--------------|--------------|
| `claude-3-opus` | Agnes AI | Anthropic |
| `claude-3-sonnet` | Agnes AI | Anthropic |
| `gpt-4o` | OpenAI | Azure |
| `gpt-4-turbo` | OpenAI | Azure |
| `gpt-3.5-turbo` | OpenAI | Azure |
| `dall-e-3` | OpenAI | Agnes AI |
| `runway-gen3` | Runway | — |
| `pika-1.0` | Pika | — |
| `sd3` | Stability AI | — |
| `ernie-4.0` | 百度千帆 | — |
| `qwen-2-max` | 阿里通义 | — |

---

## 6. 技术挑战与解决方案

### 6.1 API 差异

| 挑战 | 解决方案 |
|------|---------|
| 各 Provider 参数命名不同 | 统一参数名，适配器内部做映射 |
| 响应格式不同 | 统一响应模型，适配器内部做转换 |
| 错误码不同 | 统一错误类型，适配器内部做映射 |

### 6.2 视频生成的异步特性

| 挑战 | 解决方案 |
|------|---------|
| 视频生成耗时久 | 异步任务模式，创建任务 + 轮询状态 |
| 轮询接口不同 | 统一 `video_poll()` 接口 |
| 状态值不同 | 统一状态枚举值 |

### 6.3 流式输出

| 挑战 | 解决方案 |
|------|---------|
| 流式格式不同 | 统一 `AsyncGenerator` 输出格式 |
| SSE 协议差异 | 统一 SSE 解析逻辑 |

### 6.4 认证方式

| 挑战 | 解决方案 |
|------|---------|
| API Key 认证方式不同 | 统一配置 `api_key`，适配器内部处理 |
| OAuth 认证 | 预留 `auth_method` 参数 |
| 多密钥轮换 | 支持密钥列表，自动轮换 |

---

## 7. 性能优化策略

### 7.1 连接池复用

- 使用 httpx.AsyncClient 连接池
- 复用 HTTP 连接，减少握手开销
- 配置合理的最大连接数

### 7.2 缓存策略

- 缓存模型列表（避免频繁调用 `/models`）
- 缓存请求结果（可配置）
- 使用 ETag 或 Last-Modified 进行条件请求

### 7.3 异步并发

- 全异步设计，支持高并发
- 使用 asyncio 事件循环
- 支持并发限制（`max_concurrent`）

### 7.4 重试策略

- 指数退避重试
- 可配置重试次数和延迟
- 区分可重试错误和不可重试错误
