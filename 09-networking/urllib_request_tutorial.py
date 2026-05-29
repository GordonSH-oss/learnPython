"""Learn urllib.request by calling a Claude-compatible Messages API.

Required environment variables:
    MAAS_BASE_URL=https://maas.rongcloud.net
    MAAS_API_KEY=your-api-key

Run:
    python 09-networking/urllib_request_tutorial.py "请用一句话解释 urllib.request"
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any
from urllib import error, request


DEFAULT_MODEL = "claude-sonnet-4-6"


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def post_json(
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    timeout: int = 60,
) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    req = request.Request(
        url=url,
        data=data,
        headers=headers,
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout) as resp:
            raw_body = resp.read().decode("utf-8")
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"API request failed: HTTP {exc.code} {body}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Network request failed: {exc.reason}") from exc

    try:
        return json.loads(raw_body)
    except json.JSONDecodeError as exc:
        preview = raw_body[:500]
        raise RuntimeError(f"Response is not valid JSON: {preview}") from exc


def call_claude(prompt: str, model: str = DEFAULT_MODEL) -> str:
    base_url = require_env("MAAS_BASE_URL").rstrip("/")
    api_key = require_env("MAAS_API_KEY")

    payload = {
        "model": model,
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }

    result = post_json(
        url=f"{base_url}/v1/messages",
        payload=payload,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )

    text_blocks = [
        item["text"]
        for item in result.get("content", [])
        if item.get("type") == "text" and "text" in item
    ]
    return "\n".join(text_blocks)


def main() -> int:
    prompt = " ".join(sys.argv[1:]) or "请用一句话解释 urllib.request.Request。"

    try:
        print(call_claude(prompt))
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
