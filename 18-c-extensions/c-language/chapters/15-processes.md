# 15 进程与 fork/exec

## 学习目标

理解 POSIX 进程模型，掌握 fork 创建子进程、exec 替换进程映像以及正确回收子进程的方法。

## 进程基础

每个进程有唯一的 PID，由内核分配。

```c
#include <unistd.h>
#include <stdio.h>

int main(void) {
    printf("PID:  %d\n", getpid());
    printf("PPID: %d\n", getppid());
    return 0;
}
```

## fork 创建子进程

`fork()` 复制当前进程。父进程得到子进程 PID，子进程得到 0，失败返回 -1。

```c
#include <unistd.h>
#include <stdio.h>

int main(void) {
    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return 1;
    } else if (pid == 0) {
        printf("子进程, PID=%d\n", getpid());
    } else {
        printf("父进程, 子PID=%d\n", pid);
    }
    return 0;
}
```

fork 之后父子进程拥有独立的地址空间，变量修改互不影响。

## wait/waitpid 回收子进程

子进程退出后若父进程未调用 wait，则变为僵尸进程占用系统资源。

```c
#include <sys/wait.h>
#include <unistd.h>
#include <stdio.h>

int main(void) {
    pid_t pid = fork();
    if (pid == 0) {
        printf("子进程工作中...\n");
        return 42;
    }
    int status;
    waitpid(pid, &status, 0);  // 阻塞等待子进程结束
    if (WIFEXITED(status)) {
        printf("子进程退出码: %d\n", WEXITSTATUS(status));
    }
    return 0;
}
```

## exec 族函数

exec 用新程序替换当前进程映像。调用成功后原代码不再执行。

```c
#include <unistd.h>
#include <stdio.h>

int main(void) {
    char *args[] = {"ls", "-l", NULL};
    execvp("ls", args);
    // 仅在 exec 失败时执行到此
    perror("execvp");
    return 1;
}
```

常用变体：`execl`（参数列表）、`execvp`（数组 + PATH 搜索）、`execve`（可传环境变量）。

## fork + exec 组合模式

经典模式：fork 创建子进程，子进程 exec 执行外部命令，父进程 wait 回收。

```c
#include <unistd.h>
#include <sys/wait.h>
#include <stdio.h>

void run_command(char *args[]) {
    pid_t pid = fork();
    if (pid == 0) {
        execvp(args[0], args);
        perror("execvp");
        _exit(127);
    }
    int status;
    waitpid(pid, &status, 0);
    printf("命令退出码: %d\n", WEXITSTATUS(status));
}

int main(void) {
    char *cmd[] = {"echo", "hello from child", NULL};
    run_command(cmd);
    return 0;
}
```

## 进程退出

`exit(n)` 会刷新 stdio 缓冲区并执行 `atexit` 注册的清理函数；`_exit(n)` 立即退出，不做任何清理。子进程 exec 失败时应使用 `_exit` 避免重复刷新父进程的缓冲区。

```c
#include <stdlib.h>
#include <stdio.h>

void cleanup(void) {
    printf("清理资源...\n");
}

int main(void) {
    atexit(cleanup);       // 注册清理函数，exit 时自动调用
    printf("正常退出\n");
    exit(0);               // 触发 cleanup
}
```

## 环境变量

进程从父进程继承环境变量，可通过 `getenv`/`setenv` 读写。

```c
#include <stdlib.h>
#include <stdio.h>

int main(void) {
    const char *home = getenv("HOME");
    if (home) printf("HOME=%s\n", home);

    setenv("MY_VAR", "hello", 1);  // 1 表示覆盖已有值
    printf("MY_VAR=%s\n", getenv("MY_VAR"));
    return 0;
}
```

`setenv` 仅影响当前进程及其子进程，不会改变父进程或系统环境。

## 动手练习

实现一个迷你 shell：循环读取用户输入，用空格分词后 fork + execvp 执行命令，输入 `exit` 时退出。
