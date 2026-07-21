# 17 系统调用与文件描述符

## 学习目标

完成本章后，你应该能够：

- 区分 ISO C 流、POSIX API 和内核系统调用边界
- 解释 fd、描述符表和 open file description 的关系
- 正确处理短读、短写、EOF 和 `EINTR`
- 使用 `dup2`、管道和 close-on-exec 管理 fd 生命周期
- 安全建立并释放文件映射

## 库函数与系统调用

`printf` 是 C 标准库函数，通常先写入用户态缓冲区，最终可能通过 `write` 等系统接口提交数据。一次系统调用涉及用户态到内核态的模式切换，但不等于一定发生线程调度或进程上下文切换。

POSIX 函数也不一定一一对应系统调用。例如 `opendir`、`stdio` 和线程函数包含用户态封装。编程时应遵守公开 API 契约，而不是假定特定 libc 内部实现。

```c
#include <stdio.h>
#include <unistd.h>

int main(void) {
    const char message[] = "hello from write\n";
    if (write(STDOUT_FILENO, message, sizeof message - 1) == -1) {
        perror("write");
        return 1;
    }
    return 0;
}
```

## fd 模型

fd 是当前进程描述符表中的一个小整数索引：

```text
进程 fd 表                  内核 open file description
fd 3 --------------------> 文件偏移、状态标志、底层对象
fd 4 -----------+
                +--------> 另一个打开实例
```

`dup`、`dup2` 和 `fork` 可能让多个 fd 引用同一个 open file description，因此共享文件偏移和某些状态。文件路径不是 fd：文件被重命名后，已经打开的 fd 通常仍然引用原对象。

传统标准描述符为：

| fd | 常量 | 通常用途 |
| --- | --- | --- |
| 0 | `STDIN_FILENO` | 标准输入 |
| 1 | `STDOUT_FILENO` | 标准输出 |
| 2 | `STDERR_FILENO` | 标准错误 |

程序仍应允许它们已关闭或被重定向。

## `open`、`read`、`write`、`close`

```c
int fd = open(path, O_RDONLY | O_CLOEXEC);
if (fd == -1) {
    perror("open");
    return 1;
}
```

`O_CLOEXEC` 防止 fd 意外泄漏到之后 `exec` 的程序。

### 短读与 EOF

`read` 返回：

- 正数：本次实际读取的字节数，可能少于请求
- `0`：EOF；管道或 socket 中通常表示所有写端已经关闭
- `-1`：失败，检查 `errno`

```c
ssize_t count;
do {
    count = read(fd, buffer, capacity);
} while (count == -1 && errno == EINTR);
```

只有 `count > 0` 时才能访问这部分数据。二进制数据不需要 `\0`；若要作为字符串打印，必须预留一个字节并手动终止。

### 短写

`write` 成功也可能只写入部分数据。对普通文件、管道和 socket，都应根据接口需求循环：

```c
static int write_all(int fd, const void *data, size_t length) {
    const unsigned char *cursor = data;
    while (length > 0) {
        ssize_t written = write(fd, cursor, length);
        if (written > 0) {
            cursor += written;
            length -= (size_t)written;
        } else if (written == -1 && errno == EINTR) {
            continue;
        } else {
            return -1;
        }
    }
    return 0;
}
```

非阻塞 fd 还要处理 `EAGAIN`/`EWOULDBLOCK`，通常交给事件循环稍后重试。

`close` 也可能失败。尤其是写入文件时，延迟错误可能在关闭时才暴露。失败后的 fd 状态具有平台细节，不能盲目循环 close 一个可能已被其他线程复用的整数。

## `FILE *` 与 fd

`FILE *` 是 C 流抽象，通常在 fd 之上增加缓冲、格式化和流状态。POSIX 提供：

```c
int fd = fileno(stdout);
FILE *stream = fdopen(raw_fd, "w");
```

`fdopen` 失败时原 fd 仍由调用者负责；成功后 `fclose(stream)` 会同时关闭底层 fd。不要再单独 close 同一个 fd。

不要在同一底层文件位置上无协议地混用 stdio 和 `read`/`write`。缓冲可能让两层看到不同的偏移和数据状态。切换前必须遵守相关同步规则，最简单的设计是一个资源只交给一层管理。

## `dup2` 与重定向

`dup2(old_fd, new_fd)` 让 `new_fd` 引用与 `old_fd` 相同的 open file description。若 `new_fd` 已打开，它会被原子关闭并替换。

```c
if (fflush(stdout) == EOF) {
    perror("fflush");
    return 1;
}
if (dup2(file_fd, STDOUT_FILENO) == -1) {
    perror("dup2");
    return 1;
}
```

重定向 stdio 对应的 fd 前先刷新流，避免旧缓冲内容被写到新目标。`dup2` 成功后，如果不再需要原 fd，应关闭它。

shell 执行 `command >output 2>&1` 的核心就是在 exec 前建立这样的描述符关系。

## 管道与 EOF

`pipe` 创建读端和写端：

```text
pipefd[1] --bytes--> pipefd[0]
```

fork 后父子进程都继承两端，必须立即关闭不使用的端点。只要任意进程仍持有写端，读端就不会看到 EOF。这是管道程序“已经写完却永远阻塞”的常见根因。

小于等于 `PIPE_BUF` 的单次管道写入在阻塞模式下具有特定原子性保证，但不代表任意大小消息都不会交错。字节流也不保存应用消息边界。

## I/O 多路复用

`poll` 可以同时等待多个 fd：

```c
struct pollfd descriptors[] = {
    {.fd = input_fd, .events = POLLIN},
    {.fd = socket_fd, .events = POLLIN},
};

int ready;
do {
    ready = poll(descriptors, 2, 5000);
} while (ready == -1 && errno == EINTR);
```

返回后不仅要检查 `POLLIN`，还要处理 `POLLERR`、`POLLHUP` 和 `POLLNVAL`。可读表示一次读取不会按原条件阻塞，不保证能得到完整应用消息。

Linux 的 `epoll` 和 macOS 的 `kqueue` 更适合大量 fd，但仍需正确处理非阻塞 I/O、部分完成和连接生命周期。

## `mmap` 文件映射

建立文件映射的基本流程：

```text
open -> 确认/设置文件长度 -> mmap -> 访问 -> munmap -> close
```

```c
void *mapping = mmap(NULL, length, PROT_READ | PROT_WRITE,
                     MAP_SHARED, fd, 0);
if (mapping == MAP_FAILED) {
    perror("mmap");
}
```

注意：

- 长度必须有效，零长度映射不可用。
- 访问超过文件实际范围的映射页面可能触发 `SIGBUS`。
- `MAP_SHARED` 修改对底层对象可见；`MAP_PRIVATE` 修改使用写时复制。
- `msync(..., MS_SYNC)` 请求同步映射修改，但完整持久性还涉及文件系统和硬件语义。
- 映射建立后通常可以关闭 fd，映射仍保持；但最终必须 `munmap`。

`mmap` 不保证比 `read` 更快。顺序流式处理、小文件和错误隔离需求都可能更适合普通 I/O。

## 常见错误

- 把系统调用等同于一定发生上下文切换
- 把 fd 直接等同于文件对象
- 未处理短读、短写和 `EINTR`
- `read` 返回 `-1` 后用负数作为数组索引
- 忘记关闭管道的多余写端导致无 EOF
- `fdopen` 成功后又 close 原 fd
- 重定向前未刷新 stdio
- 用 `mapping == NULL` 判断 mmap 失败
- 映射空文件或访问超过文件长度

## 检查点

1. 两个通过 `dup` 得到的 fd 是否共享文件偏移？通常是。
2. 为什么一次成功 `write` 也可能需要继续写？
3. 为什么父进程保留管道写端会让读端等不到 EOF？
4. `MAP_FAILED` 的值是否保证为 `NULL`？不保证。

## 动手练习

1. 运行 `examples/17_syscalls_fd.c`，跟踪每个 fd 的创建、复制和关闭。
2. 完成 `exercises/12_file_copy.c`，循环处理短读短写和 `EINTR`。
3. 创建管道后故意不关闭一个写端，观察 EOF 等待，再修复。
4. 映射一个临时文件，分别测试 `MAP_SHARED` 与 `MAP_PRIVATE` 的写入结果。
