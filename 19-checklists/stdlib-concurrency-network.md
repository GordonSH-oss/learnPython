# 标准库：并发与网络

## `threading`、`multiprocessing`、`concurrent.futures`

- [ ] 我能根据 CPU 密集或 I/O 密集选择线程、进程或线程池。
- [ ] 我会使用 `Lock`、`Event`、`ThreadPoolExecutor`、`ProcessPoolExecutor` 和 `Future`。

```python
from concurrent.futures import ThreadPoolExecutor

def fetch(n: int) -> int:
    return n * 2

with ThreadPoolExecutor(max_workers=4) as pool:
    print(list(pool.map(fetch, range(4))))
```

常见坑：共享可变状态需要同步；线程不能绕过 CPython 的 CPU 密集 GIL 限制；进程任务要可序列化；退出时要等待或取消任务。

自查：为什么 I/O 密集任务适合线程？进程池函数为什么通常要定义在模块顶层？

练习：将一个顺序的慢 I/O 模拟程序改为线程池，并比较耗时；再说明 CPU 版本为何应换进程池。

仓库关联：[并发学习指南](../11-concurrency/README.md)、[asyncio pipeline](../11-concurrency/asyncio_pipeline.py)。

## `asyncio`

- [ ] 我理解协程、事件循环、任务和 `await` 的关系。
- [ ] 我会使用 `async def`、`create_task`、`gather`、超时和取消。

```python
import asyncio

async def work(n: int) -> int:
    await asyncio.sleep(0.01)
    return n * 2

async def main() -> None:
    print(await asyncio.gather(*(work(n) for n in range(3))))

asyncio.run(main())
```

常见坑：协程函数调用后不会自动运行；在事件循环中执行阻塞 I/O 会卡住所有任务；取消必须让资源清理代码执行。

自查：`await` 让出了什么控制权？什么时候用 `to_thread`？

练习：给并发任务添加超时和异常处理，并确保任务取消后不会留下未回收资源。

仓库关联：[asyncio pipeline](../11-concurrency/asyncio_pipeline.py)。

## `urllib` 与 `http`

- [ ] 我知道标准库可以构造 URL、发送请求并解析响应。
- [ ] 我会使用 `urllib.request`、`urllib.parse`、`urllib.error` 和 `http.HTTPStatus`。

```python
from urllib.parse import urlencode, urljoin
from urllib.request import Request

url = urljoin("https://example.com/", "search?" + urlencode({"q": "python"}))
request = Request(url, headers={"Accept": "application/json"})
print(request.full_url)
```

常见坑：生产请求要设置超时、处理 HTTP 错误和关闭响应；URL 参数应使用 `urlencode`；不要把证书验证关闭当作通用修复。

自查：`urllib.parse` 解决了什么编码问题？HTTP 4xx 和网络连接失败应如何区分？

练习：为一个 GET 请求增加超时、状态码检查和 JSON 解码失败处理。

仓库关联：[urllib.request 教程](../09-networking/urllib_request_tutorial.py)。

