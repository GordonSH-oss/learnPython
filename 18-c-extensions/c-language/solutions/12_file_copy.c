/*
 * 练习 12 参考答案: 使用 POSIX 系统调用复制文件
 * 编译: clang -std=c17 -Wall -Wextra -Wpedantic -o file_copy 12_file_copy.c
 */

#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define BUF_SIZE 4096

int main(int argc, char *argv[]) {
    /* 检查参数 */
    if (argc != 3) {
        fprintf(stderr, "用法: %s <源文件> <目标文件>\n", argv[0]);
        return 2;
    }

    const char *src_path = argv[1];
    const char *dst_path = argv[2];

    /* 只读打开源文件 */
    int src_fd = open(src_path, O_RDONLY);
    if (src_fd < 0) {
        perror(src_path);
        return 1;
    }

    /* 创建/截断目标文件，权限 0644 */
    int dst_fd = open(dst_path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (dst_fd < 0) {
        perror(dst_path);
        close(src_fd);
        return 1;
    }

    /* 读写循环 */
    char buf[BUF_SIZE];
    ssize_t bytes_read;
    ssize_t total = 0;

    while ((bytes_read = read(src_fd, buf, BUF_SIZE)) > 0) {
        /* 处理部分写入: 确保整块数据全部写出 */
        ssize_t written = 0;
        while (written < bytes_read) {
            ssize_t w = write(dst_fd, buf + written, (size_t)(bytes_read - written));
            if (w < 0) {
                perror("write");
                close(src_fd);
                close(dst_fd);
                return 1;
            }
            written += w;
        }
        total += bytes_read;
    }

    /* 检查 read() 是否因错误退出 */
    if (bytes_read < 0) {
        perror("read");
        close(src_fd);
        close(dst_fd);
        return 1;
    }

    /* 关闭文件描述符 */
    if (close(src_fd) < 0) {
        perror("close src");
        close(dst_fd);
        return 1;
    }
    if (close(dst_fd) < 0) {
        perror("close dst");
        return 1;
    }

    printf("已复制 %zd 字节。\n", total);
    return 0;
}
