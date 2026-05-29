class Test:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello, {self.name}!"
    
    def __getattr__(self, name):
        print(f"进入 __getattr__，属性 {name} 不存在")
        return f"默认值:{name}"


import json
import os
import sys
from pathlib import Path
from urllib import error, request


TOOLS_DIR = Path(__file__).resolve().parent / "06-tools-and-tests"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from markdown_retrieval import hybrid_score, lexical_overlap_score, load_docs


def call_claude(prompt: str) -> str:
    base_url = os.environ["MAAS_BASE_URL"].rstrip("/")
    api_key = os.environ["MAAS_API_KEY"]

    payload = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }

    req = request.Request(
        url=f"{base_url}/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"API request failed: HTTP {exc.code} {body}") from exc

    return result["content"][0]["text"]


if __name__ == "__main__":
    answer = call_claude("请用一句话介绍 Python 的 __getattr__。")
    print(answer)
