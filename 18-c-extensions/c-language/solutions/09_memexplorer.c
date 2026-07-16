/*
 * 解答 09 — 内存布局探索器
 * 编译: clang -std=c17 -Wall -Wextra -Wpedantic -o memexplorer 09_memexplorer.c
 */
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

/* 全局变量: data 段 (已初始化) 与 bss 段 (未初始化) */
int g_initialized = 42;
int g_uninitialized;

/* 用于验证填充的结构体 */
struct Padded {
    char a;   /* 1 字节 */
    int  b;   /* 4 字节 */
    char c;   /* 1 字节 */
};

/* ---------- 1. 打印各段地址 ---------- */
static void print_segments(void) {
    int stack_var = 0;
    int *heap_var = malloc(sizeof(int));
    printf("  text  (print_segments): %p\n", (void *)(uintptr_t)print_segments);
    printf("  data  (g_initialized): %p\n", (void *)&g_initialized);
    printf("  bss   (g_uninitialized): %p\n", (void *)&g_uninitialized);
    printf("  stack (局部变量):      %p\n", (void *)&stack_var);
    printf("  heap  (malloc):        %p\n", (void *)heap_var);
    free(heap_var);
}

/* ---------- 2. 验证栈向低地址增长 ---------- */
static void stack_grows_down(int depth, void *prev_addr) {
    int local;
    uintptr_t cur = (uintptr_t)&local;
    uintptr_t pre = (uintptr_t)prev_addr;
    printf("  depth=%d addr=%p %s\n", depth, (void *)&local,
           cur < pre ? "(低于上层 ✓)" : "(高于上层 ✗)");
    if (depth > 0)
        stack_grows_down(depth - 1, &local);
}

/* ---------- 3. 验证堆向高地址增长 ---------- */
static void heap_grows_up(void) {
    void *p1 = malloc(32);
    void *p2 = malloc(32);
    void *p3 = malloc(32);
    printf("  p1=%p\n  p2=%p %s\n  p3=%p %s\n",
           p1, p2,
           (uintptr_t)p2 >= (uintptr_t)p1 ? "(>= p1 ✓)" : "(< p1 ✗)",
           p3,
           (uintptr_t)p3 >= (uintptr_t)p2 ? "(>= p2 ✓)" : "(< p2 ✗)");
    free(p1); free(p2); free(p3);
}

/* ---------- 4. 结构体填充计算 ---------- */
static void struct_padding(void) {
    /* 预测: char(1) + 填充(3) + int(4) + char(1) + 填充(3) = 12 */
    printf("  预测 sizeof(struct Padded) = 12\n");
    printf("  实际 sizeof(struct Padded) = %zu\n", sizeof(struct Padded));
    printf("  offsetof(a) = %zu\n", offsetof(struct Padded, a));
    printf("  offsetof(b) = %zu\n", offsetof(struct Padded, b));
    printf("  offsetof(c) = %zu\n", offsetof(struct Padded, c));
}

/* ---------- 5. 栈深度计数器 ---------- */
static int stack_depth_counter(int current) {
    if (current >= 10000)
        return current;
    return stack_depth_counter(current + 1);
}

/* ===== main ===== */
int main(void) {
    printf("===== 内存布局探索器 =====\n\n");

    printf("[1] 各段地址:\n");
    print_segments();

    printf("\n[2] 验证栈向低地址增长:\n");
    int local;
    stack_grows_down(3, &local);

    printf("\n[3] 验证堆向高地址增长:\n");
    heap_grows_up();

    printf("\n[4] 结构体填充:\n");
    struct_padding();

    printf("\n[5] 栈深度计数器:\n");
    int depth = stack_depth_counter(0);
    printf("  达到递归深度: %d\n", depth);

    return 0;
}
