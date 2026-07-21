# 15 进程与 `fork`/`exec`

## 学习目标

完成本章后，你应该能够：

- 解释 PID、父子关系和进程地址空间隔离
- 正确处理 `fork` 的三种返回结果
- 使用 `exec` 替换子进程映像
- 用 `waitpid` 回收子进程并解释退出或信号状态
- 避免 `fork` 与 stdio 缓冲、多线程和资源继承产生的常见问题

## 进程模型

进程是正在运行的程序实例，拥有虚拟地址空间、文件描述符表、信号状态和至少一个执行线程。PID 由内核分配，在某个时刻唯一，但退出后的 PID 以后可能被复用。

```c
#include <stdio.h>
#include <unistd.h>

int main(void) {
    printf("PID=%ld PPID=%ld\n", (long)getpid(), (long)getppid());
    return 0;
}
```

## `fork` 创建子进程

`fork` 调用一次，却在两个进程中返回：

| 返回值 | 所在进程 | 含义 |
| --- | --- | --- |
| `-1` | 原进程 | 创建失败，没有子进程 |
| `0` | 子进程 | 当前正在执行子进程路径 |
| 正数 | 父进程 | 返回值是新子进程 PID |

```c
pid_t pid = fork();
if (pid == -1) {
    perror("fork");
    return 1;
}
if (pid == 0) {
    /* 子进程路径 */
    _exit(0);
}
/* 父进程路径，pid 是子进程 ID。 */
```

父子进程拥有独立的虚拟地址空间。初始内容通常通过写时复制共享，任一进程写入后不影响另一方。文件描述符会被继承，父子描述符通常引用相同的 open file description，因此可能共享文件偏移和状态标志。

## stdio 缓冲与 `fork`

`fork` 会复制用户态 stdio 缓冲区。如果缓冲区在 `fork` 前尚未刷新，父子进程后来都调用 `exit` 或刷新流，内容可能输出两次。

```c
printf("starting\n");
if (fflush(NULL) == EOF) {
    perror("fflush");
    return 1;
}
pid_t pid = fork();
```

子进程调用 `_exit` 不会刷新 stdio 缓冲，所以在 `_exit` 前用 `printf` 的内容也可能丢失。fork 后准备 exec 的子进程通常使用 `write`/`dprintf` 报告错误，然后 `_exit`。

## `waitpid` 与子进程状态

子进程退出后，内核保留少量状态供父进程读取；父进程尚未回收时称为僵尸进程。

```c
#include <errno.h>
#include <sys/wait.h>

int status;
pid_t waited;
do {
    waited = waitpid(pid, &status, 0);
} while (waited == -1 && errno == EINTR);

if (waited == -1) {
    perror("waitpid");
} else if (WIFEXITED(status)) {
    printf("exit=%d\n", WEXITSTATUS(status));
} else if (WIFSIGNALED(status)) {
    printf("signal=%d\n", WTERMSIG(status));
}
```

只有 `WIFEXITED(status)` 为真时才能解释 `WEXITSTATUS`；只有 `WIFSIGNALED` 为真时才能读取终止信号。

## `exec` 替换进程映像

`exec` 族函数不会创建新进程，而是用另一个程序替换当前进程的代码、数据、堆和栈。PID 保持不变。调用成功后不会返回：

```c
char *const arguments[] = {"ls", "-l", NULL};
execvp(arguments[0], arguments);

/* 只有失败才执行。 */
int error = errno;
dprintf(STDERR_FILENO, "execvp failed: %s\n", strerror(error));
_exit(127);
```

常见名称可以拆解：

- `l`：参数以列表传入
- `v`：参数以 `argv` 数组传入
- `p`：按 `PATH` 搜索程序
- `e`：调用者显式提供环境数组

## `fork` + `exec` + `waitpid`

```text
父进程 fork
   ├── 子进程：关闭无关 fd -> exec
   └── 父进程：关闭无关 fd -> waitpid
```

父进程必须处理 `fork` 失败；子进程必须处理 `exec` 失败；父进程必须判断子进程是正常退出还是被信号终止。

现代 POSIX 还提供 `posix_spawn`，可在许多“创建后立即 exec”的场景中减少 fork 后准备工作的复杂度，尤其适合多线程程序。

## 多线程程序中的 `fork`

多线程进程调用 `fork` 后，子进程只保留调用 `fork` 的线程，但会继承其他线程可能持有的 mutex 状态。子进程在 `exec` 前原则上只能调用 async-signal-safe 函数，否则可能永久等待一个已不存在的线程释放锁。

实际工程通常选择：

- 在创建线程前启动子进程
- fork 后立即 exec
- 使用 `posix_spawn`
- 必要时谨慎使用 `pthread_atfork`

## 环境与文件描述符继承

子进程继承环境变量副本。`setenv` 只影响当前进程及之后创建的子进程，不会修改父进程或 shell。

默认情况下，打开的 fd 会跨 `exec` 保留。敏感或不需要继承的 fd 应设置 close-on-exec：

```c
int fd = open(path, O_RDONLY | O_CLOEXEC);
```

也可以通过 `fcntl` 设置 `FD_CLOEXEC`。忘记关闭继承的管道端点会导致读取方永远等不到 EOF。

## 进程退出

- `return` 离开 `main` 等价于调用 `exit`。
- `exit` 刷新并关闭 C 流，调用 `atexit` 处理器。
- `_exit` 立即把状态交给内核，不运行用户态清理。

fork 后 exec 失败的子进程通常使用 `_exit(127)`，避免重复刷新从父进程复制来的缓冲区。

## 常见错误

- 忽略 `fork` 失败并把父进程路径当作成功
- 未检查 `waitpid` 就读取 `status`
- 未判断 `WIFEXITED` 就调用 `WEXITSTATUS`
- fork 前没有刷新 stdio，导致重复输出
- `_exit` 前使用缓冲输出，导致内容丢失
- 父子进程没有关闭不需要的管道端点
- exec 前泄漏本应 close-on-exec 的 fd
- 多线程子进程在 exec 前调用可能加锁的库函数

## 检查点

1. `fork` 后为什么父子进程可能打印相同的指针值？
2. `exec` 成功后 PID 是否改变？
3. 为什么只有 `WIFEXITED` 为真才能读取退出码？
4. 为什么 fork 前未刷新的输出可能出现两次或完全消失？

## 动手练习

1. 运行 `examples/15_processes.c`，记录父子进程 PID 和退出状态。
2. 在 fork 前去掉 `fflush`，把输出重定向到文件，观察缓冲复制效果。
3. 完成 `exercises/10_minishell.c`：支持 fork、execvp、waitpid 和 `exit`。
4. 给迷你 shell 增加命令不存在、fork 失败模拟和信号终止状态输出。
