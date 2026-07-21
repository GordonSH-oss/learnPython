/**
 * 14_memory_layout.c - 观察当前进程中的内存地址与结构体布局
 * 编译: clang -std=c17 -Wall -Wextra -Wpedantic -g 14_memory_layout.c -o 14_memory_layout
 */
#include <stddef.h>
#include <stdalign.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int g_initialized = 42;
int g_uninitialized;
static const char g_read_only[] = "read only";

static void inspect_addresses(void) {
    int automatic = 99;
    int *allocated = malloc(sizeof *allocated);
    if (allocated == NULL) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }

    *allocated = 123;
    printf("=== 本次运行观察到的地址 ===\n");
    printf("已初始化全局对象:   %p\n", (void *)&g_initialized);
    printf("零初始化全局对象:   %p\n", (void *)&g_uninitialized);
    printf("只读字符数组:       %p\n", (const void *)g_read_only);
    printf("动态分配对象:       %p\n", (void *)allocated);
    printf("自动存储期对象:     %p\n", (void *)&automatic);
    printf("这些地址只描述当前系统、构建和本次运行。\n");

    free(allocated);
}

static void inspect_call_frames(int depth) {
    volatile int local = depth;
    printf("调用深度 %d: %p\n", depth, (const void *)&local);
    if (depth < 4) {
        inspect_call_frames(depth + 1);
    }
}

struct Padded {
    char a;
    int b;
    char c;
};

struct Reordered {
    int b;
    char a;
    char c;
};

static void inspect_struct_layout(void) {
    printf("\n=== 结构体布局 ===\n");
    printf("Padded: size=%zu align=%zu offsets=(%zu, %zu, %zu)\n",
           sizeof(struct Padded), alignof(struct Padded),
           offsetof(struct Padded, a), offsetof(struct Padded, b),
           offsetof(struct Padded, c));
    printf("Reordered: size=%zu align=%zu offsets=(%zu, %zu, %zu)\n",
           sizeof(struct Reordered), alignof(struct Reordered),
           offsetof(struct Reordered, b), offsetof(struct Reordered, a),
           offsetof(struct Reordered, c));
    printf("具体大小和偏移由当前平台的 ABI 决定。\n");
}

static void inspect_page_size(void) {
    long page_size = sysconf(_SC_PAGESIZE);
    printf("\n=== 虚拟内存页 ===\n");
    if (page_size == -1) {
        perror("sysconf");
        return;
    }
    printf("当前系统页大小: %ld bytes\n", page_size);
}

int main(void) {
    inspect_addresses();

    printf("\n=== 递归调用中的局部对象地址 ===\n");
    inspect_call_frames(0);
    printf("地址变化方向是当前 ABI 和编译结果的观察值，不是 C 标准保证。\n");

    inspect_struct_layout();
    inspect_page_size();
    return 0;
}
