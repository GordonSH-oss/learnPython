/*
 * 练习 08: 位操作 — 文件权限系统
 * 编译: clang -std=c17 -Wall -Wextra -Wpedantic -o 08_bitflags 08_bitflags.c
 *
 * 要求:
 *   1. 用位移定义权限常量 (READ, WRITE, EXEC)
 *   2. 实现 set / clear / check / toggle / to_string 五个函数
 *   3. main() 中的测试全部通过
 */
#include <stdint.h>
#include <stdio.h>

/* TODO: 用位移运算定义权限常量（提示：1<<0, 1<<1, 1<<2） */
#define PERM_READ   0  /* 修改此值 */
#define PERM_WRITE  0  /* 修改此值 */
#define PERM_EXEC   0  /* 修改此值 */

/* 设置权限位 */
static uint8_t permissions_set(uint8_t flags, uint8_t perm) {
    /* TODO: 返回设置了 perm 位后的 flags */
    (void)flags; (void)perm;
    return 0;
}

/* 清除权限位 */
static uint8_t permissions_clear(uint8_t flags, uint8_t perm) {
    /* TODO: 返回清除了 perm 位后的 flags */
    (void)flags; (void)perm;
    return 0;
}

/* 检查权限位是否已设置，返回非零表示已设置 */
static int permissions_check(uint8_t flags, uint8_t perm) {
    /* TODO: 检查 flags 中是否包含 perm */
    (void)flags; (void)perm;
    return 0;
}

/* 切换权限位 */
static uint8_t permissions_toggle(uint8_t flags, uint8_t perm) {
    /* TODO: 翻转 perm 对应的位 */
    (void)flags; (void)perm;
    return 0;
}

/* 将权限转换为 "rwx" 格式字符串，buf 至少 4 字节 */
static void permissions_to_string(uint8_t flags, char buf[4]) {
    /* TODO: 有权限显示字母，无权限显示 '-'，例如 "rw-" */
    (void)flags; (void)buf;
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
