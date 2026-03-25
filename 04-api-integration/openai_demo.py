import os
import httpx
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 文件（从当前目录或项目根目录）
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()


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
    """过滤掉 OpenAI SDK 自动添加的特征请求头，避免被中转服务识别拦截。"""
    def __init__(self):
        self._transport = httpx.HTTPTransport()

    def handle_request(self, request):
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

response = client.chat.completions.create(
    model="gpt-5.4",
    messages=[{"role": "user", "content": "你是谁？你可以做啥?"}]
)

print(response.choices[0].message.content)