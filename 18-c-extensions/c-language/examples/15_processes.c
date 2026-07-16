/**
 * 15_processes.c - POSIX 进程操作示例
 * 编译: clang -std=c17 -Wall -Wextra -Wpedantic 15_processes.c -o 15_processes
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

/* 演示 fork + wait */
void demo_fork_wait(void) {
    printf("\n--- fork() + wait() ---\n");
    pid_t pid = fork();

    if (pid < 0) {
        perror("fork 失败");
        exit(EXIT_FAILURE);
    } else if (pid == 0) {
        /* 子进程 */
        printf("[子进程] PID=%d, 父进程PID=%d\n", getpid(), getppid());
        printf("[子进程] 执行一些工作...\n");
        _exit(42);  /* 子进程退出，返回码42 */
    } else {
        /* 父进程 */
        printf("[父进程] 创建子进程 PID=%d\n", pid);
        int status;
        waitpid(pid, &status, 0);
        if (WIFEXITED(status)) {
            printf("[父进程] 子进程退出码: %d\n", WEXITSTATUS(status));
        }
    }
}

/* 演示 fork + exec */
void demo_fork_exec(void) {
    printf("\n--- fork() + execvp() ---\n");
    pid_t pid = fork();

    if (pid < 0) {
        perror("fork 失败");
        exit(EXIT_FAILURE);
    } else if (pid == 0) {
        /* 子进程: 用 execvp 执行 echo 命令 */
        char *args[] = {"echo", "[exec] 子进程通过 execvp 运行 echo", NULL};
        execvp("echo", args);
        perror("execvp 失败");  /* 仅在exec失败时执行 */
        _exit(EXIT_FAILURE);
    } else {
        int status;
        waitpid(pid, &status, 0);
        printf("[父进程] exec子进程已结束\n");
    }
}

/* 演示环境变量 */
void demo_env(void) {
    printf("\n--- 环境变量 ---\n");
    const char *home = getenv("HOME");
    const char *path = getenv("PATH");
    printf("HOME = %s\n", home ? home : "(未设置)");
    printf("PATH = %.60s...\n", path ? path : "(未设置)");
}

int main(void) {
    printf("=== POSIX 进程操作 ===\n");

    /* 1. 当前进程信息 */
    printf("\n--- 进程信息 ---\n");
    printf("当前进程 PID: %d\n", getpid());
    printf("父进程 PPID:  %d\n", getppid());

    /* 2. fork + wait */
    demo_fork_wait();

    /* 3. fork + exec */
    demo_fork_exec();

    /* 4. 环境变量 */
    demo_env();

    printf("\n=== 完成 ===\n");
    return 0;
}
