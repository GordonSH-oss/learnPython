/**
 * 练习 14: 多客户端 TCP 回显聊天服务器 (Multi-Client TCP Echo Chat Server)
 *
 * 使用 fork 实现一个简单的多客户端 TCP 聊天服务器。
 * 每个客户端连接由独立子进程处理，收到消息后加 "Server: " 前缀回显。
 *
 * 编译: clang -std=c17 -Wall -Wextra -Wpedantic -o 14_chat_server 14_chat_server.c
 * 运行: ./14_chat_server [端口号]
 * 测试: nc localhost 8080
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define DEFAULT_PORT 8080
#define BUFFER_SIZE  1024
#define BACKLOG      5

/* 全局服务器 socket，用于信号处理函数中关闭 */
static int server_fd = -1;

/**
 * SIGCHLD 信号处理函数
 * 回收已终止的子进程，防止产生僵尸进程
 */
void sigchld_handler(int sig) {
    (void)sig;
    // TODO: 使用 waitpid 配合 WNOHANG 循环回收所有已终止的子进程
}

/**
 * SIGINT 信号处理函数
 * 优雅关闭服务器 socket 并退出
 */
void sigint_handler(int sig) {
    (void)sig;
    // TODO: 关闭 server_fd，打印退出信息，调用 exit(0)
}

/**
 * 处理单个客户端的通信
 * 在子进程中运行，循环读取消息并回显
 */
void handle_client(int client_fd, struct sockaddr_in *client_addr) {
    char buffer[BUFFER_SIZE];
    char response[BUFFER_SIZE + 16];

    printf("[子进程 %d] 客户端已连接: %s:%d\n",
           getpid(), inet_ntoa(client_addr->sin_addr),
           ntohs(client_addr->sin_port));

    // TODO: 循环读取客户端消息 (使用 read/recv)
    //   - 如果 read 返回 0 或负数，表示客户端断开，退出循环
    //   - 去掉消息末尾的换行符
    //   - 拼接 "Server: " 前缀和原始消息到 response
    //   - 将 response 发送回客户端 (使用 write/send)

    printf("[子进程 %d] 客户端已断开\n", getpid());
    close(client_fd);
    exit(0);
}

int main(int argc, char *argv[]) {
    int port = (argc > 1) ? atoi(argv[1]) : DEFAULT_PORT;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len = sizeof(client_addr);

    // TODO: 注册 SIGCHLD 和 SIGINT 信号处理函数 (使用 signal 或 sigaction)

    // TODO: 创建 TCP socket (AF_INET, SOCK_STREAM)
    //       设置 SO_REUSEADDR 选项避免 "Address already in use" 错误

    // TODO: 填充 server_addr 结构体 (AF_INET, INADDR_ANY, htons(port))
    //       绑定 socket 到该地址 (bind)

    // TODO: 开始监听连接 (listen, BACKLOG)

    printf("聊天服务器启动，监听端口 %d ...\n", port);
    printf("使用 Ctrl+C 关闭服务器\n");

    // TODO: 主循环 — 接受新连接 (accept)
    //   - accept 返回新的 client_fd
    //   - fork 创建子进程:
    //     - 子进程: 关闭 server_fd, 调用 handle_client
    //     - 父进程: 关闭 client_fd, 继续循环

    return 0;
}
