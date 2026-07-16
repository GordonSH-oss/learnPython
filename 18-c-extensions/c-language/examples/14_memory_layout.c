/**
 * 14_memory_layout.c - 内存布局演示
 * 编译: clang -std=c17 -Wall -Wextra -Wpedantic 14_memory_layout.c -o 14_memory_layout
 */
#include <stdio.h>
#include <stdlib.h>

/* ===== 1. 各段变量地址 ===== */
int g_var = 42;                    // 全局变量 (数据段)
int g_uninit;                      // 未初始化全局 (BSS段)

void show_segments(void) {
    static int s_var = 10;         // 静态变量 (数据段)
    int local = 99;                // 局部变量 (栈)
    int *heap = malloc(sizeof(int));
    printf("=== 内存段地址 ===\n");
    printf("代码段 (函数地址):  %p\n", (void *)show_segments);
    printf("数据段 (全局变量):  %p\n", (void *)&g_var);
    printf("BSS段 (未初始化):   %p\n", (void *)&g_uninit);
    printf("数据段 (静态变量):  %p\n", (void *)&s_var);
    printf("栈 (局部变量):      %p\n", (void *)&local);
    printf("堆 (malloc):        %p\n", (void *)heap);
    free(heap);
}

/* ===== 2. 栈增长方向 ===== */
void stack_depth(int depth, void *prev_addr) {
    int local;
    void *curr = &local;
    if (depth == 0) printf("\n=== 栈增长方向 ===\n");
    if (depth < 4) {
        printf("深度%d: %p (差值: %+ld)\n", depth, curr,
               prev_addr ? (long)((char*)curr - (char*)prev_addr) : 0L);
        stack_depth(depth + 1, curr);
    } else {
        printf("结论: 栈向%s增长\n", (curr < prev_addr) ? "低地址" : "高地址");
    }
}

/* ===== 3. 堆增长方向 ===== */
void show_heap_growth(void) {
    printf("\n=== 堆增长方向 ===\n");
    void *ptrs[4];
    for (int i = 0; i < 4; i++) {
        ptrs[i] = malloc(32);
        printf("malloc[%d]: %p", i, ptrs[i]);
        if (i > 0)
            printf(" (差值: %+ld)", (long)((char*)ptrs[i] - (char*)ptrs[i-1]));
        printf("\n");
    }
    printf("结论: 堆向高地址增长\n");
    for (int i = 0; i < 4; i++) free(ptrs[i]);
}

/* ===== 4. 结构体对齐与填充 ===== */
struct Padded { char a; int b; char c; };       // 1+3pad+4+1+3pad = 12
struct Packed { char a; char c; int b; };       // 1+1+2pad+4 = 8

void show_struct_padding(void) {
    printf("\n=== 结构体填充与对齐 ===\n");
    printf("Padded {char,int,char}: sizeof=%zu (预期6, 实际有填充)\n",
           sizeof(struct Padded));
    printf("Packed {char,char,int}: sizeof=%zu (重排后更紧凑)\n",
           sizeof(struct Packed));
    struct Padded p;
    printf("成员偏移: a=%ld, b=%ld, c=%ld\n",
           (long)((char*)&p.a - (char*)&p),
           (long)((char*)&p.b - (char*)&p),
           (long)((char*)&p.c - (char*)&p));
}

/* ===== 5. 栈溢出深度测试 (安全限制) ===== */
static int max_depth = 0;
#define SAFE_LIMIT 10000

void recurse(int depth) {
    char buf[256]; buf[0] = (char)depth; (void)buf;  // 每帧占用栈空间
    max_depth = depth;
    if (depth < SAFE_LIMIT) recurse(depth + 1);
}

void show_stack_overflow(void) {
    printf("\n=== 栈深度测试 (安全限制=%d) ===\n", SAFE_LIMIT);
    recurse(0);
    printf("达到递归深度: %d\n", max_depth);
    printf("每帧约256+字节, 估算栈使用: ~%d KB\n", max_depth * 256 / 1024);
}

/* ===== 主函数 ===== */
int main(void) {
    show_segments();
    stack_depth(0, NULL);
    show_heap_growth();
    show_struct_padding();
    show_stack_overflow();
    return 0;
}
