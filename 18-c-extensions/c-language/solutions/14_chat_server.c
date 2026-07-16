/**
 * 练习 14 参考答案: 多客户端 TCP 回显聊天服务器
 * 编译: clang -std=c17 -Wall -Wextra -Wpedantic -o 14_chat_server 14_chat_server.c
 * 运行: ./14_chat_server [端口号]    测试: nc localhost 8080
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

static int server_fd = -1;  /* 全局服务器 socket，供信号处理函数使用 */

/* SIGCHLD 处理: 回收僵尸子进程 */
void sigchld_handler(int sig) {
    (void)sig;
    while (waitpid(-1, NULL, WNOHANG) > 0);
}

/* SIGINT 处理: 优雅关闭服务器 */
void sigint_handler(int sig) {
    (void)sig;
    printf("\n服务器正在关闭...\n");
    if (server_fd != -1) close(server_fd);
    exit(0);
}

/* 处理单个客户端的通信 (子进程中运行) */
void handle_client(int client_fd, struct sockaddr_in *addr) {
    char buffer[BUFFER_SIZE], response[BUFFER_SIZE + 16];
    printf("[子进程 %d] 客户端已连接: %s:%d\n",
           getpid(), inet_ntoa(addr->sin_addr), ntohs(addr->sin_port));

    ssize_t n;
    while ((n = read(client_fd, buffer, BUFFER_SIZE - 1)) > 0) {
        buffer[n] = '\0';
        /* 去除末尾换行符 */
        while (n > 0 && (buffer[n-1] == '\n' || buffer[n-1] == '\r'))
            buffer[--n] = '\0';
        if (n == 0) continue;

        snprintf(response, sizeof(response), "Server: %s\n", buffer);
        write(client_fd, response, strlen(response));
    }
    printf("[子进程 %d] 客户端已断开\n", getpid());
    close(client_fd);
    exit(0);
}

int main(int argc, char *argv[]) {
    int port = (argc > 1) ? atoi(argv[1]) : DEFAULT_PORT;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len = sizeof(client_addr);

    signal(SIGCHLD, sigchld_handler);  /* 注册信号处理 */
    signal(SIGINT, sigint_handler);

    /* 创建 TCP socket 并设置地址复用 */
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) { perror("socket"); exit(1); }
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    /* 绑定地址并开始监听 */
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);
    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("bind"); close(server_fd); exit(1);
    }
    if (listen(server_fd, BACKLOG) < 0) {
        perror("listen"); close(server_fd); exit(1);
    }

    printf("聊天服务器启动，监听端口 %d ...\n", port);
    printf("使用 Ctrl+C 关闭服务器\n");

    /* 主循环: 接受连接并 fork 子进程处理 */
    while (1) {
        int client_fd = accept(server_fd,
                               (struct sockaddr *)&client_addr, &client_len);
        if (client_fd < 0) { perror("accept"); continue; }

        pid_t pid = fork();
        if (pid < 0) {
            perror("fork"); close(client_fd);
        } else if (pid == 0) {
            close(server_fd);  /* 子进程关闭监听 socket */
            handle_client(client_fd, &client_addr);
        } else {
            close(client_fd);  /* 父进程关闭客户端 fd */
        }
    }
    return 0;
}
