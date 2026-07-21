/*
 * 练习 06c: 指针陷阱与调试
 * 编译: gcc -Wall -Wextra -g -fsanitize=address 06_pointer_pitfalls.c -o 06_pointer_pitfalls
 * 目标: 识别常见指针错误，学会使用 AddressSanitizer 定位问题
 *
 * 使用方法:
 * 1. 先阅读每个函数，预判哪里有 bug
 * 2. 编译运行，观察 AddressSanitizer 的报错
 * 3. 修复 bug 使程序正确运行
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ========== 陷阱 1: 悬垂指针 (Dangling Pointer) ========== */
/* BUG: 返回了局部变量的地址 */
static int *dangling_example(void) {
    int local = 42;
    return &local;  /* TODO: 修复这个函数，使返回的指针有效 */
}

/* ========== 陷阱 2: 越界访问 (Out-of-Bounds) ========== */
/* BUG: 循环多走了一步 */
static void oob_example(void) {
    int arr[5] = {10, 20, 30, 40, 50};
    for (int i = 0; i <= 5; i++) {  /* TODO: 修复边界条件 */
        printf("arr[%d] = %d\n", i, arr[i]);
    }
}

/* ========== 陷阱 3: 未初始化指针 ========== */
/* BUG: 指针未初始化就解引用 */
static void uninit_example(void) {
    int *p;  /* TODO: 在使用前给 p 一个有效的值 */
    printf("value = %d\n", *p);
}

/* ========== 陷阱 4: 内存泄漏 ========== */
/* BUG: 分配了内存但提前返回导致泄漏 */
static int leak_example(int n) {
    int *buf = malloc(sizeof(int) * (size_t)n);
    if (buf == NULL) return -1;

    for (int i = 0; i < n; i++)
        buf[i] = i * i;

    if (n > 100) {
        return -2;  /* TODO: 修复此处的内存泄漏 */
    }

    int sum = 0;
    for (int i = 0; i < n; i++)
        sum += buf[i];

    free(buf);
    return sum;
}

/* ========== 陷阱 5: Use-After-Free ========== */
/* BUG: 释放后仍然使用指针 */
static void uaf_example(void) {
    char *msg = malloc(32);
    if (!msg) return;
    strcpy(msg, "hello");
    free(msg);
    printf("msg = %s\n", msg);  /* TODO: 修复 use-after-free */
}

/* ========== 陷阱 6: 指针类型混淆 ========== */
/* BUG: 把 int* 错误转为 char* 读取，字节序混乱 */
static void type_confusion(void) {
    int value = 0x41424344;
    char *cp = (char *)&value;
    /* 思考题: 在你的机器上这会打印什么？为什么？
     * 提示: x86 是小端序 (little-endian) */
    printf("bytes: ");
    for (int i = 0; i < 4; i++)
        printf("0x%02X '%c' ", (unsigned char)cp[i], cp[i]);
    printf("\n");
    printf("思考: 为什么第一个字节不是 0x41?\n");
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
