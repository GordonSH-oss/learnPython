# 10 多文件项目与构建

## 学习目标

理解头文件、源文件、翻译单元、链接和 Makefile 的增量构建。

本章示例包含：

```text
examples/calculator.h    公共声明
examples/calculator.c    函数定义
examples/10_multi_file.c 使用接口的程序入口
```

头文件使用 include guard 防止重复包含：

```c
#ifndef CALCULATOR_H
#define CALCULATOR_H
double calculator_add(double left, double right);
#endif
```

头文件放调用者必须知道的契约，不放普通函数定义和私有实现。源文件可用 `static` 限制辅助函数只在当前翻译单元可见。

## 编译和链接

```bash
clang -c examples/calculator.c -o build/calculator.o
clang -c examples/10_multi_file.c -o build/main.o
clang build/main.o build/calculator.o -o build/calculator_demo
```

声明不一致通常产生编译警告或错误；只有声明却没有定义通常产生链接错误。

## Makefile 心智模型

规则描述目标、依赖和生成命令。依赖没变化时，`make` 不必重新生成目标。命令行必须以 Tab 开头。

## 动手练习

给 calculator 模块增加乘法和安全除法。除数为零时不要返回一个看似正常的数字，应返回状态并通过输出参数给出结果。
