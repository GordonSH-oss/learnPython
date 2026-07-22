/*
 * 练习 06c: 指针陷阱与调试 — 参考答案
 * 编译: gcc -Wall -Wextra -g -fsanitize=address 06_pointer_pitfalls.c -o 06_pointer_pitfalls
 *
 * 修复说明：每个函数的 bug 都已修复，注释中说明了原始错误
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ========== 陷阱 1: 悬垂指针 (Dangling Pointer) ========== */
/* 原 BUG: 返回了局部变量的地址
 * 修复方法 1: 使用 static 变量（本例）
 * 修复方法 2: 让调用者传入指针
 * 修复方法 3: 返回 malloc 分配的内存（需调用者 free）
 */
static int *dangling_example(void) {
    static int local = 42;  /* static 存储期，生命周期延续到程序结束 */
    return &local;
}

/* ========== 陷阱 2: 越界访问 (Out-of-Bounds) ========== */
/* 原 BUG: i <= 5 导致访问 arr[5]，越界 */
static void oob_example(void) {
    int arr[5] = {10, 20, 30, 40, 50};
    for (int i = 0; i < 5; i++) {  /* 修复: < 而非 <= */
        printf("arr[%d] = %d\n", i, arr[i]);
    }
}

/* ========== 陷阱 3: 未初始化指针 ========== */
/* 原 BUG: 指针未初始化就解引用，指向随机地址 */
static void uninit_example(void) {
    int value = 123;
    int *p = &value;  /* 修复: 给 p 赋一个有效地址 */
    printf("value = %d\n", *p);
}

/* ========== 陷阱 4: 内存泄漏 ========== */
/* 原 BUG: n > 100 时提前返回，buf 未释放 */
static int leak_example(int n) {
    int *buf = malloc(sizeof(int) * (size_t)n);
    if (buf == NULL) return -1;

    for (int i = 0; i < n; i++)
        buf[i] = i * i;

    if (n > 100) {
        free(buf);  /* 修复: 在所有返回路径前释放 */
        return -2;
    }

    int sum = 0;
    for (int i = 0; i < n; i++)
        sum += buf[i];

    free(buf);
    return sum;
}

/* ========== 陷阱 5: Use-After-Free ========== */
/* 原 BUG: free 后仍然解引用 msg */
static void uaf_example(void) {
    char *msg = malloc(32);
    if (!msg) return;
    strcpy(msg, "hello");
    printf("msg = %s\n", msg);  /* 修复: 在 free 之前使用 */
    free(msg);
}

/* ========== 陷阱 6: 指针类型混淆 ========== */
/* 演示字节序：x86 是小端序，低字节存在低地址 */
static void type_confusion(void) {
    int value = 0x41424344;  /* 'A'=0x41, 'B'=0x42, 'C'=0x43, 'D'=0x44 */
    char *cp = (char *)&value;

    printf("int 值: 0x%08X\n", value);
    printf("字节序（从低地址到高地址）: ");
    for (int i = 0; i < 4; i++)
        printf("0x%02X ", (unsigned char)cp[i]);
    printf("\n");

    printf("\n解释:\n");
    printf("  x86 小端序: 最低有效字节 (0x44='D') 存在最低地址\n");
    printf("  cp[0]=0x44, cp[1]=0x43, cp[2]=0x42, cp[3]=0x41\n");
    printf("  所以第一个字节不是 0x41，而是 0x44\n");
}

int main(void) {
    printf("===== 陷阱 1: 悬垂指针 =====\n");
    int *p = dangling_example();
    printf("*p = %d (期望: 42)\n\n", *p);

    printf("===== 陷阱 2: 越界访问 =====\n");
    oob_example();
    printf("\n");

    printf("===== 陷阱 3: 未初始化指针 =====\n");
    uninit_example();
    printf("\n");

    printf("===== 陷阱 4: 内存泄漏 =====\n");
    printf("sum(5) = %d (期望: 30)\n", leak_example(5));
    printf("sum(200) = %d (期望: -2, 无泄漏)\n\n", leak_example(200));

    printf("===== 陷阱 5: Use-After-Free =====\n");
    uaf_example();
    printf("\n");

    printf("===== 陷阱 6: 类型混淆与字节序 =====\n");
    type_confusion();

    return 0;
}
