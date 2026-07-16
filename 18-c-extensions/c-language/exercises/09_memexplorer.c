/*
 * 练习 09 — 内存布局探索器
 * 编译: clang -std=c17 -Wall -Wextra -Wpedantic -o memexplorer 09_memexplorer.c
 *
 * 目标: 通过打印地址和计算来验证经典进程内存布局的若干假设。
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

/* ===== 全局变量 (用于展示 data/bss 段) ===== */
int g_initialized = 42;   /* data 段 */
int g_uninitialized;       /* bss 段 */

/* ===== 结构体填充验证 ===== */
struct Padded {
    char  a;   /* 1 字节 */
    int   b;   /* 4 字节 */
    char  c;   /* 1 字节 */
};

/* ---------- TODO 1: 打印各段地址 ---------- */
static void print_segments(void) {
    /* TODO: 打印 text 段 (函数地址)、data 段 (g_initialized)、
     *       bss 段 (g_uninitialized)、stack (局部变量)、heap (malloc) 地址。
     *       使用 %p 格式化指针。 */
}

/* ---------- TODO 2: 验证栈向低地址增长 ---------- */
static void stack_grows_down(int depth, void *prev_addr) {
    /* TODO: 声明一个局部变量，打印其地址。
     *       与 prev_addr 比较，验证地址递减。
     *       递归调用自身 (depth > 0 时)。 */
}

/* ---------- TODO 3: 验证堆向高地址增长 ---------- */
static void heap_grows_up(void) {
    /* TODO: 连续 malloc 三次 (小块内存)，打印每次返回的地址。
     *       验证后续地址 >= 前一次地址。
     *       记得 free。 */
}

/* ---------- TODO 4: 计算结构体填充 ---------- */
static void struct_padding(void) {
    /* TODO: 预测 struct Padded 的 sizeof (考虑对齐)。
     *       打印实际 sizeof 和各成员的 offsetof。
     *       对比预测与实际。 */
}

/* ---------- TODO 5: 栈深度计数器 ---------- */
static int stack_depth_counter(int current) {
    /* TODO: 递归调用自身，每次 current + 1。
     *       当 current >= 10000 时停止并返回 current。
     *       (在真实系统中用于估算栈空间大小) */
    return current;
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
