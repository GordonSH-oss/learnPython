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
