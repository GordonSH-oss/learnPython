# 13 预处理器与位操作

## 学习目标

完成本章后，你应该能够：

- 解释宏展开、条件编译和头文件保护发生在哪个阶段
- 说明每种常用预处理指令接收什么输入、产生什么结果
- 编写能正确处理参数优先级的简单宏
- 使用字符串化、token 拼接、预定义宏和 pragma
- 识别宏重复求值和非标准扩展风险
- 使用无符号整数安全操作标志位和掩码
- 说明移位、位域和对齐技巧的边界条件

## 预处理器做什么

预处理发生在真正编译之前，主要处理：

- `#include` 引入声明文本
- `#define` 宏替换
- `#if`、`#ifdef` 条件编译
- `#` 字符串化和 `##` token 拼接

可以观察展开结果：

```bash
clang -std=c17 -E examples/13_preprocessor_bits.c -o /tmp/preprocessed.i
```

宏不是函数，没有参数类型、局部作用域或普通调用语义。

## 预处理指令总览

预处理指令以 `#` 开头，通常占据一个逻辑行。反斜杠 `\` 可以把下一物理行连接进同一逻辑行。

| 指令 | 输入 | 预处理阶段产生的效果 |
| --- | --- | --- |
| `#include` | 头文件名 | 在当前位置引入头文件提供的预处理 token |
| `#define` | 宏名、可选参数和替换列表 | 建立后续宏替换规则 |
| `#undef` | 宏名 | 删除当前宏定义 |
| `#if` | 整数常量表达式 | 根据结果是否非零保留或丢弃代码 |
| `#ifdef` | 宏名 | 宏已定义时保留分支 |
| `#ifndef` | 宏名 | 宏未定义时保留分支 |
| `#elif` | 整数常量表达式 | 前面分支未选中时继续判断 |
| `#else` | 无 | 选择前面条件都未命中的分支 |
| `#endif` | 无 | 结束条件编译组 |
| `#error` | 诊断文本 | 产生编译诊断并使翻译失败 |
| `#line` | 行号和可选文件名 | 改变后续 `__LINE__`、`__FILE__` 和诊断位置 |
| `#pragma` | 实现定义参数 | 向具体编译器传递控制信息 |

预处理的直接产物仍然是 C token，不是目标文件或机器码。`clang -E` 输出的是预处理后的源代码；之后才进入语法、类型和代码生成阶段。

## `#include` 与搜索路径

两种写法表达不同的搜索意图：

```c
#include "task.h"
#include <stdio.h>
```

- `"task.h"` 通常先搜索当前源文件附近或调用者指定的项目目录，再搜索系统目录。
- `<stdio.h>` 通常直接搜索实现配置的系统头文件目录。

精确顺序由编译器实现和参数决定。项目头文件路径通常通过 `-I` 添加：

```bash
clang -std=c17 -Iinclude -c src/task.c -o task.o
```

可以让 Clang 输出头文件层次和搜索目录：

```bash
clang -std=c17 -H -c examples/13_preprocessor_bits.c -o /tmp/preprocessor.o
clang -std=c17 -E -v examples/13_preprocessor_bits.c -o /dev/null
```

`#include` 常被口语化描述为“复制文本”，但更准确的模型是：实现定位头文件，处理其中的预处理 token 和指令，并把结果纳入当前翻译单元。头文件自身也可以继续 include 其他头文件。

## 宏展开的输入与结果

对象式宏替换宏名：

```c
#define BUFFER_SIZE 256
char buffer[BUFFER_SIZE];
```

预处理后相当于：

```c
char buffer[256];
```

函数式宏只有在宏名后跟参数列表时才调用：

```c
#define SQUARE(value) ((value) * (value))
int result = SQUARE(2 + 3);
```

展开结果是：

```c
int result = ((2 + 3) * (2 + 3));
```

宏展开只是 token 替换，不会先理解表达式的类型和业务含义。

## 对象宏与函数式宏

```c
#define PI 3.141592653589793
#define MAX(a, b) ((a) > (b) ? (a) : (b))
```

参数和整个结果都要加括号，避免调用表达式改变优先级。但 `MAX` 仍有重复求值问题：

```c
int larger = MAX(i++, j++); /* 某个参数可能执行两次 */
```

需要类型检查或只求值一次时，优先使用普通函数或 `static inline` 函数：

```c
static inline int max_int(int a, int b) {
    return a > b ? a : b;
}
```

多语句宏使用 `do { ... } while (0)` 形成单条语句：

```c
#define LOG_AND_RETURN(value) do {             \
    int result_ = (value);                     \
    fprintf(stderr, "returning %d\n", result_); \
    return result_;                            \
} while (0)
```

临时名称仍可能与调用位置名称冲突，这也是复杂逻辑应使用函数的原因。

## 可变参数宏

C17 可移植写法要求 `...` 至少对应一个参数：

```c
#define DEBUG_FORMAT(format, ...) \
    fprintf(stderr, "[DEBUG] " format "\n", __VA_ARGS__)

DEBUG_FORMAT("count=%d", count);
```

GNU 的 `, ##__VA_ARGS__` 可以吞掉零参数前的逗号，但不是 C17 标准。C23 提供 `__VA_OPT__`，也不应在本课程的 C17 示例中直接使用。若需要只记录固定字符串，可以单独定义：

```c
#define DEBUG_MESSAGE(message) \
    fprintf(stderr, "[DEBUG] %s\n", (message))
```

## 字符串化 `#`

在函数式宏替换列表中，`#parameter` 把调用时传入的 token 拼成字符串字面量：

```c
#define STRINGIFY_DIRECT(value) #value

const char *text = STRINGIFY_DIRECT(hello + world);
```

展开为：

```c
const char *text = "hello + world";
```

当参数本身是宏并且希望先展开再字符串化时，需要两层宏：

```c
#define STRINGIFY_DIRECT(value) #value
#define STRINGIFY(value) STRINGIFY_DIRECT(value)
#define VERSION 17

STRINGIFY_DIRECT(VERSION) /* "VERSION" */
STRINGIFY(VERSION)        /* "17" */
```

参数直接参与 `#` 时不会先做普通宏展开；外层 `STRINGIFY` 提供了额外的一轮展开机会。

## token 拼接 `##`

`##` 把左右两侧 token 拼成一个新的预处理 token：

```c
#define DECLARE_COUNTER(name) int counter_##name = 0

DECLARE_COUNTER(requests);
```

展开为：

```c
int counter_requests = 0;
```

若参与拼接的参数也需要先展开，同样使用两层辅助宏：

```c
#define CONCAT_DIRECT(left, right) left##right
#define CONCAT(left, right) CONCAT_DIRECT(left, right)
```

拼接结果必须能形成合法 token。`##` 适合生成规则化标识符，但过度使用会让搜索、调试和 IDE 分析更困难。

## 宏展开顺序

理解展开时可以使用下面的简化规则：

1. 识别宏调用并收集参数 token。
2. 普通参数通常先展开其中的宏。
3. 把展开后的参数代入替换列表。
4. 直接参与 `#` 或 `##` 的参数不会按普通方式预展开。
5. 对替换结果继续重新扫描，展开其中新的宏调用。
6. 当前正在展开的同一个宏会受到抑制，避免立即无限递归。

例如：

```c
#define VALUE 8
#define DOUBLE(value) ((value) + (value))

DOUBLE(VALUE)
```

最终得到：

```c
((8) + (8))
```

不要依赖互相递归宏构造循环；预处理器的抑制规则会让结果难以直觉预测。

## 条件编译和头文件保护

```c
#ifndef TASK_H
#define TASK_H

/* 公共声明 */

#endif
```

平台分支应检测操作系统能力，而不是仅检测 CPU：

```c
#if defined(_WIN32)
    /* Windows */
#elif defined(__APPLE__)
    /* macOS */
#elif defined(__linux__)
    /* Linux */
#else
#error "unsupported platform"
#endif
```

条件编译适合隔离小范围平台差异。大量业务逻辑散布 `#ifdef` 会形成难以测试的多个隐形程序，通常应封装成统一接口和平台实现文件。

### `#if` 表达式

`#if` 使用预处理整数常量表达式：

```c
#define FEATURE_LEVEL 2

#if FEATURE_LEVEL >= 2
/* 编译高级实现 */
#endif
```

可以使用 `defined(NAME)` 检查宏。表达式中经过宏展开后仍然存在的普通标识符会按 `0` 处理：

```c
#if UNKNOWN_FEATURE
/* UNKNOWN_FEATURE 未定义时，这个分支不会选中。 */
#endif
```

虽然合法，显式使用 `defined(UNKNOWN_FEATURE)` 通常更能表达意图，也能减少拼写错误被静默当成 `0` 的风险。

命令行可以在不修改源码的情况下定义宏：

```bash
clang -std=c17 -DDEBUG -DFEATURE_LEVEL=2 source.c -o program
```

`-DNAME` 通常等价于把 `NAME` 定义为 `1`；也可以用 `-UNAME` 取消命令行或环境中已有的定义。

## 标准预定义宏

实现会预先定义一些标准宏：

| 宏 | 含义 |
| --- | --- |
| `__FILE__` | 当前逻辑源文件名字符串 |
| `__LINE__` | 当前逻辑行号整数 |
| `__DATE__` | 翻译日期字符串 |
| `__TIME__` | 翻译时间字符串 |
| `__STDC__` | 实现声明符合 ISO C 时定义为 `1` |
| `__STDC_VERSION__` | 所采用 C 标准版本，例如 C17 通常为 `201710L` |
| `__STDC_HOSTED__` | hosted 实现为 `1`，freestanding 实现为 `0` |

```c
printf("compiled from %s:%d, C version=%ld\n",
       __FILE__, __LINE__, (long)__STDC_VERSION__);
```

`__DATE__` 和 `__TIME__` 会让相同源码在不同时间产生不同内容，不利于可重复构建，除非确实需要，否则不要把它们写入产物。

查看编译器当前预定义的全部宏：

```bash
clang -std=c17 -dM -E -x c /dev/null
```

以下划线加大写字母开头或包含双下划线的名称通常保留给实现。用户代码不要自行定义类似 `__MY_MACRO` 的名称。

## `#line`

`#line` 改变后续逻辑位置：

```c
#line 200 "generated_config.c"
printf("%s:%d\n", __FILE__, __LINE__);
```

下一行会使用指定文件名和接近 200 的逻辑行号。它主要用于代码生成器，让编译诊断指回模板或原始输入。普通手写代码很少需要它，滥用会让源码位置和诊断位置不一致。

## `#pragma` 与 `_Pragma`

`#pragma` 向编译器传递实现定义指令。未知 pragma 通常被忽略或产生警告，具体行为应查工具链文档：

```c
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wunused-parameter"
/* 受控范围内的代码 */
#pragma clang diagnostic pop
```

上例是 Clang 专用，不是可移植 C17 功能。警告抑制应限制在无法修改的外部代码边界，不能替代修复自身代码。

`_Pragma` 是 C99 起提供的一元运算符形式，参数是字符串字面量，并且可以出现在宏展开中：

```c
#define DO_PRAGMA(content) _Pragma(#content)
#define CLANG_DIAGNOSTIC_PUSH DO_PRAGMA(clang diagnostic push)
```

普通 `#pragma` 不能由宏直接生成，`_Pragma` 正是为这个场景提供的标准机制，但其中的具体 pragma 内容仍然依赖编译器。

## X-Macro 模式

X-Macro 用一份列表生成多个相互对应的结构：

```c
#define COLOR_LIST \
    X(RED)          \
    X(GREEN)        \
    X(BLUE)

typedef enum {
#define X(name) COLOR_##name,
    COLOR_LIST
#undef X
    COLOR_COUNT
} Color;

static const char *const color_names[COLOR_COUNT] = {
#define X(name) [COLOR_##name] = #name,
    COLOR_LIST
#undef X
};
```

它能减少枚举和字符串映射不同步，但也增加预处理阅读成本，适合确实存在多个生成视图的稳定列表。

## 位运算符

C17 没有标准二进制整数字面量，因此使用十六进制展示位模式：

```c
unsigned a = 0xCu; /* 1100 */
unsigned b = 0xAu; /* 1010 */

unsigned both = a & b;       /* 1000 */
unsigned either = a | b;     /* 1110 */
unsigned different = a ^ b;  /* 0110 */
unsigned shifted = a << 2;   /* 110000 */
```

位操作通常优先使用无符号类型。有符号负数右移结果依赖实现；左移负数或移出不可表示结果可能产生未定义行为。移位数量必须小于类型的位宽。

## 位掩码与标志位

```c
#define FLAG_READ  (1u << 0)
#define FLAG_WRITE (1u << 1)
#define FLAG_EXEC  (1u << 2)

unsigned permissions = 0;
permissions |= FLAG_READ;                 /* 设置 */
permissions &= ~FLAG_EXEC;                /* 清除 */
permissions ^= FLAG_WRITE;                /* 翻转 */
bool can_read = (permissions & FLAG_READ) != 0; /* 检测 */
```

如果标志位可能超过 `unsigned` 位宽，应改用明确宽度类型和对应常量，例如 `UINT64_C(1) << bit`，并先验证 `bit < 64`。

## 位域的边界

```c
struct Flags {
    unsigned ready : 1;
    unsigned mode : 3;
};
```

位域的分配顺序、跨存储单元方式、对齐和结构体总大小依赖实现。它适合当前编译器和 ABI 内部的紧凑状态，不适合直接映射网络协议、磁盘格式或跨编译器公共 ABI。

## 实用位技巧及前置条件

判断 2 的幂：

```c
static bool is_power_of_two(size_t value) {
    return value != 0 && (value & (value - 1)) == 0;
}
```

向上对齐时，不仅要求 `alignment` 为 2 的幂，还要检查加法溢出：

```c
static bool align_up(size_t value, size_t alignment, size_t *result) {
    if (result == NULL || !is_power_of_two(alignment)) {
        return false;
    }
    size_t mask = alignment - 1;
    if (value > SIZE_MAX - mask) {
        return false;
    }
    *result = (value + mask) & ~mask;
    return true;
}
```

交换整数应使用临时变量：

```c
static void swap_int(int *left, int *right) {
    int temporary = *left;
    *left = *right;
    *right = temporary;
}
```

XOR swap 难读且在两个指针指向同一对象时会把值清零，优化器也能很好地处理普通交换写法。

## 常见错误

- 宏参数没有括号
- 把带副作用的表达式传给会重复求值的宏
- 误以为 `#include` 会自动链接对应实现
- 混淆字符串化、token 拼接和普通参数展开时机
- 拼错 `#if` 中的宏名后被静默当作 `0`
- 自定义实现保留形式的宏名
- 用编译器专用 pragma 隐藏本应修复的警告
- 在 C17 中使用 C23 或 GNU 扩展却不说明
- 对有符号负数做位移并假定跨平台结果一致
- 移位数量达到或超过类型位宽
- 把位域布局当作协议格式
- 对齐计算没有检查溢出

## 检查点

1. `MAX(i++, j++)` 为什么不能按普通函数调用理解？
2. 为什么 C17 示例不能使用 `0b1010`？
3. 为什么位域不能直接替代网络协议编码？
4. `STRINGIFY_DIRECT(VERSION)` 和 `STRINGIFY(VERSION)` 为什么不同？
5. `#include "module.h"` 为什么不会自动编译或链接 `module.c`？

## 动手练习

1. 运行 `clang -E`，找到 `MAX` 或标志宏展开后的表达式。
2. 使用 `clang -dM -E -x c /dev/null`，找出当前编译器的 C 版本和平台宏。
3. 分别用 `-DDEBUG` 和不带该参数编译示例，对比预处理输出和运行输出。
4. 编写字符串化和 token 拼接宏，先预测一层与两层辅助宏的展开结果。
5. 完成 `exercises/08_bitflags.c`，验证设置、清除、翻转和组合检测。
6. 给 `align_up` 编写零对齐、非 2 的幂、普通值和溢出输入测试。
7. 比较宏版 `MAX` 与 `static inline` 版本面对副作用参数时的行为。
