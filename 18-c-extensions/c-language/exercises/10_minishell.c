/*
 * 练习 10: 迷你 Shell
 * 实现一个最小交互式 shell，支持外部命令执行和内建命令。
 * 编译: clang -std=c17 -Wall -Wextra -Wpedantic -o minishell 10_minishell.c
 *
 * 本练习涉及: fork / execvp / waitpid / chdir (第15章内容)
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

#define MAX_LINE 1024   /* 输入行最大长度 */
#define MAX_ARGS 64     /* 命令参数最大数量 */

/*
 * parse_line: 将输入行按空格拆分为 argv 数组
 * 返回 token 数量，argv 以 NULL 结尾
 */
static int parse_line(char *line, char *argv[]) {
    /* TODO: 使用 strtok 按空格/制表符/换行符拆分 line
     *       将每个 token 存入 argv[]，最多 MAX_ARGS - 1 个
     *       末尾设置 argv[count] = NULL
     *       返回 token 数量 */
    (void)line;
    (void)argv;
    return 0;
}

/*
 * execute_command: 使用 fork + execvp 执行外部命令
 * 父进程等待子进程结束
 */
static void execute_command(char *argv[]) {
    /* TODO: 1. 调用 fork() 创建子进程
     *       2. 子进程中调用 execvp(argv[0], argv)
     *       3. 如果 execvp 失败，用 perror 打印错误并 _exit(EXIT_FAILURE)
     *       4. 父进程调用 waitpid 等待子进程
     *       5. fork 失败时打印错误信息 */
    (void)argv;
}

int main(void) {
    char line[MAX_LINE];
    char *argv[MAX_ARGS];

    for (;;) {
        /* 打印提示符 */
        printf("> ");
        fflush(stdout);

        /* TODO: 用 fgets 读取一行，如果返回 NULL (EOF) 则退出循环 */

        /* TODO: 调用 parse_line 解析命令行，如果没有 token 则 continue */

        /* TODO: 处理内建命令 "exit" —— 直接 break 退出循环 */

        /* TODO: 处理内建命令 "cd" —— 调用 chdir(argv[1])
         *       如果参数缺失或 chdir 失败，打印错误信息 */

        /* TODO: 其他命令调用 execute_command */
    }

    printf("\n");
    return 0;
}
