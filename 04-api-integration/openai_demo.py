import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 文件（从当前目录或项目根目录）
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # 尝试从项目根目录加载
    load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

response = client.chat.completions.create(
    model="claude-4.5-sonnet",  # 使用更常见的模型，或者咨询 API 提供商支持哪些模型
    messages=[{"role": "user", "content": "你是谁？你可以做啥?"}]
)

print(response.choices[0].message.content)