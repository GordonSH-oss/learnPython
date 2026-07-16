/**
 * 19_socket.c - TCP 回显(echo)示例：fork 成服务器+客户端
 * 编译: clang -std=c17 -Wall -Wextra -Wpedantic 19_socket.c -o 19_socket
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define PORT 9999
#define BUF_SIZE 256

/* 子进程：TCP 回显服务器 */
static void run_server(void) {
    int sfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sfd < 0) { perror("server socket"); exit(1); }

    /* 允许端口复用 */
    int opt = 1;
    setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_port = htons(PORT),
        .sin_addr.s_addr = inet_addr("127.0.0.1")
    };

    if (bind(sfd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind"); exit(1);
    }
    if (listen(sfd, 1) < 0) { perror("listen"); exit(1); }

    printf("[服务器] 监听 127.0.0.1:%d ...\n", PORT);

    /* 接受一个连接 */
    int cfd = accept(sfd, NULL, NULL);
    if (cfd < 0) { perror("accept"); exit(1); }

    /* 读取数据并回显 */
    char buf[BUF_SIZE];
    ssize_t n = read(cfd, buf, sizeof(buf) - 1);
    if (n > 0) {
        buf[n] = '\0';
        printf("[服务器] 收到: \"%s\"\n", buf);
        write(cfd, buf, (size_t)n);  /* 回显 */
    }

    close(cfd);
    close(sfd);
}

/* 父进程：TCP 客户端 */
static void run_client(void) {
    /* 等待服务器就绪 */
    usleep(100000);  /* 100ms */

    int sfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sfd < 0) { perror("client socket"); exit(1); }

    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_port = htons(PORT),
        .sin_addr.s_addr = inet_addr("127.0.0.1")
    };

    if (connect(sfd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("connect"); exit(1);
    }

    const char *msg = "Hello, TCP echo!";
    write(sfd, msg, strlen(msg));
    printf("[客户端] 发送: \"%s\"\n", msg);

    /* 读取回显 */
    char buf[BUF_SIZE];
    ssize_t n = read(sfd, buf, sizeof(buf) - 1);
    if (n > 0) {
        buf[n] = '\0';
        printf("[客户端] 收到回显: \"%s\"\n", buf);
    }

    close(sfd);
}

int main(void) {
    printf("=== TCP Echo Demo (fork: 服务器 + 客户端) ===\n");

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return 1;
    }

    if (pid == 0) {
        /* 子进程 → 服务器 */
        run_server();
        _exit(0);
    } else {
        /* 父进程 → 客户端 */
        run_client();
        /* 等待子进程退出 */
        int status;
        waitpid(pid, &status, 0);
        printf("服务器子进程退出, status=%d\n", WEXITSTATUS(status));
    }

    return 0;
}
