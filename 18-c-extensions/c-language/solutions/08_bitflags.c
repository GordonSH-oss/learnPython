/*
 * 解答 08: 位操作 — 文件权限系统
 * 编译: clang -std=c17 -Wall -Wextra -Wpedantic -o 08_bitflags 08_bitflags.c
 */
#include <stdint.h>
#include <stdio.h>

/* 权限常量：用位移定义，方便扩展 */
#define PERM_READ  (1U << 0)  /* 0b001 = 1 */
#define PERM_WRITE (1U << 1)  /* 0b010 = 2 */
#define PERM_EXEC  (1U << 2)  /* 0b100 = 4 */

/* 设置权限位：用 OR 运算 */
static uint8_t permissions_set(uint8_t flags, uint8_t perm) {
    return flags | perm;
}

/* 清除权限位：用 AND + NOT 运算 */
static uint8_t permissions_clear(uint8_t flags, uint8_t perm) {
    return flags & (uint8_t)~perm;
}

/* 检查权限位是否已设置 */
static int permissions_check(uint8_t flags, uint8_t perm) {
    return (flags & perm) != 0;
}

/* 切换权限位：用 XOR 运算 */
static uint8_t permissions_toggle(uint8_t flags, uint8_t perm) {
    return flags ^ perm;
}

/* 将权限转换为 "rwx" 格式字符串，buf 至少 4 字节 */
static void permissions_to_string(uint8_t flags, char buf[4]) {
    buf[0] = (flags & PERM_READ)  ? 'r' : '-';
    buf[1] = (flags & PERM_WRITE) ? 'w' : '-';
    buf[2] = (flags & PERM_EXEC)  ? 'x' : '-';
    buf[3] = '\0';
}

int main(void) {
    uint8_t perms = 0;
    char buf[4];

    /* 测试 set */
    perms = permissions_set(perms, PERM_READ);
    perms = permissions_set(perms, PERM_WRITE);
    permissions_to_string(perms, buf);
    printf("set R+W:    %s (期望 rw-)\n", buf);

    /* 测试 check */
    printf("has READ?   %s (期望 yes)\n", permissions_check(perms, PERM_READ) ? "yes" : "no");
    printf("has EXEC?   %s (期望 no)\n", permissions_check(perms, PERM_EXEC) ? "yes" : "no");

    /* 测试 toggle */
    perms = permissions_toggle(perms, PERM_EXEC);
    permissions_to_string(perms, buf);
    printf("toggle +X:  %s (期望 rwx)\n", buf);

    perms = permissions_toggle(perms, PERM_WRITE);
    permissions_to_string(perms, buf);
    printf("toggle -W:  %s (期望 r-x)\n", buf);

    /* 测试 clear */
    perms = permissions_clear(perms, PERM_READ);
    permissions_to_string(perms, buf);
    printf("clear R:    %s (期望 --x)\n", buf);

    return 0;
}
