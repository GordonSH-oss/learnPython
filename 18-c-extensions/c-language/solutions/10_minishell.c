/*
 * 练习 10 参考答案: 迷你 Shell
 * 实现一个最小交互式 shell，支持外部命令和内建命令 (exit, cd)。
 * 编译: clang -std=c17 -Wall -Wextra -Wpedantic -o minishell 10_minishell.c
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/wait.h>

#define MAX_LINE 1024   /* 输入行最大长度 */
#define MAX_ARGS 64     /* 命令参数最大数量 */

/* 将输入行按空白字符拆分为 argv 数组，返回 token 数量 */
static int parse_line(char *line, char *argv[]) {
    int count = 0;
    char *token = strtok(line, " \t\n");

    while (token != NULL && count < MAX_ARGS - 1) {
        argv[count++] = token;
        token = strtok(NULL, " \t\n");
    }
    argv[count] = NULL;  /* execvp 要求以 NULL 结尾 */
    return count;
}

/* 使用 fork + execvp 执行外部命令，父进程等待子进程结束 */
static int execute_command(char *argv[]) {
    pid_t pid = fork();

    if (pid < 0) {
        perror("minishell: fork");
        return -1;
    }

    if (pid == 0) {
        /* 子进程: 执行命令 */
        execvp(argv[0], argv);
        /* execvp 仅在失败时返回 */
        perror(argv[0]);
        _exit(127);
    }

    /* 父进程: 等待子进程结束 */
    int status;
    pid_t waited;
    do {
        waited = waitpid(pid, &status, 0);
    } while (waited == -1 && errno == EINTR);
    if (waited == -1) {
        perror("minishell: waitpid");
        return -1;
    }
    if (WIFSIGNALED(status)) {
        fprintf(stderr, "minishell: terminated by signal %d\n", WTERMSIG(status));
    }
    return 0;
}

int main(void) {
    char line[MAX_LINE];
    char *argv[MAX_ARGS];

    for (;;) {
        /* 打印提示符并刷新输出缓冲区 */
        printf("> ");
        fflush(stdout);

        /* 读取一行输入，EOF 时退出 */
        if (fgets(line, MAX_LINE, stdin) == NULL) {
            if (ferror(stdin)) perror("minishell: stdin");
            break;
        }

        if (strchr(line, '\n') == NULL && !feof(stdin)) {
            int character;
            while ((character = getchar()) != '\n' && character != EOF) {}
            fputs("minishell: input line too long\n", stderr);
            continue;
        }

        /* 解析命令行 */
        int argc = parse_line(line, argv);
        if (argc == 0) {
            continue;  /* 空行，重新读取 */
        }

        /* 内建命令: exit */
        if (strcmp(argv[0], "exit") == 0) {
            break;
        }

        /* 内建命令: cd */
        if (strcmp(argv[0], "cd") == 0) {
            if (argv[1] == NULL) {
                fprintf(stderr, "minishell: cd 需要目标目录参数\n");
            } else if (chdir(argv[1]) != 0) {
                perror("minishell: cd");
            }
            continue;
        }

        /* 外部命令: fork + execvp */
        execute_command(argv);
    }

    printf("\n");
    return 0;
}
