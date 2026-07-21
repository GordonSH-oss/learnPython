# 19 Socket 网络编程

## 学习目标

完成本章后，你应该能够：

- 使用 `getaddrinfo` 建立 IPv4/IPv6 TCP 客户端或服务端
- 解释 TCP 字节流和 UDP 数据报的语义差异
- 正确处理短读、短写、断开、`EINTR` 和 `SIGPIPE`
- 设计应用层消息边界，而不是假定一次读写就是一条消息
- 管理监听 socket、连接 socket 和并发 worker 的生命周期

## Socket 是什么

Socket 是操作系统提供的通信端点，在 POSIX 中通过 fd 操作。它与普通文件共享 `read`、`write`、`close` 等接口，但网络具有连接中断、分段、延迟、半关闭和对端不可信等额外语义。

```text
应用协议
   ↓
TCP 字节流 / UDP 数据报
   ↓
IP
   ↓
链路层
```

## 字节序

网络协议字段通常使用网络字节序，也就是大端序：

```c
uint16_t network_port = htons(8080);
uint16_t host_port = ntohs(network_port);
```

这些函数只转换固定宽度整数。应用消息中的字符串、浮点数和结构体不能通过直接发送内存布局自动变成可移植协议。协议必须明确字段宽度、编码、字节序和长度。

## 使用 `getaddrinfo`

不要只写死 `sockaddr_in` 和 IPv4。`getaddrinfo` 可以解析主机名并返回 IPv4/IPv6 候选：

```c
struct addrinfo hints = {
    .ai_family = AF_UNSPEC,
    .ai_socktype = SOCK_STREAM,
};
struct addrinfo *addresses = NULL;
int error = getaddrinfo(host, service, &hints, &addresses);
if (error != 0) {
    fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(error));
}
```

客户端应遍历候选地址，依次尝试 `socket` 和 `connect`，而不是假定第一个结果一定可用。结束后调用 `freeaddrinfo`。

## TCP 服务端生命周期

```text
getaddrinfo
   ↓
socket -> setsockopt -> bind -> listen
                                ↓
                         accept 循环
                                ↓
                     处理连接 -> close
```

每一步都可能失败并需要关闭已获得资源。常用 `SO_REUSEADDR` 缩短服务重启时地址仍被占用造成的等待，但它不等于允许任意两个活跃服务安全绑定同一地址。

使用端口 `0` 绑定时，内核会选择可用端口；可以通过 `getsockname` 查询。这比测试中写死端口并睡眠等待更可靠。

`accept` 返回一个新的连接 fd；监听 fd 继续接受其他连接。两者必须分别关闭。

## TCP 是字节流

发送端两次 `write`：

```text
write("hello")
write("world")
```

接收端可能一次读到 `helloworld`，也可能分成任意片段。TCP 保证有序字节流，不保存应用调用边界。

应用协议必须自行定义消息边界，例如：

- 固定长度记录
- 长度前缀
- 分隔符，并规定转义和最大长度
- 连接关闭表示消息结束

读取长度前缀后还要验证上限，防止对端诱导超大分配。

## 发送全部数据

一次 `send` 可能只接受部分字节：

```c
static int send_all(int fd, const void *data, size_t length) {
    const unsigned char *cursor = data;
    while (length > 0) {
        ssize_t sent = send(fd, cursor, length, 0);
        if (sent > 0) {
            cursor += sent;
            length -= (size_t)sent;
        } else if (sent == -1 && errno == EINTR) {
            continue;
        } else {
            return -1;
        }
    }
    return 0;
}
```

向已关闭连接发送可能触发 `SIGPIPE` 并终止进程。平台策略包括忽略 `SIGPIPE`、Linux 使用 `MSG_NOSIGNAL`，或 macOS 设置 `SO_NOSIGPIPE`。应选择平台合适方法，并仍然处理 `EPIPE`。

## 接收、EOF 与半关闭

`recv` 返回：

- 正数：收到这些字节
- `0`：对端已完成发送方向的有序关闭
- `-1`：错误；`EINTR` 可重试，非阻塞模式还会出现 `EAGAIN`

TCP 支持半关闭：`shutdown(fd, SHUT_WR)` 表示本端不再发送，但仍可接收对端剩余数据。`close` 则释放本进程对 socket 的引用。

## UDP 数据报

UDP 保留数据报边界，但不保证到达、顺序或唯一性。`recvfrom` 一次接收一条数据报；缓冲区过小时，超出部分可能被截断。

应用必须考虑：

- 丢包、重复和乱序是否需要业务层处理
- 单个数据报最大尺寸
- 来源地址是否可信
- 放大攻击和伪造来源风险

UDP “无连接”表示不需要 TCP 握手，并不表示完全没有本地状态；UDP socket 也可以调用 `connect` 固定默认对端并过滤来源。

## 并发服务器

常见模型：

- fork-per-connection：概念直观，进程成本较高
- thread-per-connection：共享状态方便，但线程和同步成本随连接增长
- 固定线程池：限制并发资源，需要队列和背压
- 非阻塞事件循环：适合大量连接，但状态机更复杂

fork 模型中，子进程关闭监听 fd，父进程关闭连接 fd。必须处理 fork 失败；否则父进程可能错误关闭唯一连接而没有 worker 接管。

线程模型中不能把栈上的 `client_fd` 地址交给线程后立即在下一轮覆盖。应为任务保存独立值，并明确谁负责 close。

## 超时与背压

生产服务不能让一个慢客户端无限占用资源。可以使用：

- `poll`/`select`/`kqueue`/`epoll` 超时
- socket 收发超时
- 应用层 deadline
- 最大消息长度、最大连接数和有界任务队列

超时后必须明确连接状态和已发送部分是否可以安全重试。网络操作通常不是天然幂等。

## 常见错误

- 不检查 `socket`、`bind`、`listen`、`accept`、`connect`
- `recv` 返回 `-1` 后写 `buffer[-1]`
- 假定一次 send/write 发送全部数据
- 把一次 recv/read 当作一条完整消息
- 用固定 `sleep` 猜测服务端已经监听
- 忽略 `SIGPIPE` 和对端提前关闭
- 只支持 IPv4 数字地址，不处理 DNS 和 IPv6
- fork 失败后仍按父进程成功路径关闭连接
- 无限创建进程或线程，没有资源上限和背压

## 检查点

1. 两次 `send` 是否一定对应接收端两次 `recv`？不一定。
2. TCP `recv` 返回 `0` 表示什么？对端发送方向已关闭。
3. UDP 是否会自动重传丢失数据报？不会。
4. 为什么测试服务更适合绑定端口 0，而不是固定端口后睡眠？

## 动手练习

1. 运行 `examples/19_socket.c`，解释监听 socket 为什么在 fork 前建立。
2. 给回显协议增加 32 位网络字节序长度前缀，并限制最大消息为 1 MiB。
3. 完成 `exercises/14_chat_server.c`，处理短写、断开和子进程回收。
4. 用 `getaddrinfo` 改写客户端，同时尝试 `localhost` 的 IPv4 和 IPv6 地址。
5. 使用本地客户端发送分片数据，验证服务端不会假定一次 read 得到完整消息。

配套示例需要本地监听端口权限。批量脚本默认跳过它；允许本地网络时运行：

```bash
make build/examples/19_socket
./build/examples/19_socket
# 或让批量脚本包含网络示例
RUN_NETWORK_EXAMPLES=1 bash scripts/run_examples.sh
```
