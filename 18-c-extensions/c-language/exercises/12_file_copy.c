/*
 * 练习 12: 使用 POSIX 系统调用复制文件
 * 编译: clang -std=c17 -Wall -Wextra -Wpedantic -o file_copy 12_file_copy.c
 *
 * 要求:
 *   1. 解析命令行参数: 源文件路径 和 目标文件路径
 *   2. 用 open() 只读打开源文件
 *   3. 用 open() 创建目标文件 (写入|创建|截断, 权限 0644)
 *   4. 循环 read()/write() 拷贝数据，处理部分写入
 *   5. 关闭两个文件描述符
 *   6. 每次系统调用都检查返回值，失败时 perror 并退出
 *   7. 最后打印已复制的总字节数
 */

#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define BUF_SIZE 4096

int main(int argc, char *argv[]) {
    /* TODO: 检查参数数量，不正确时打印用法并退出 */

    /* TODO: 用 open() 只读方式打开源文件，失败时 perror 并退出 */

    /* TODO: 用 open() 创建/截断目标文件，权限 0644，失败时关闭源 fd 并退出 */

    /* TODO: 声明缓冲区 buf[BUF_SIZE]，以及记录总字节数的变量 */

    /* TODO: 读循环 —— read() 返回值 > 0 时继续 */
    /*   TODO: 写循环 —— 处理 write() 可能的部分写入 */
    /*   TODO: 累加已复制字节数 */

    /* TODO: 检查 read() 是否因错误退出 (返回 -1) */

    /* TODO: 关闭两个文件描述符，检查返回值 */

    /* TODO: 打印 "Copied %zd bytes.\n" */

    printf("TODO: file copy (argc=%d, program=%s)\n", argc, argv[0]);
    return 0;
}
