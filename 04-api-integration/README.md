# API 集成

学习如何集成和使用第三方 API。

## OpenAI API

### 文件
- `openai_demo.py` - OpenAI API 使用示例

### 内容

#### 基础配置
使用 OpenAI SDK 1.0+ 版本的新语法：

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-api-key",
    base_url="https://api.openai.com/v1"  # 或其他兼容的 API 端点
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
# 安装 OpenAI SDK
pip install openai

# 如果使用旧版本需要升级
pip install --upgrade openai
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

1. **API Key 安全**: 不要将 API key 提交到代码仓库
2. **使用环境变量**:
   ```python
   import os
   client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
   ```
3. **错误处理**: 始终添加异常处理
4. **模型可用性**: 确认服务端支持你使用的模型
5. **速率限制**: 注意 API 调用频率限制

## 更多资源

- [OpenAI Python SDK 文档](https://github.com/openai/openai-python)
- [OpenAI API 参考](https://platform.openai.com/docs/api-reference)
- [迁移指南](https://github.com/openai/openai-python/discussions/742)
