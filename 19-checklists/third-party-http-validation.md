# 第三方库：HTTP 与数据校验

## `requests`

- [ ] 我知道同步 HTTP 客户端、响应状态和连接超时的基本模型。
- [ ] 我会使用 `get`、`params`、`json`、`headers`、`raise_for_status`、`timeout` 和 `Session`。

安装：`python -m pip install requests`（仓库基线 `requests>=2.31`）。

```python
import requests

response = requests.get("https://example.com/api", timeout=5)
response.raise_for_status()
data = response.json()
```

常见坑：不设置超时会让线程永久等待；`raise_for_status()` 不会捕获网络连接异常；大响应应流式读取；敏感头不能写日志。

自查：连接超时与读取超时有什么区别？什么时候使用 `Session`？

练习：实现带重试边界的 GET 客户端，并把 4xx、5xx、网络异常映射为不同错误。

仓库关联：[API 集成](../04-api-integration/resilient_api_client.py)。

## `httpx`

- [ ] 我知道它同时提供同步和异步客户端。
- [ ] 我会使用 `Client`、`AsyncClient`、`timeout`、`raise_for_status` 和 `async with`。

安装：`python -m pip install httpx`（仓库基线 `httpx>=0.27`）。

```python
import httpx

with httpx.Client(timeout=5) as client:
    response = client.get("https://example.com")
    response.raise_for_status()
```

常见坑：异步客户端必须关闭；不要在每次请求中重复创建客户端；`requests` 的同步代码不能直接复制成异步代码。

自查：`httpx.AsyncClient` 为什么适合 asyncio？`Client` 复用连接带来什么收益？

练习：将一个 requests 客户端改写为 AsyncClient，并用 `asyncio.gather` 并发获取三个 URL。

仓库关联：[网络请求](../09-networking/README.md)、[并发](../11-concurrency/README.md)。

## Pydantic

- [ ] 我知道 Pydantic 在外部数据边界执行模型校验和序列化。
- [ ] 我会使用 `BaseModel`、`Field`、嵌套模型、`model_validate`、`model_dump` 和 `ValidationError`。

安装：`python -m pip install pydantic`（仓库基线 `pydantic>=2.0`）。

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str
    age: int = Field(ge=0)

user = User.model_validate({"name": "Ada", "age": 36})
print(user.model_dump())
```

常见坑：模型校验不是权限校验；要区分宽松转换和严格模式；不要把外部模型直接当数据库事务边界。

自查：`model_validate` 与 `model_dump` 的方向是什么？字段约束失败如何向调用方报告？

练习：为外部 API 响应定义嵌套模型，捕获校验错误并输出字段定位。

仓库关联：[Pydantic 指南](../03-python-basics/pydantic/PYDANTIC_GUIDE.md)、[API 集成](../04-api-integration/README.md)。

