# 14 内存布局与虚拟内存

## 学习目标

理解进程地址空间的各段布局，掌握栈帧、堆分配和虚拟内存的工作方式。

## 进程地址空间

典型 Linux/macOS 进程从低地址到高地址依次为：text（代码段）、data（已初始化全局变量）、bss（未初始化全局变量）、heap（向高地址增长）、stack（向低地址增长）。

```c
#include <stdio.h>
#include <stdlib.h>

int global_init = 42;       // data 段
int global_uninit;           // bss 段

int main(void) {
    int local = 1;           // stack
    int *heap_ptr = malloc(sizeof(int)); // heap
    printf("text:  %p\n", (void *)main);
    printf("data:  %p\n", (void *)&global_init);
    printf("bss:   %p\n", (void *)&global_uninit);
    printf("heap:  %p\n", (void *)heap_ptr);
    printf("stack: %p\n", (void *)&local);
    free(heap_ptr);
    return 0;
}
```

运行后可观察到地址从低到高的排列顺序。

## 栈帧结构

每次函数调用会在栈上压入一个栈帧，包含：局部变量、保存的寄存器、返回地址。

```c
#include <stdio.h>

void show_stack_growth(int depth) {
    int local;
    printf("depth %d: &local = %p\n", depth, (void *)&local);
    if (depth < 5)
        show_stack_growth(depth + 1);
}

int main(void) {
    show_stack_growth(0);
    return 0;
}
```

输出会显示地址递减——栈向低地址增长。

## 堆的工作原理

`malloc` 底层通过两种系统调用获取内存：小块用 `brk`/`sbrk` 扩展数据段；大块（通常 >= 128KB）用 `mmap` 直接映射。分配器维护空闲链表，频繁 malloc/free 不同大小的块会产生内存碎片。

```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    // 演示碎片：交替分配释放不同大小
    void *a = malloc(32);
    void *b = malloc(1024);
    void *c = malloc(32);
    free(b);  // 中间空洞，后续 1024 字节请求可复用，但更大的不行
    void *d = malloc(2048); // 可能无法填入 b 的空洞
    printf("a=%p b_freed c=%p d=%p\n", a, c, d);
    free(a); free(c); free(d);
    return 0;
}
```

## 虚拟内存概念

每个进程拥有独立的虚拟地址空间。CPU 通过页表将虚拟页映射到物理页帧，页大小通常为 4KB。两个进程中相同的指针值指向不同的物理内存。

```c
#include <stdio.h>
#include <unistd.h>

int main(void) {
    int x = 100;
    pid_t pid = fork();
    if (pid == 0) {
        x = 200;
        printf("child:  &x=%p x=%d\n", (void *)&x, x);
    } else {
        printf("parent: &x=%p x=%d\n", (void *)&x, x);
    }
    return 0;
}
```

父子进程中 `&x` 相同，但值不同——虚拟地址相同，物理页已因写时复制(COW)而分离。

## 栈溢出实验

栈大小有限（默认通常 8MB），无限递归会触发 stack overflow。

```c
#include <stdio.h>

void overflow(int n) {
    char buf[4096]; // 每帧占 4KB
    printf("depth %d\n", n);
    overflow(n + 1);
}

int main(void) {
    overflow(0);
    return 0;
}
```

```bash
# 查看当前栈大小限制
ulimit -s        # 输出单位为 KB，如 8192 = 8MB
# 临时缩小栈以更快触发溢出
ulimit -s 1024   # 设为 1MB
./a.out
```

程序将在约 `栈大小 / 每帧大小` 次递归后收到 SIGSEGV。

## 内存对齐

CPU 访问对齐地址最高效。编译器在 struct 成员间插入 padding 保证对齐。

```c
#include <stdio.h>
#include <stdalign.h>

struct Bad {
    char a;   // 1 byte + 3 padding
    int  b;   // 4 bytes
    char c;   // 1 byte + 3 padding
};            // 总共 12 bytes

struct Good {
    int  b;   // 4 bytes
    char a;   // 1 byte
    char c;   // 1 byte + 2 padding
};            // 总共 8 bytes

int main(void) {
    printf("Bad:  size=%zu align=%zu\n", sizeof(struct Bad), alignof(struct Bad));
    printf("Good: size=%zu align=%zu\n", sizeof(struct Good), alignof(struct Good));
    return 0;
}
```

规则：将大成员放前面，小成员集中排列，可减少 padding 浪费。

## 动手练习

1. 编译并运行地址空间示例，验证各段地址的高低顺序
2. 用 `ulimit -s 512` 缩小栈后运行栈溢出程序，观察递归深度变化
3. 重新排列一个 struct 的成员顺序使其 `sizeof` 最小
