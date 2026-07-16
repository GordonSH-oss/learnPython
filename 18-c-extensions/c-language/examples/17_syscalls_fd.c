/**
 * 17_syscalls_fd.c - 系统调用与文件描述符
 * 编译: clang -std=c17 -Wall -Wextra -Wpedantic 17_syscalls_fd.c -o 17_syscalls_fd
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

int main(void) {
    // === 1. write() 系统调用 vs printf ===
    const char *msg = "1) 直接用 write() 写到 stdout (fd=1)\n";
    write(STDOUT_FILENO, msg, strlen(msg));  // fd=1 即标准输出
    printf("   printf 底层也是调用 write(1, ...)\n\n");
    fflush(stdout);

    // === 2. open/read/close 读取文件 ===
    printf("2) 用 open/read/close 读取 /etc/hosts 前 80 字节:\n");
    int fd = open("/etc/hosts", O_RDONLY);
    if (fd < 0) {
        perror("open");
        return 1;
    }
    char buf[81] = {0};
    ssize_t n = read(fd, buf, 80);
    if (n > 0) {
        printf("   [fd=%d] 读到 %zd 字节:\n   %s\n\n", fd, n, buf);
    }
    close(fd);

    // === 3. dup2: 重定向 stdout 到文件 ===
    printf("3) dup2 重定向 stdout -> /tmp/redir_test.txt\n");
    fflush(stdout);
    int saved_stdout = dup(STDOUT_FILENO);  // 保存原 stdout
    int file_fd = open("/tmp/redir_test.txt",
                       O_WRONLY | O_CREAT | O_TRUNC, 0644);
    dup2(file_fd, STDOUT_FILENO);           // stdout 指向文件
    printf("   这行 printf 会写入文件而非终端\n");
    fflush(stdout);
    dup2(saved_stdout, STDOUT_FILENO);      // 恢复 stdout
    close(file_fd);
    close(saved_stdout);

    // 验证文件内容
    char verify[128] = {0};
    int vfd = open("/tmp/redir_test.txt", O_RDONLY);
    read(vfd, verify, sizeof(verify) - 1);
    close(vfd);
    printf("   恢复后读回文件内容: %s\n", verify);

    // === 4. pipe: 管道通信 ===
    printf("4) pipe 管道: 写入一端, 从另一端读出\n");
    int pipefd[2];  // pipefd[0]=读端, pipefd[1]=写端
    if (pipe(pipefd) < 0) {
        perror("pipe");
        return 1;
    }
    const char *pipe_msg = "Hello from pipe!";
    write(pipefd[1], pipe_msg, strlen(pipe_msg));
    close(pipefd[1]);  // 关闭写端

    char pipe_buf[64] = {0};
    read(pipefd[0], pipe_buf, sizeof(pipe_buf) - 1);
    close(pipefd[0]);
    printf("   管道读出: %s\n\n", pipe_buf);

    // === 5. FILE* 与 fd 的关系 ===
    printf("5) FILE* 与文件描述符的关系 (fileno):\n");
    printf("   stdin  -> fd %d\n", fileno(stdin));
    printf("   stdout -> fd %d\n", fileno(stdout));
    printf("   stderr -> fd %d\n", fileno(stderr));

    FILE *fp = fopen("/tmp/redir_test.txt", "r");
    if (fp) {
        printf("   fopen 得到的 FILE* 底层 fd = %d\n", fileno(fp));
        fclose(fp);
    }

    printf("\n总结: fd 是内核级句柄, FILE* 是 C 标准库的缓冲包装\n");
    return 0;
}
