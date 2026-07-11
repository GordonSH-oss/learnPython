"""http.server 入门教程：用标准库写一个 JSON HTTP 服务。

本文件既是一篇教程，也是一个可运行示例。它演示 Python 标准库
`http.server` 的基本用法：

1. 创建一个 HTTP 服务。
2. 自定义请求处理器。
3. 处理 GET 请求。
4. 读取 POST 请求体。
5. 返回 JSON 响应。
6. 用多线程方式同时处理多个请求。

运行：

    python 09-networking/http.py

测试 GET：

    curl http://127.0.0.1:8000/api/hello

测试 POST：

    curl -X POST http://127.0.0.1:8000/api/echo \
      -H "Content-Type: application/json" \
      -d '{"name":"Python","topic":"http.server"}'

停止服务：

    按 Ctrl+C

重要提醒：

    这个文件为了配合课程命名为 `http.py`。在真实项目里不建议这样命名，
    因为它会遮蔽 Python 标准库的 `http` 包。更推荐命名为
    `http_server_tutorial.py` 或 `server.py`。

    为了让当前文件名也能运行，下面的 `_import_http_server` 会先临时把
    当前目录从 `sys.path` 中移除，再导入标准库 `http.server`。

学习心智模型：

    浏览器 / curl / 客户端
        -> 建立 TCP 连接
        -> 发送 HTTP 请求行、请求头、请求体
        -> ThreadingHTTPServer 接收请求
        -> 为这个请求创建一个 MyHandler 实例
        -> 调用 do_GET / do_POST 等方法
        -> handler 写入状态码、响应头、响应体
        -> 客户端收到响应

`http.server` 适合学习、调试、本地工具和小型内部服务。它不是生产级 Web
框架：没有路由系统、鉴权中间件、请求校验、限流、TLS 管理等能力。真实业务
服务通常会使用 Flask、FastAPI、Django、aiohttp 或其他框架。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _import_http_server() -> tuple[type[Any], type[Any]]:
    """Import stdlib http.server even though this tutorial file is named http.py."""

    script_dir = Path(__file__).resolve().parent
    removed_paths: list[tuple[int, str]] = []

    for index, item in reversed(list(enumerate(sys.path))):
        path = Path(item or ".").resolve()
        if path == script_dir:
            removed_paths.append((index, item))
            sys.path.pop(index)

    try:
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    finally:
        for index, item in sorted(removed_paths):
            sys.path.insert(index, item)

    return BaseHTTPRequestHandler, ThreadingHTTPServer


BaseHTTPRequestHandler, ThreadingHTTPServer = _import_http_server()


HOST = "127.0.0.1"
PORT = 8000


class MyHandler(BaseHTTPRequestHandler):
    """自定义请求处理器。

    `BaseHTTPRequestHandler` 的核心机制是方法分发：

    - 收到 GET 请求时，框架会调用 `do_GET(self)`。
    - 收到 POST 请求时，框架会调用 `do_POST(self)`。
    - 如果没有实现对应方法，默认会返回 501 Unsupported method。

    每个请求都会创建一个新的 handler 实例，所以这里不要把跨请求共享状态放在
    `self` 上。如果需要共享状态，通常要放在数据库、缓存、队列或专门的服务层。
    """

    server_version = "PythonTutorialHTTP/1.0"

    def send_json(self, data: dict[str, Any], code: int = 200) -> None:
        """统一返回 JSON。

        HTTP 响应由三部分组成：

        1. 状态码，例如 200、400、404。
        2. 响应头，例如 Content-Type。
        3. 响应体，这里是 JSON 字符串编码后的 bytes。

        `wfile` 是一个二进制输出流，所以必须写入 bytes，而不是 str。
        """

        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")

        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json_body(self) -> dict[str, Any] | None:
        """读取并解析 JSON 请求体。

        `BaseHTTPRequestHandler` 不会自动帮我们解析请求体。POST 请求体要从
        `self.rfile` 读取，而读取多少字节要看 `Content-Length` 请求头。
        """

        content_len = int(self.headers.get("Content-Length", 0))
        if content_len == 0:
            return None

        body_raw = self.rfile.read(content_len)
        return json.loads(body_raw.decode("utf-8"))

    def do_GET(self) -> None:
        """处理 GET 请求。

        GET 一般用于读取资源。这个示例只支持一个路径：

        - `/api/hello`: 返回服务状态。
        """

        if self.path == "/api/hello":
            self.send_json(
                {
                    "msg": "多线程服务正常，我就是需要测试测试",
                    "host": HOST,
                    "port": PORT,
                    "path": self.path,
                }
            )
            return

        self.send_json(
            {
                "error": "接口不存在",
                "path": self.path,
                "available_paths": ["/api/hello", "/api/echo"],
            },
            404,
        )

    def do_POST(self) -> None:
        """处理 POST 请求。

        POST 常用于提交数据。这里实现一个 echo 接口：客户端发什么 JSON，
        服务端就把解析后的数据放到 `received` 字段里返回。
        """

        if self.path != "/api/echo":
            self.send_json(
                {
                    "error": "接口不存在",
                    "path": self.path,
                    "available_paths": ["/api/hello", "/api/echo"],
                },
                404,
            )
            return

        try:
            body = self.read_json_body()
        except json.JSONDecodeError as exc:
            self.send_json(
                {
                    "error": "请求体不是合法 JSON",
                    "detail": str(exc),
                },
                400,
            )
            return

        self.send_json(
            {
                "received": body,
                "success": True,
            }
        )

    def log_message(self, format: str, *args: Any) -> None:
        """定制访问日志。

        默认日志会写到 stderr。这里保留日志，但让格式更适合学习观察。
        """

        print(f"{self.client_address[0]} - {format % args}")


def main() -> int:
    """启动 HTTP 服务。

    `ThreadingHTTPServer` 会为每个请求开一个线程。学习阶段可以直观看到：
    一个慢请求不会完全阻塞其他请求。
    """

    server = ThreadingHTTPServer((HOST, PORT), MyHandler)
    print(f"服务启动：http://{HOST}:{PORT}")
    print("可用接口：")
    print(f"  GET  http://{HOST}:{PORT}/api/hello")
    print(f"  POST http://{HOST}:{PORT}/api/echo")
    print("按 Ctrl+C 停止服务")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n正在关闭服务...")
        server.shutdown()
        server.server_close()
        print("服务已关闭")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
