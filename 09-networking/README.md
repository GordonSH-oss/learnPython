# 网络请求：使用 urllib.request 调用 HTTP API

本章学习 Python 标准库里的 `urllib.request`。它不需要安装第三方包，适合理解 HTTP 请求到底是怎么发出去的。

如果后续使用 `requests`、`httpx`、OpenAI SDK 或其他 SDK，它们底层也离不开同一套概念：URL、请求方法、请求头、请求体、响应状态码、响应体和异常处理。

## 学习目标

学完本章后，你应该能做到：

- 看懂一次 HTTP 请求由哪些部分组成。
- 使用 `urllib.request.Request` 构造 GET 和 POST 请求。
- 把 Python 字典序列化成 JSON 请求体。
- 从环境变量读取 API key 和 base URL。
- 调用 MaaS Claude Messages API。
- 区分 `HTTPError`、`URLError` 和超时问题。

## 先建立心智模型

一次 HTTP 调用可以拆成 4 个输入和 1 个输出：

| 部分 | 作用 | Python 中的位置 |
| --- | --- | --- |
| URL | 要访问哪个服务和路径 | `Request(url=...)` |
| method | 用 GET、POST 还是其他方法 | `Request(method="POST")` |
| headers | 请求元数据，例如鉴权和内容类型 | `Request(headers={...})` |
| body | 请求体，例如 JSON 数据 | `Request(data=bytes)` |
| response | 服务端返回的状态、头和正文 | `urlopen(req)` 返回的对象 |

数据流大致如下：

```text
Python dict
  -> json.dumps(...)
  -> UTF-8 bytes
  -> urllib.request.Request
  -> urllib.request.urlopen
  -> response.read()
  -> json.loads(...)
  -> Python dict
```

关键点：HTTP 请求体不是 Python 字典，也不是字符串，而是字节。调用 JSON API 时，通常需要先 `json.dumps(payload).encode("utf-8")`。

## 最小 GET 请求

GET 请求通常不带请求体，适合读取公开资源：

```python
from urllib import request

with request.urlopen("https://example.com", timeout=10) as resp:
    body = resp.read().decode("utf-8")
    print(resp.status)
    print(body[:200])
```

这里有两个细节：

- `timeout=10` 表示最多等待 10 秒，避免程序一直卡住。
- `resp.read()` 读出来的是 bytes，需要 `decode("utf-8")` 变成字符串。

## 使用 Request 对象

真实 API 往往需要请求头、请求方法和请求体，所以会显式创建 `Request`：

```python
from urllib import request

req = request.Request(
    url="https://api.example.com/v1/messages",
    data=b'{"message":"hello"}',
    headers={
        "content-type": "application/json",
        "authorization": "Bearer your-token",
    },
    method="POST",
)

with request.urlopen(req, timeout=30) as resp:
    print(resp.status)
    print(resp.read().decode("utf-8"))
```

`Request` 的核心参数：

- `url`: 完整接口地址。
- `data`: 请求体，必须是 bytes。传了 `data` 通常就是 POST，但建议显式写 `method="POST"`。
- `headers`: 请求头，用来传鉴权、内容类型、版本号等信息。
- `method`: 请求方法，例如 `GET`、`POST`、`PUT`、`DELETE`。

## POST JSON 的标准写法

调用 JSON API 时，推荐把“构造请求”和“处理响应”拆清楚：

```python
import json
from urllib import request

payload = {
    "model": "claude-sonnet-4-6",
    "max_tokens": 1024,
    "messages": [
        {"role": "user", "content": "hello"}
    ],
}

req = request.Request(
    url="https://maas.rongcloud.net/v1/messages",
    data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
    headers={
        "x-api-key": "不要硬编码真实 key",
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    },
    method="POST",
)

with request.urlopen(req, timeout=60) as resp:
    result = json.loads(resp.read().decode("utf-8"))

print(result["content"][0]["text"])
```

注意不要把真实 API key 写进代码。应该从环境变量读取。

## 调用 MaaS Claude Messages API

本目录提供了一个可运行示例：

- `urllib_request_tutorial.py`

它读取两个环境变量：

```bash
export MAAS_BASE_URL="https://maas.rongcloud.net"
export MAAS_API_KEY="你的 API key"
```

运行：

```bash
python 09-networking/urllib_request_tutorial.py "请用一句话解释 urllib.request.Request"
```

示例代码的核心调用路径：

```python
base_url = os.environ["MAAS_BASE_URL"].rstrip("/")
api_key = os.environ["MAAS_API_KEY"]

url = f"{base_url}/v1/messages"
headers = {
    "x-api-key": api_key,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}
```

这里用 `rstrip("/")` 是为了避免环境变量写成 `https://maas.rongcloud.net/` 时拼出 `//v1/messages`。

## 错误处理

`urllib.request` 常见异常主要有两类：

| 异常 | 代表什么 | 常见原因 |
| --- | --- | --- |
| `HTTPError` | 服务端返回了 4xx 或 5xx | key 错、模型名错、参数格式错、服务端错误 |
| `URLError` | 请求没有正常到达服务端 | 域名错误、网络断开、TLS 问题、超时 |
| `JSONDecodeError` | 响应正文不是合法 JSON | URL 路径错、服务端返回 HTML 错误页、网关返回非 JSON |

`HTTPError` 很重要的一点是：它里面通常还带着服务端返回的错误正文，可以读出来帮助排查：

```python
from urllib import error

try:
    ...
except error.HTTPError as exc:
    body = exc.read().decode("utf-8", errors="replace")
    raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
```

如果只打印 `HTTP 400`，通常看不出是哪个参数错了。把 body 打出来，才能看到服务端的具体错误信息。

## 调试清单

请求失败时按这个顺序查：

1. `MAAS_BASE_URL` 是否包含协议，例如 `https://maas.rongcloud.net`。
2. URL 是否拼成了正确路径，例如 `/v1/messages`。
3. API key 是否从环境变量读到了，代码里不要打印完整 key。
4. 请求头是否包含 `x-api-key`、`anthropic-version`、`content-type`。
5. `payload` 是否能被 `json.dumps` 序列化。
6. 请求体是否是 bytes，而不是 dict 或 str。
7. 是否设置了合理的 timeout。
8. `HTTPError` 的 body 是否包含更具体的错误原因。

## 练习

1. 把 `max_tokens` 改成 `32`，观察返回内容长度变化。
2. 把模型名故意写错，看看 `HTTPError` 的错误正文。
3. 把 `MAAS_BASE_URL` 末尾加一个 `/`，确认 `rstrip("/")` 的效果。
4. 增加一个 `temperature` 参数，观察模型输出是否更发散。
5. 写一个 `get_json(url)` 函数，封装 GET 请求并返回 Python 字典。

## 和 requests 库的区别

`requests` 是第三方库，写法更简洁：

```python
import requests

resp = requests.post(url, headers=headers, json=payload, timeout=60)
resp.raise_for_status()
result = resp.json()
```

但学习阶段建议先掌握 `urllib.request`，因为它能暴露更多 HTTP 的真实细节：请求体必须编码、响应体需要解码、错误正文需要手动读取。理解这些之后，再用 `requests` 或 `httpx` 会更容易判断问题出在哪里。
