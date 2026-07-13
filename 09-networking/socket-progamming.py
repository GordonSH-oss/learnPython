"""Python Socket 系统教程：从系统调用到应用层协议。

这个文件既是一篇教程，也是一个可以直接运行的实验程序。它不依赖第三方库，
默认只访问本机回环地址，适合用来观察 Socket 的真实行为。

运行方式：

    python 09-networking/socket-progamming.py tcp
    python 09-networking/socket-progamming.py framing
    python 09-networking/socket-progamming.py udp
    python 09-networking/socket-progamming.py nonblocking
    python 09-networking/socket-progamming.py all

可选的外网 HTTP 实验：

    python 09-networking/socket-progamming.py http example.com /

学习路线：

1. TCP 回显：理解 socket、bind、listen、accept、connect、send、recv、close。
2. 消息边界：理解 TCP 是字节流，以及为什么需要应用层 framing。
3. UDP：理解数据报、无连接通信和消息边界。
4. 非阻塞 I/O：理解阻塞、就绪通知和 selectors。
5. 原始 HTTP：理解 HTTP 如何构建在 TCP 字节流之上。

===============================================================================
一、Socket 到底是什么
===============================================================================

Socket 不是“网络连接”本身，而是进程向操作系统申请的一个通信端点。Python 的
``socket.socket(...)`` 最终会进入操作系统内核，创建一个 socket 对象，并返回
一个文件描述符（Windows 上是类似的句柄）。应用程序通过这个描述符读写内核中的
发送缓冲区和接收缓冲区。

    Python 进程                       操作系统内核
    +----------------+               +---------------------------+
    | bytes          | -- send() --> | Socket 发送缓冲区          |
    |                |               | TCP/IP 协议栈 -> 网卡       |
    | bytes          | <-- recv() -- | Socket 接收缓冲区          |
    +----------------+               +---------------------------+

``send`` 成功只表示数据被复制进了本机内核缓冲区，不表示对端应用已经处理数据；
``recv`` 返回的是当前已经到达接收缓冲区的数据，不保证对应某一次 ``send``。

常见创建参数：

* ``AF_INET``：IPv4 地址族，地址写成 ``(host, port)``。
* ``AF_INET6``：IPv6 地址族。
* ``SOCK_STREAM``：有序、可靠、面向字节流，通常对应 TCP。
* ``SOCK_DGRAM``：保留消息边界的数据报，通常对应 UDP。

端口属于传输层的寻址信息。IP 地址定位主机，端口定位主机上的服务。客户端也有
本地端口；调用 ``connect`` 时，如果没有显式 ``bind``，内核会自动选择临时端口。

===============================================================================
二、TCP 的生命周期和底层状态
===============================================================================

服务端：socket -> bind -> listen -> accept -> recv/send -> close
客户端：socket -> connect ----------------> send/recv -> close

``listen`` 创建的是监听 socket。``accept`` 不会把监听 socket 变成客户端连接，
而是返回一个全新的已连接 socket。一个服务通常始终保留监听 socket，并为每个
客户端维护一个连接 socket。

``connect`` 会触发 TCP 三次握手：

    客户端                     服务端
      | -------- SYN ----------> |
      | <----- SYN + ACK ------- |
      | -------- ACK ----------> |
      |      连接已建立           |

握手由内核 TCP 协议栈完成。Python 只会看到 ``connect`` 成功或抛出异常。

关闭通常触发 FIN/ACK 交换。``shutdown(SHUT_WR)`` 是半关闭：告诉对端“我不会再发
数据”，但本端仍可继续接收。``recv`` 返回 ``b""`` 表示对端已经有序关闭发送方向；
它不是“暂时没有数据”。非阻塞 socket 暂时无数据时会抛 ``BlockingIOError``。

===============================================================================
三、最重要的规则：TCP 没有消息边界
===============================================================================

TCP 只提供一条有序字节流。下面两次发送：

    sendall(b"hello")
    sendall(b"world")

接收端可能读成 ``b"helloworld"``，也可能读成 ``b"hel"``、``b"loworld"``。
这不是异常，也不能靠增大 ``recv(4096)`` 修复。应用层必须自己定义边界：

* 固定长度：适合长度恒定的数据结构。
* 分隔符：例如一行以 ``\n`` 结尾；正文包含分隔符时要转义。
* 长度前缀：先发送固定长度的整数，再发送对应长度的正文。
* 自描述协议：例如 HTTP 使用请求行、头、Content-Length 或 chunked encoding。

本教程使用 4 字节大端无符号整数作为长度前缀：

    +----------------------+-------------------+
    | payload length (4B)  | payload (N bytes) |
    +----------------------+-------------------+

网络协议通常使用大端字节序，也叫 network byte order。``struct.pack("!I", n)``
中的 ``!`` 表示网络字节序，``I`` 表示 4 字节无符号整数。

===============================================================================
四、阻塞、并发和背压
===============================================================================

阻塞 socket 的 ``accept``、``connect``、``recv``、``send`` 都可能等待。设置
``settimeout`` 后，超时会抛出 ``socket.timeout``。生产代码不应无限期阻塞。

常见并发模型：

* 每连接一个线程：直观，适合连接数较少、以 I/O 为主的程序。
* 每连接一个进程：隔离强，内存和切换成本较高。
* 非阻塞 socket + selectors：一个线程管理许多连接。
* asyncio：在事件循环上提供协程抽象，底层仍使用非阻塞 I/O 和就绪通知。

发送缓冲区满时，阻塞 ``send`` 会等待，非阻塞 ``send`` 可能只写一部分甚至抛出
``BlockingIOError``。这种“生产速度超过消费速度”的现象叫背压。因此通用代码应
使用 ``sendall``，或在非阻塞模式下维护待发送缓冲区并处理部分写入。

===============================================================================
五、TCP 与 UDP 对比
===============================================================================

TCP 提供可靠、有序、去重的字节流，但需要连接状态和握手。UDP 不建立连接，每个
``sendto`` 对应一个数据报；接收端保留数据报边界，但数据报可能丢失、重复、乱序，
也可能因超过接收缓冲区而被截断。需要可靠性时，应用层要自己实现序号、确认、重传
和拥塞控制，或者直接使用 TCP/QUIC 等成熟协议。

安全提醒：裸 socket 不提供加密、身份认证、权限控制或输入校验。TLS 通常通过
``ssl`` 模块包装 TCP socket。服务端还应限制消息大小、连接数、空闲时间和资源占用。
"""

from __future__ import annotations

import argparse
import selectors
import socket
import struct
import threading
from collections.abc import Callable


HOST = "127.0.0.1"
MAX_FRAME_SIZE = 1024 * 1024
HEADER_SIZE = 4


def recv_exact(sock: socket.socket, size: int) -> bytes:
    """恰好读取 size 个字节，或在对端提前关闭时抛出 ConnectionError。

    一次 recv 可能少于请求的字节数，所以协议解析不能假设 ``recv(size)`` 一次
    就返回完整字段。这个循环是所有定长字段解析器的基础。
    """

    chunks: list[bytes] = []
    remaining = size

    while remaining:
        chunk = sock.recv(remaining)
        if not chunk:
            received = size - remaining
            raise ConnectionError(
                f"连接提前关闭：期望 {size} 字节，只收到 {received} 字节"
            )
        chunks.append(chunk)
        remaining -= len(chunk)

    return b"".join(chunks)


def send_frame(sock: socket.socket, payload: bytes) -> None:
    """发送一个“4 字节长度 + 正文”的应用层消息。"""

    if len(payload) > MAX_FRAME_SIZE:
        raise ValueError(f"消息超过上限 {MAX_FRAME_SIZE} 字节")
    header = struct.pack("!I", len(payload))
    sock.sendall(header + payload)


def recv_frame(sock: socket.socket) -> bytes:
    """接收一个长度前缀消息，并在分配内存前校验长度。"""

    header = recv_exact(sock, HEADER_SIZE)
    (size,) = struct.unpack("!I", header)
    if size > MAX_FRAME_SIZE:
        raise ValueError(f"对端声明的消息长度 {size} 超过上限")
    return recv_exact(sock, size)


def start_one_shot_tcp_server(
    handler: Callable[[socket.socket], None],
) -> tuple[int, threading.Thread]:
    """启动只处理一个客户端的本地 TCP 服务，返回临时端口和线程。

    先在主线程 bind/listen，再启动线程，可以避免客户端 connect 时服务端尚未就绪
    的竞态。端口 0 表示让内核选择一个当前可用的临时端口。
    """

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((HOST, 0))
    listener.listen(1)
    port = listener.getsockname()[1]

    def serve() -> None:
        with listener:
            conn, address = listener.accept()
            with conn:
                print(f"[server] accept: peer={address}, local={conn.getsockname()}")
                handler(conn)

    thread = threading.Thread(target=serve, name="socket-tutorial-server")
    thread.start()
    return port, thread


def demo_tcp_echo() -> None:
    """实验 1：观察 TCP 建连、半关闭、EOF 和回显。"""

    def handle(conn: socket.socket) -> None:
        chunks: list[bytes] = []
        while True:
            chunk = conn.recv(8)
            print(f"[server] recv -> {chunk!r}")
            if not chunk:
                break
            chunks.append(chunk)
        conn.sendall(b"echo:" + b"".join(chunks))

    port, server_thread = start_one_shot_tcp_server(handle)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.settimeout(3)
        client.connect((HOST, port))
        print(f"[client] local={client.getsockname()}, peer={client.getpeername()}")
        client.sendall("你好，TCP".encode("utf-8"))
        client.shutdown(socket.SHUT_WR)
        print(f"[client] response={client.recv(1024).decode('utf-8')!r}")

    server_thread.join()
    print("结论：shutdown(SHUT_WR) 让服务端 recv 到 EOF，但客户端仍能接收响应。")


def demo_framing() -> None:
    """实验 2：使用长度前缀，在同一 TCP 连接上可靠传递多条消息。"""

    messages = ["短消息", "包含换行\n也没关系", "x" * 20_000]

    def handle(conn: socket.socket) -> None:
        for _ in messages:
            request = recv_frame(conn)
            print(f"[server] 收到一帧：{len(request)} bytes")
            send_frame(conn, request.upper())

    port, server_thread = start_one_shot_tcp_server(handle)

    with socket.create_connection((HOST, port), timeout=3) as client:
        for message in messages:
            send_frame(client, message.encode("utf-8"))
            response = recv_frame(client).decode("utf-8")
            print(f"[client] 响应长度={len(response)}，预览={response[:30]!r}")

    server_thread.join()
    print("结论：消息可以被 TCP 任意分片，但 recv_exact 会按协议重新组装。")


def demo_udp() -> None:
    """实验 3：观察 UDP 数据报边界和无连接通信。"""

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind((HOST, 0))
        server.settimeout(3)
        server_address = server.getsockname()

        def serve() -> None:
            data, client_address = server.recvfrom(65_535)
            print(f"[udp server] 来自 {client_address} 的一个数据报：{data!r}")
            server.sendto(b"ack:" + data, client_address)

        thread = threading.Thread(target=serve, name="udp-tutorial-server")
        thread.start()

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
            client.settimeout(3)
            client.sendto(b"one complete datagram", server_address)
            response, address = client.recvfrom(65_535)
            print(f"[udp client] from={address}, response={response!r}")

        thread.join()

    print("结论：UDP 的一次 recvfrom 返回一个数据报，同时给出发送方地址。")


def demo_nonblocking() -> None:
    """实验 4：用 selectors 等待非阻塞 socket 变为可读。"""

    left, right = socket.socketpair()
    selector = selectors.DefaultSelector()

    try:
        left.setblocking(False)
        selector.register(left, selectors.EVENT_READ)

        try:
            left.recv(1)
        except BlockingIOError:
            print("[nonblocking] 当前无数据，recv 立即抛出 BlockingIOError")

        right.sendall(b"event loop data")
        events = selector.select(timeout=1)
        for key, _mask in events:
            print(f"[selector] fd={key.fd} 已可读：{key.fileobj.recv(1024)!r}")
    finally:
        selector.close()
        left.close()
        right.close()

    print("结论：selector 不传输数据，只通知哪些文件描述符已就绪。")


def simple_http_get(host: str, path: str = "/", port: int = 80) -> tuple[str, bytes]:
    """通过原始 TCP 发送 HTTP/1.1 GET，返回响应头文本和原始响应体。

    这是教学实现，不支持 HTTPS、重定向、chunked 解码、压缩和连接复用。真实项目
    应使用 urllib、http.client、httpx 或 requests。响应体保留 bytes，因为图片、
    压缩数据等并不一定是 UTF-8 文本。
    """

    if not path.startswith("/"):
        path = "/" + path

    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "Connection: close\r\n"
        "Accept-Encoding: identity\r\n"
        "User-Agent: raw-socket-tutorial/1.0\r\n"
        "\r\n"
    ).encode("ascii")

    chunks: list[bytes] = []
    with socket.create_connection((host, port), timeout=5) as sock:
        sock.sendall(request)
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)

    response = b"".join(chunks)
    head, separator, body = response.partition(b"\r\n\r\n")
    if not separator:
        raise ValueError("响应中没有找到 HTTP 头结束标记")
    return head.decode("iso-8859-1"), body


def demo_http(host: str, path: str) -> None:
    """实验 5：查看构建在 TCP 之上的 HTTP 响应。"""

    headers, body = simple_http_get(host, path)
    print("--- HTTP response headers ---")
    print(headers)
    print(f"--- body: {len(body)} bytes, preview ---")
    print(body[:500].decode("utf-8", errors="replace"))
    print("结论：TCP 只传 bytes；请求行、头、空行和正文边界都由 HTTP 定义。")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="通过可运行实验学习 Python Socket 和底层网络原理"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("tcp", help="TCP 回显、半关闭与 EOF")
    subparsers.add_parser("framing", help="TCP 长度前缀消息协议")
    subparsers.add_parser("udp", help="UDP 数据报")
    subparsers.add_parser("nonblocking", help="非阻塞 I/O 与 selectors")
    subparsers.add_parser("all", help="运行全部本地实验")

    http_parser = subparsers.add_parser("http", help="发送原始 HTTP/1.1 请求")
    http_parser.add_argument("host", nargs="?", default="example.com")
    http_parser.add_argument("path", nargs="?", default="/")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    demos: dict[str, Callable[[], None]] = {
        "tcp": demo_tcp_echo,
        "framing": demo_framing,
        "udp": demo_udp,
        "nonblocking": demo_nonblocking,
    }

    if args.command == "all":
        for name, demo in demos.items():
            print(f"\n{'=' * 24} {name} {'=' * 24}")
            demo()
    elif args.command == "http":
        demo_http(args.host, args.path)
    else:
        demos[args.command]()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
