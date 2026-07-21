# 04 函数与作用域

## 学习目标

完成本章后，你应该能够：

- 用函数契约描述输入、输出、失败和副作用
- 区分函数声明、定义和调用
- 解释 C 的按值传递以及输出参数的用途
- 区分作用域、链接和存储期
- 判断递归是否具有正确的基本情况和进展条件

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

## C 始终按值传递

函数接收实参值的副本：

```c
static void set_to_zero(int value) {
    value = 0;
}
```

它不会修改调用者的整数。传入指针时，复制的是地址值；函数可以通过这个地址修改调用者对象：

```c
static void set_to_zero(int *value) {
    if (value != NULL) {
        *value = 0;
    }
}
```

这仍然是按值传递，不是“按引用传递”。第 06 章会深入解释指针有效性和生命周期。

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

全局可变状态会让函数依赖隐藏上下文，应尽量减少并通过清晰接口管理。

## 递归

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

这个函数仍存在整数溢出边界。正确终止不代表结果对任意输入都有效。递归还会消耗调用栈，简单线性遍历通常用循环更直接。

## 常见错误

- 调用前没有可见声明
- 声明与定义的参数类型不一致
- 忽略空输入和失败表达
- 返回局部变量地址
- 误以为修改普通参数会修改调用者
- 递归没有基本情况，或参数没有接近基本情况
- 用全局变量隐藏本应显式传递的依赖

## 检查点

1. 为什么数组参数还需要单独传入长度？
2. 指针参数为什么仍然属于按值传递？
3. `static` 局部变量的作用域和存储期分别是什么？

## 动手练习

1. 为整数数组实现 `min`、`max` 和 `mean`。空数组通过返回 `false` 表达失败。
2. 给函数补充契约注释，明确空指针、长度和输出参数规则。
3. 分别用递归和循环计算整数和，测试 `0`、`1` 和较大输入，并解释溢出边界。
