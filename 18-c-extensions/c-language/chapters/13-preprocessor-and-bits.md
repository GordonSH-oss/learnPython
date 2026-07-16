# 13 预处理器与位操作

## 学习目标

掌握宏与条件编译的常用模式，熟练使用位运算处理标志位和底层数据。

## 宏定义与带参数宏

```c
#define PI 3.14159265
#define MAX(a, b) ((a) > (b) ? (a) : (b))

// do-while(0) 包装多语句宏，确保在 if/else 中安全使用
#define LOG_AND_RETURN(val) do { \
    printf("returning %d\n", (val));  \
    return (val);                     \
} while (0)
```

## 可变参数宏

```c
#define DEBUG_FMT(fmt, ...) \
    fprintf(stderr, "[DEBUG] " fmt "\n", __VA_ARGS__)

// C23/GNU 扩展：##__VA_ARGS__ 允许零参数
#define LOG(fmt, ...) \
    fprintf(stderr, "[%s:%d] " fmt "\n", __FILE__, __LINE__, ##__VA_ARGS__)
```

## 条件编译

```c
#ifndef HEADER_GUARD_H
#define HEADER_GUARD_H
// 头文件内容
#endif

#ifdef DEBUG
    #define TRACE(msg) puts(msg)
#else
    #define TRACE(msg) ((void)0)
#endif

// 平台检测
#if defined(_WIN32)
    #include <windows.h>
#elif defined(__linux__)
    #include <unistd.h>
#elif defined(__APPLE__)
    #include <mach/mach.h>
#endif
```

## X-Macro 模式

用一份列表同时生成枚举值和字符串映射，避免手动同步：

```c
#define COLOR_LIST \
    X(RED)         \
    X(GREEN)       \
    X(BLUE)

// 生成枚举
typedef enum {
    #define X(name) COLOR_##name,
    COLOR_LIST
    #undef X
    COLOR_COUNT
} Color;

// 生成字符串数组
static const char *color_names[] = {
    #define X(name) [COLOR_##name] = #name,
    COLOR_LIST
    #undef X
};
```

## 位运算符

```c
unsigned a = 0b1100, b = 0b1010;
a & b;   // AND  -> 0b1000
a | b;   // OR   -> 0b1110
a ^ b;   // XOR  -> 0b0110
~a;      // NOT  -> 取反所有位
a << 2;  // 左移 -> 0b110000
a >> 1;  // 右移 -> 0b0110
```

## 位掩码与标志位

```c
#define FLAG_READ    (1u << 0)  // 0x01
#define FLAG_WRITE   (1u << 1)  // 0x02
#define FLAG_EXEC    (1u << 2)  // 0x04

unsigned perms = 0;
perms |= FLAG_READ;              // 设置
perms |= (FLAG_WRITE | FLAG_EXEC);
perms &= ~FLAG_EXEC;            // 清除
perms ^= FLAG_WRITE;            // 翻转
if (perms & FLAG_READ) { /* 检测 */ }
```

## 位域

```c
struct PacketHeader {
    unsigned version : 4;   // 4 bits, 0-15
    unsigned type    : 4;
    unsigned length  : 8;
    unsigned flags   : 16;
};  // 总共 32 bits = 4 字节

struct PacketHeader hdr = { .version = 1, .type = 3, .length = 64, .flags = 0 };
```

注意：位域的内存布局依赖实现，不适合直接映射网络协议字节序。

## 实用技巧

```c
// 判断是否为 2 的幂（n > 0）
int is_power_of_2(unsigned n) {
    return n && !(n & (n - 1));
}

// 向上对齐到 align（align 必须为 2 的幂）
size_t align_up(size_t n, size_t align) {
    return (n + align - 1) & ~(align - 1);
}

// 不用临时变量交换两个整数
void swap(int *a, int *b) {
    *a ^= *b;
    *b ^= *a;
    *a ^= *b;
}
```
