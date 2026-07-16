# 19 Socket 网络编程

## 学习目标

理解 TCP/IP 网络分层模型，掌握 Socket API 进行 TCP/UDP 通信的完整流程。

## 网络分层与 Socket 概念

TCP/IP 四层模型：应用层 → 传输层(TCP/UDP) → 网络层(IP) → 链路层。Socket 是操作系统提供的网络通信抽象，本质是一个文件描述符(fd)，通过它可以像读写文件一样进行网络 I/O。

## 字节序

网络传输统一使用大端序(Big-Endian)。主机字节序因架构而异，需要转换：

```c
#include <arpa/inet.h>

uint16_t port = htons(8080);    // host to network short
uint32_t addr = htonl(INADDR_ANY); // host to network long
uint16_t local_port = ntohs(port); // network to host short
```

## 地址结构

```c
#include <netinet/in.h>
#include <arpa/inet.h>

struct sockaddr_in server_addr;
server_addr.sin_family = AF_INET;
server_addr.sin_port = htons(8080);
inet_pton(AF_INET, "127.0.0.1", &server_addr.sin_addr);
```

## TCP 服务端流程

socket → bind → listen → accept → read/write → close

```c
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

int main(void) {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);

    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_port = htons(8080),
        .sin_addr.s_addr = INADDR_ANY
    };

    bind(server_fd, (struct sockaddr *)&addr, sizeof(addr));
    listen(server_fd, 5);

    struct sockaddr_in client_addr;
    socklen_t client_len = sizeof(client_addr);
    int client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &client_len);

    char buf[1024];
    ssize_t n = read(client_fd, buf, sizeof(buf) - 1);
    buf[n] = '\0';
    printf("收到: %s\n", buf);
    write(client_fd, "OK\n", 3);

    close(client_fd);
    close(server_fd);
    return 0;
}
```

## TCP 客户端流程

socket → connect → write/read → close

```c
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main(void) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);

    struct sockaddr_in server = {
        .sin_family = AF_INET,
        .sin_port = htons(8080)
    };
    inet_pton(AF_INET, "127.0.0.1", &server.sin_addr);

    connect(fd, (struct sockaddr *)&server, sizeof(server));
    write(fd, "Hello", 5);

    char buf[1024];
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    buf[n] = '\0';
    printf("服务端回复: %s\n", buf);

    close(fd);
    return 0;
}
```

## UDP 收发

UDP 无连接，使用 sendto/recvfrom 直接收发数据报：

```c
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

// UDP 服务端
int main(void) {
    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_port = htons(9090),
        .sin_addr.s_addr = INADDR_ANY
    };
    bind(fd, (struct sockaddr *)&addr, sizeof(addr));

    char buf[1024];
    struct sockaddr_in client;
    socklen_t len = sizeof(client);
    ssize_t n = recvfrom(fd, buf, sizeof(buf) - 1, 0,
                         (struct sockaddr *)&client, &len);
    buf[n] = '\0';
    printf("UDP 收到: %s\n", buf);

    const char *reply = "ACK";
    sendto(fd, reply, strlen(reply), 0,
           (struct sockaddr *)&client, len);

    close(fd);
    return 0;
}
```

## 并发服务器 (fork-per-connection)

每次 accept 后 fork 子进程处理客户端，父进程继续监听：

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <netinet/in.h>
#include <signal.h>

void handle_client(int fd) {
    char buf[1024];
    ssize_t n;
    while ((n = read(fd, buf, sizeof(buf))) > 0)
        write(fd, buf, n); // echo back
    close(fd);
}

int main(void) {
    signal(SIGCHLD, SIG_IGN); // 自动回收子进程

    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_port = htons(8080),
        .sin_addr.s_addr = INADDR_ANY
    };
    bind(server_fd, (struct sockaddr *)&addr, sizeof(addr));
    listen(server_fd, 128);

    for (;;) {
        int client_fd = accept(server_fd, NULL, NULL);
        if (fork() == 0) {      // 子进程
            close(server_fd);
            handle_client(client_fd);
            _exit(0);
        }
        close(client_fd);       // 父进程关闭连接 fd
    }
}
```

编译与测试：开两个终端，一个运行服务端，另一个用 `nc 127.0.0.1 8080` 作为客户端测试。
