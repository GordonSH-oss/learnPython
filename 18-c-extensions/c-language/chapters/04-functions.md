# 04 函数与作用域

## 学习目标

完成本章后，你应该能够：

- 用函数契约描述输入、输出、失败和副作用
- 区分函数声明、定义和调用
- 解释 C 的按值传递以及输出参数的用途
- 区分作用域、链接和存储期
- 判断递归是否具有正确的基本情况和进展条件
- 使用 `stdarg.h` 编写可变参数函数，理解类型安全问题
- 声明和使用函数指针，用 `typedef` 提高可读性
- 理解 `inline` 和 `_Noreturn` 的语义
- 描述函数调用时栈帧的结构和生命周期

函数指针的高级应用（回调、虚表模式）将在第 11 章展开，内存布局的完整模型见第 14 章。

## 先运行示例

```bash
make build/examples/04_functions
./build/examples/04_functions
```

## 声明、定义与调用

```c
#include <stddef.h>

double average(const int values[], size_t length);
```

这是函数声明，也称为原型。它让编译器知道名称、参数和返回类型。函数定义提供函数体：

```c
double average(const int values[], size_t length) {
    long sum = 0;
    for (size_t i = 0; i < length; ++i) {
        sum += values[i];
    }
    return (double)sum / (double)length;
}
```

声明通常放在头文件，定义通常放在 `.c` 文件。声明与定义不一致可能在编译或链接阶段暴露，也可能形成更隐蔽的接口错误。

调用函数时，编译器会按照原型检查实参的数量和类型：

```c
int data[] = {10, 20, 30};
double avg = average(data, 3);  // 编译器按原型检查参数
```

如果调用点没有可见的原型，C89 会隐式假设返回 `int`（隐式声明），这在 C99 之后已被废除。始终在调用前提供原型。

## 函数契约

一个可用的接口应说明：

- 输入允许哪些值，例如指针能否为 `NULL`
- 数组长度和缓冲区容量由谁提供
- 成功时返回什么
- 失败如何表达
- 函数是否修改输入或外部状态
- 返回资源由谁释放

上面的 `average` 对空数组没有有效结果。可以改为状态返回值加输出参数：

```c
#include <stdbool.h>
#include <stddef.h>

bool average(const int values[], size_t length, double *result) {
    if (values == NULL || result == NULL || length == 0) {
        return false;
    }

    long sum = 0;
    for (size_t i = 0; i < length; ++i) {
        sum += values[i];
    }
    *result = (double)sum / (double)length;
    return true;
}
```

这种模式在 CPython 内部大量使用。例如 `PyArg_ParseTuple` 返回成功/失败，通过输出参数传递解析结果。在设计 C 接口时，优先考虑"失败可表达"的契约形式。

## C 始终按值传递

函数接收实参值的副本：

```c
static void set_to_zero(int value) {
    value = 0;  // 只修改了副本
}
```

它不会修改调用者的整数。传入指针时，复制的是地址值；函数可以通过这个地址修改调用者对象：

```c
static void set_to_zero(int *value) {
    if (value != NULL) {
        *value = 0;  // 通过地址修改调用者的对象
    }
}
```

这仍然是按值传递，不是"按引用传递"。如果你想修改调用者的指针本身（比如让它指向新分配的内存），就需要传二级指针 `int **`。第 06 章会深入解释指针有效性和生命周期。

与 Python 对比：Python 对象是引用语义，函数内对可变对象的修改对调用者可见。C 中没有"引用"——一切都是值的复制，要修改调用者数据就必须显式传地址。

## 作用域、链接与存储期

这三个概念回答不同问题：

| 概念 | 问题 |
| --- | --- |
| 作用域 | 名称在源代码的哪些位置可见？ |
| 链接 | 不同声明是否表示同一个跨翻译单元实体？ |
| 存储期 | 对象在运行期间何时存在？ |

- 块作用域名称只在对应花括号内可见。
- 文件作用域名称从声明处到文件末尾可见。
- 普通局部对象通常具有自动存储期。
- `static` 局部对象具有静态存储期，会在程序运行期间保留值。
- 文件作用域函数或对象使用 `static` 时具有内部链接，只对当前翻译单元可见。

```c
static int call_count = 0;  // 文件作用域，内部链接，静态存储期

void track_call(void) {
    static int local_count = 0;  // 块作用域，无链接，静态存储期
    call_count++;
    local_count++;
}
```

`call_count` 对本文件所有函数可见；`local_count` 只在 `track_call` 内可见，但两者的生命周期都持续到程序结束。

全局可变状态会让函数依赖隐藏上下文，应尽量减少并通过清晰接口管理。CPython 的全局解释器锁（GIL）相关的全局状态就是一个教训——后续版本正在努力去除全局状态以支持子解释器。

## 可变参数函数

C 允许函数接受不定数量的参数。`printf` 就是最典型的例子。标准头文件 `<stdarg.h>` 提供了访问可变参数的宏：

```c
#include <stdarg.h>
#include <stdio.h>

double sum_doubles(int count, ...) {
    va_list args;
    va_start(args, count);  // 从 count 之后开始读取

    double total = 0.0;
    for (int i = 0; i < count; i++) {
        total += va_arg(args, double);  // 按 double 类型取下一个参数
    }

    va_end(args);  // 清理
    return total;
}

// 调用
double result = sum_doubles(3, 1.0, 2.5, 3.7);  // result = 7.2
```

关键宏说明：

| 宏 | 作用 |
| --- | --- |
| `va_list` | 保存遍历状态的类型 |
| `va_start(ap, last_fixed)` | 初始化 `ap`，`last_fixed` 是最后一个固定参数 |
| `va_arg(ap, type)` | 取出下一个参数并按 `type` 解释 |
| `va_end(ap)` | 结束遍历，必须调用 |
| `va_copy(dest, src)` | 复制遍历状态（需要多次遍历时） |

### 类型安全问题

`va_arg` 完全依赖调用者传入的类型与 `type` 参数匹配。编译器无法验证——这是 C 可变参数的根本风险：

```c
// 危险：传入 int，但读取为 double
int x = 5;
total += va_arg(args, double);  // 未定义行为：按 8 字节读取 4 字节的 int
```

整数提升规则（默认参数提升）进一步复杂化了这个问题：
- `char` 和 `short` 会被提升为 `int`
- `float` 会被提升为 `double`

因此 `va_arg(args, char)` 是错误的，应使用 `va_arg(args, int)` 再强制转换。

格式字符串（如 `printf` 的 `"%d %s"`）是一种约定俗成的解决方案：调用者在格式字符串中声明每个参数的类型，函数据此解析。这正是为什么 `printf("%d", 3.14)` 是未定义行为——格式字符串说了 `int`，但传入了 `double`。

GCC 和 Clang 的 `__attribute__((format(printf, n, m)))` 可以让编译器帮你检查格式字符串与实参的一致性。

### 与 CPython 的关联

`Py_BuildValue` 和 `PyArg_ParseTuple` 都是可变参数函数，它们用格式字符串描述 Python 对象的类型：

```c
// 构建一个包含 int 和 str 的 Python 元组
PyObject *tuple = Py_BuildValue("(is)", 42, "hello");

// 解析传入的 Python 参数
int n;
const char *s;
if (!PyArg_ParseTuple(args, "is", &n, &s)) {
    return NULL;
}
```

格式字符串 `"is"` 意思是：第一个参数是 `int`，第二个是 `char *`（Python str）。理解可变参数的工作原理，能帮你正确使用这些 API 并读懂它们的错误信息。

## 函数指针基础

函数在编译后存在于代码段，有一个入口地址。函数指针就是保存这个地址的变量，可以用来间接调用函数——也就是把"行为"当作数据传递。

### 声明语法

```c
// 声明一个函数指针变量 compare
// 它指向的函数接收两个 int 参数，返回 bool
bool (*compare)(int, int);
```

小括号 `(*compare)` 不能省略。没有括号的话，`bool *compare(int, int)` 表示的是"返回 `bool *` 的函数"而非函数指针。

赋值和调用：

```c
#include <stdbool.h>
#include <stdio.h>

static bool ascending(int a, int b) { return a < b; }
static bool descending(int a, int b) { return a > b; }

int main(void) {
    bool (*cmp)(int, int) = ascending;
    printf("%d\n", cmp(3, 5));  // 输出 1（true）

    cmp = descending;
    printf("%d\n", cmp(3, 5));  // 输出 0（false）
    return 0;
}
```

### 用 typedef 提高可读性

函数指针声明很容易变得难以阅读。`typedef` 可以给类型起别名：

```c
typedef bool (*Comparator)(int, int);

// 现在可以像普通类型一样使用
void sort(int arr[], size_t len, Comparator cmp) {
    // 使用 cmp(a, b) 比较元素
}

sort(data, n, ascending);
sort(data, n, descending);
```

这就是把行为作为参数传递——类似 Python 中把函数对象传给 `sorted(key=func)`。

### 为什么这对 CPython 重要

CPython 的类型系统大量使用函数指针。`PyTypeObject` 结构体里的 `tp_init`、`tp_new`、`tp_dealloc` 等成员都是函数指针——它们定义了自定义类型的行为。第 11 章将展开这种模式。

## inline 函数

`inline` 关键字建议编译器将函数体内联展开到调用点，避免函数调用的开销：

```c
static inline int max(int a, int b) {
    return a > b ? a : b;
}
```

关键点：

1. `inline` 只是建议，编译器可以忽略。现代编译器（GCC、Clang）在 `-O2` 及以上优化级别会自行决定是否内联，不需要 `inline` 提示。
2. `static inline` 是最常见的用法——定义放在头文件中，每个包含该头文件的翻译单元得到自己的副本，不会产生链接冲突。
3. 不带 `static` 的 `inline` 有复杂的链接语义：你需要在恰好一个翻译单元中提供外部定义。初学阶段优先使用 `static inline`。

什么时候适合用：
- 函数体很短（几行）
- 被频繁调用（比如在循环内部）
- 不需要取函数地址

CPython 源码中 `static inline` 大量出现在对象操作的宏/函数里，例如引用计数的 `Py_INCREF`（在新版本中从宏改为了 `static inline` 函数）。

## _Noreturn 与 noreturn

有些函数永远不会返回——它们终止程序或无限循环：

```c
#include <stdlib.h>
#include <stdnoreturn.h>  // C11

noreturn void fatal_error(const char *msg) {
    fprintf(stderr, "FATAL: %s\n", msg);
    abort();
}
```

`noreturn`（C11 的 `<stdnoreturn.h>` 宏，或 `_Noreturn` 关键字）告诉编译器和静态分析工具：这个函数不会返回到调用者。好处是：

- 编译器可以省略返回后的不可达代码警告
- 静态分析器知道调用此函数后的代码不会执行
- 帮助编译器优化控制流

```c
int process(int *data) {
    if (data == NULL) {
        fatal_error("data is NULL");
        // 编译器知道这里不可达，不会警告缺少 return
    }
    return *data + 1;
}
```

C23 引入了 `[[noreturn]]` 属性语法，与 C++ 对齐。在 C11 代码中使用 `_Noreturn` 或 `noreturn` 宏即可。

## 栈帧概念

每次函数调用，运行时都会在调用栈上压入一个栈帧（stack frame）。栈帧包含：

```text
┌─────────────────────────────┐ 高地址
│ 调用者的栈帧                  │
├─────────────────────────────┤
│ 返回地址                      │  ← 调用结束后跳回哪里
│ 保存的寄存器                  │  ← 调用者需要保护的寄存器
│ 局部变量                      │  ← 当前函数的自动变量
│ 参数准备区                    │  ← 传递给下层函数的参数
├─────────────────────────────┤
│ 被调用函数的栈帧              │
└─────────────────────────────┘ 低地址（栈向低地址增长）
```

理解栈帧有助于解释这些现象：

1. **局部变量的生命周期**：函数返回时栈帧弹出，局部变量不再有效——这就是为什么"返回局部变量地址"是经典错误。
2. **递归消耗栈空间**：每次递归调用都压入新栈帧。栈空间有限（通常 1-8 MB），深度递归会栈溢出。
3. **参数传递成本**：传入大型结构体时会复制整个对象到栈帧中。传指针只复制 8 字节（64 位系统）。
4. **调试器的回溯**：`gdb` 的 `bt`（backtrace）命令就是遍历栈帧链表，显示每层函数调用。

```c
void c(void) { /* 断点在此：栈上有 main → a → b → c 四个帧 */ }
void b(void) { c(); }
void a(void) { b(); }
int main(void) { a(); return 0; }
```

第 14 章将展示完整的进程内存布局：代码段、数据段、堆、栈的位置关系。

## 递归与尾调用

递归函数必须同时具有：

1. 基本情况：停止继续调用。
2. 进展条件：每次调用都更接近基本情况。

```c
static unsigned long factorial(unsigned n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}
```

这个函数仍存在整数溢出边界。正确终止不代表结果对任意输入都有效。

### 尾调用与栈溢出

尾调用是指函数的最后一个操作是调用另一个函数（或自身），且无需对返回值做任何处理：

```c
// 这不是尾调用——还需要乘以 n
return n * factorial(n - 1);

// 这是尾调用形式（累加器模式）
static unsigned long factorial_tail(unsigned n, unsigned long acc) {
    if (n <= 1) return acc;
    return factorial_tail(n - 1, n * acc);  // 尾调用
}
```

某些语言（Scheme）保证尾调用优化（TCO）：编译器复用当前栈帧而不是压入新帧。但 C 标准不保证 TCO。实践中：

- GCC/Clang 在 `-O2` 及以上可能会优化尾递归
- 但不能依赖它——必须考虑栈深度极限
- 默认栈大小通常为 1-8 MB，每个栈帧几十到几百字节
- `factorial(100000)` 这种深度递归在没有 TCO 时必然栈溢出

经验法则：如果递归深度与输入大小线性相关，且输入可能很大，改用循环。递归适合树形结构等天然递归深度有限的场景。
