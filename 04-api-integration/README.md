# API 集成

学习如何集成和使用第三方 API。

## OpenAI API

### 文件
- `openai_demo.py` - OpenAI API 使用示例
- `.env.example` - 环境变量配置示例
- `.env` - 实际配置文件（不会被提交到 Git）

### 快速开始

#### 1. 配置环境变量
```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
# OPENAI_API_KEY=your-api-key-here
# OPENAI_BASE_URL=https://api-xmodel.rongcloud.cn/v1
```

#### 2. 安装依赖
```bash
pip install openai python-dotenv
```

#### 3. 运行示例
```bash
python openai_demo.py
```

### 内容

#### 基础配置
使用 OpenAI SDK 1.0+ 版本的新语法，配置从环境变量读取：

```python
import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
)
```

#### 聊天完成
```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

### 常见模型
- `gpt-4` - GPT-4 模型
- `gpt-3.5-turbo` - GPT-3.5 Turbo
- `claude-3-opus-20240229` - Claude 3 Opus (需要兼容端点)
- `claude-3-sonnet-20240229` - Claude 3 Sonnet

### 错误处理
```python
from openai import OpenAI, BadRequestError, AuthenticationError

try:
    response = client.chat.completions.create(...)
except AuthenticationError:
    print("API key 无效")
except BadRequestError as e:
    print(f"请求错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

## 环境要求

```bash
# 安装 OpenAI SDK 和 python-dotenv
pip install openai python-dotenv

# 如果使用旧版本需要升级
pip install --upgrade openai
```

## 环境变量配置

### 方法 1: 使用 .env 文件（推荐）
```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api-xmodel.rongcloud.cn/v1
```

### 方法 2: 系统环境变量
```bash
# Linux/Mac
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api-xmodel.rongcloud.cn/v1"

# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key"
$env:OPENAI_BASE_URL="https://api-xmodel.rongcloud.cn/v1"
```

## API 迁移

如果你的代码使用旧版 OpenAI API (< 1.0.0)，需要迁移：

### 旧版 (< 1.0.0)
```python
import openai
openai.api_key = "sk-..."
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[...]
)
```

### 新版 (>= 1.0.0)
```python
from openai import OpenAI
client = OpenAI(api_key="sk-...")
response = client.chat.completions.create(
    model="gpt-4",
    messages=[...]
)
```

### 自动迁移工具
```bash
openai migrate
```

## 使用第三方端点

一些第三方服务提供 OpenAI 兼容的 API，只需修改 `base_url`：

```python
client = OpenAI(
    api_key="your-key",
    base_url="https://your-service.com/v1"
)
```

## 自定义 HTTP Transport

### 什么是 Transport？

OpenAI SDK 底层使用 `httpx` 库发送请求。`Transport` 是 httpx 的网络层抽象，负责把一个 `httpx.Request` 对象真正发送出去并返回响应。

```
你的代码
  → OpenAI SDK（构建请求、解析响应）
    → httpx.Client（连接管理、重试）
      → Transport（真正的网络 I/O）
        → 服务器
```

通过替换默认 Transport，可以在请求发出前拦截并修改它——比如过滤请求头、打印调试信息、模拟响应等。

### 典型场景：第三方中转服务拦截 SDK 请求头

OpenAI SDK 会自动在每个请求里附加一批特征头：

```
user-agent: OpenAI/Python 1.99.9
x-stainless-lang: python
x-stainless-os: MacOS
x-stainless-arch: arm64
...
```

部分第三方中转服务会识别这些头并拒绝请求（返回 403）。解决方案是自定义 Transport，在发送前把这些头过滤掉。

### 如何排查被拦截的请求头

先用调试 Transport 打印出 SDK 实际发出的所有头：

```python
import httpx
from openai import OpenAI

class DebugTransport(httpx.BaseTransport):
    def __init__(self):
        self._transport = httpx.HTTPTransport()

    def handle_request(self, request):
        print("=== 实际发出的请求头 ===")
        for k, v in request.headers.items():
            print(f"  {k}: {v}")
        return self._transport.handle_request(request)

client = OpenAI(
    api_key="...",
    base_url="...",
    http_client=httpx.Client(transport=DebugTransport())
)
```

然后用 `requests` 直接调用 API，逐一对比两者的头，找出哪个触发了拦截：

```python
import requests

# 只带最基础的头，看能否通过
r = requests.post(f"{base_url}/chat/completions",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    json={"model": "gpt-5.4", "messages": [{"role": "user", "content": "hi"}]}
)
print(r.status_code)  # 200 = 通过，403 = 被拦

# 加上可疑的头，复现拦截
r2 = requests.post(..., headers={..., "user-agent": "OpenAI/Python 1.99.9"}, ...)
print(r2.status_code)  # 403 → 确认是这个头触发了拦截
```

### 自定义 Transport 过滤请求头

找到被拦截的头之后，写一个过滤 Transport：

```python
import httpx
from openai import OpenAI

BLOCKED_HEADERS = {
    "user-agent",
    "x-stainless-lang",
    "x-stainless-package-version",
    "x-stainless-os",
    "x-stainless-arch",
    "x-stainless-runtime",
    "x-stainless-runtime-version",
    "x-stainless-async",
    "x-stainless-retry-count",
    "x-stainless-read-timeout",
}

class StripSDKHeadersTransport(httpx.BaseTransport):
    def __init__(self):
        self._transport = httpx.HTTPTransport()

    def handle_request(self, request):
        # 过滤掉被拦截的头，重新构建请求
        filtered = {
            k: v for k, v in request.headers.items()
            if k.lower() not in BLOCKED_HEADERS
        }
        request = httpx.Request(
            method=request.method,
            url=request.url,
            headers=filtered,
            content=request.content,
        )
        return self._transport.handle_request(request)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    http_client=httpx.Client(transport=StripSDKHeadersTransport())
)
```

### 注意事项

- **重新构建 `httpx.Request`**：httpx 的 `Headers` 是只读的，不能直接删除，必须用过滤后的字典创建新的 `Request` 对象。
- **`content` vs `stream`**：重建请求时传 `content=request.content`，这对普通 JSON 请求（已在内存中）是安全的；流式请求（streaming）需要额外处理。
- **这是中转服务的问题**：直接调用 `api.openai.com` 完全不需要这些处理，SDK 的这些头是正常的遥测信息。

## 注意事项

1. **API Key 安全**: 
   - ✅ 使用 `.env` 文件存储（已在 `.gitignore` 中）
   - ✅ 使用环境变量
   - ❌ 不要将 API key 硬编码在代码中
   - ❌ 不要提交 `.env` 文件到 Git

2. **环境变量最佳实践**:
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()  # 加载 .env 文件
   
   api_key = os.getenv("OPENAI_API_KEY")
   if not api_key:
       raise ValueError("请设置 OPENAI_API_KEY 环境变量")
   ```

3. **错误处理**: 始终添加异常处理
4. **模型可用性**: 确认服务端支持你使用的模型
5. **速率限制**: 注意 API 调用频率限制

## 更多资源

- [OpenAI Python SDK 文档](https://github.com/openai/openai-python)
- [OpenAI API 参考](https://platform.openai.com/docs/api-reference)
- [迁移指南](https://github.com/openai/openai-python/discussions/742)
