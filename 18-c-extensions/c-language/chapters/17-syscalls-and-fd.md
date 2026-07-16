# 17 系统调用与文件描述符

## 学习目标

理解用户态与内核态的边界，掌握文件描述符、重定向、管道和内存映射等 POSIX I/O 机制。

## 系统调用 vs 库函数

`printf` 是 C 库函数，内部最终调用 `write` 系统调用进入内核。系统调用开销更大（需要上下文切换），但是所有 I/O 的最终出口。

```c
#include <unistd.h>

int main(void) {
    // write 是系统调用，直接交给内核
    write(STDOUT_FILENO, "hello\n", 6);
    // printf 是库函数，经过用户态缓冲后批量 write
    printf("world\n");
    return 0;
}
```

## 文件描述符

内核为每个进程维护一张打开文件表，文件描述符（fd）是该表的索引。

| fd | 含义 |
|----|------|
| 0  | stdin  |
| 1  | stdout |
| 2  | stderr |

```c
#include <fcntl.h>
#include <unistd.h>

int main(void) {
    int fd = open("data.txt", O_RDONLY);
    if (fd < 0) { perror("open"); return 1; }

    char buf[256];
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    if (n > 0) { buf[n] = '\0'; write(STDOUT_FILENO, buf, n); }
    close(fd);
    return 0;
}
```

## stdio 是封装层

`FILE *` 在 fd 之上增加了缓冲，减少系统调用次数。

```c
#include <stdio.h>
#include <unistd.h>

int main(void) {
    // 获取 FILE* 底层的 fd
    int fd = fileno(stdout);
    printf("stdout fd = %d\n", fd);

    // 反向：将 fd 包装成 FILE*
    int raw = open("out.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    FILE *fp = fdopen(raw, "w");
    fprintf(fp, "buffered write\n");
    fclose(fp); // 同时关闭 raw fd
    return 0;
}
```

缓冲策略：终端行缓冲，文件全缓冲，stderr 无缓冲。可用 `setvbuf` 手动切换。

## dup2 重定向

`dup2(old_fd, new_fd)` 让 new_fd 指向 old_fd 的同一文件，常用于重定向。

```c
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>

int main(void) {
    int fd = open("log.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    dup2(fd, STDOUT_FILENO); // stdout 现在写入 log.txt
    close(fd);               // 原 fd 不再需要

    printf("this goes to log.txt\n");
    return 0;
}
```

## pipe 管道

`pipe` 创建一对 fd：`pipefd[0]` 读端，`pipefd[1]` 写端。配合 `fork` 实现父子进程通信。

```c
#include <unistd.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    int pipefd[2];
    pipe(pipefd);

    if (fork() == 0) {
        // 子进程：写入管道
        close(pipefd[0]);
        const char *msg = "hello from child";
        write(pipefd[1], msg, strlen(msg));
        close(pipefd[1]);
        _exit(0);
    }
    // 父进程：读取管道
    close(pipefd[1]);
    char buf[64];
    ssize_t n = read(pipefd[0], buf, sizeof(buf) - 1);
    buf[n] = '\0';
    printf("parent got: %s\n", buf);
    close(pipefd[0]);
    return 0;
}
```

## I/O 多路复用

当需要同时监视多个 fd（网络连接、管道等），用 `select` 或 `poll` 避免逐个阻塞。

```c
#include <poll.h>
#include <unistd.h>
#include <stdio.h>

// 同时监视 stdin 和另一个 fd
void watch_two(int fd1, int fd2) {
    struct pollfd fds[2] = {
        { .fd = fd1, .events = POLLIN },
        { .fd = fd2, .events = POLLIN },
    };
    int ready = poll(fds, 2, 5000); // 超时 5 秒
    if (ready > 0) {
        if (fds[0].revents & POLLIN) printf("fd1 readable\n");
        if (fds[1].revents & POLLIN) printf("fd2 readable\n");
    }
}
```

生产环境推荐 Linux `epoll` 或 macOS `kqueue`，但接口思想与 `poll` 一致。

## mmap 内存映射文件

将文件内容映射到进程地址空间，读写内存即读写文件，适合大文件随机访问。

```c
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    int fd = open("data.bin", O_RDWR | O_CREAT | O_TRUNC, 0644);
    const char *text = "mmap demo data";
    size_t len = strlen(text);
    ftruncate(fd, len); // 设定文件大小

    char *map = mmap(NULL, len, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    close(fd); // 映射建立后可关闭 fd

    memcpy(map, text, len);   // 写入
    printf("read back: %.*s\n", (int)len, map);

    munmap(map, len);
    return 0;
}
```

`MAP_SHARED` 修改会写回文件，`MAP_PRIVATE` 则写时复制。`msync` 可强制刷盘。
