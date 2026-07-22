# 12 多文件项目、测试与调试

## 学习目标

- 组织头文件、实现文件和构建目标
- 理解 ODR、inline 和模板定义位置
- 编写自动测试并使用 sanitizer
- 识别编译期、链接期和运行期错误

## 模块边界

普通非模板接口仍采用头文件声明、`.cpp` 定义：

```cpp
// include/task.hpp
#pragma once
class Task { /* public contract */ };
```

`#pragma once` 广泛支持但不是 ISO 标准；传统 include guard 最可移植。

头文件应自包含，直接 include 自己需要的声明。不要依赖调用者先 include 某个头。

## One Definition Rule

ODR 要求程序中的实体定义满足规则。常见违反方式：

- 在头文件定义非 inline 普通函数或全局变量
- 不同翻译单元看到不一致类定义
- 宏让同一 inline 函数产生不同实现

C++17 inline 变量可安全放头文件，但仍应控制全局状态。

## 模板和 inline

模板定义通常必须对实例化点可见，所以放头文件。类内定义的成员函数隐式 inline；inline 主要允许多翻译单元一致定义，不等于编译器一定内联机器码。

## 测试

本教程脚本运行所有示例和答案。实际项目可使用 Catch2、GoogleTest 或 doctest，但框架不能替代测试设计。

测试应覆盖：

- 正常值和边界
- 构造失败与异常
- 复制、移动和 moved-from 状态
- 资源释放和失败回滚
- 并发不变量

## 调试与 sanitizer

```bash
make sanitize
lldb build/examples/03_classes
```

ASan/UBSan 能发现许多内存和未定义行为；TSan 需要单独并发构建。标准库 debug mode 和迭代器检查取决于实现。

## 编译数据库

大型项目使用 CMake/Meson 等生成 `compile_commands.json`，供 clangd、clang-tidy 和静态分析使用。构建系统必须明确标准版本、警告、目标依赖和平台链接参数。

## 动手练习

1. 把一个示例拆成 `.hpp`、`.cpp`、`main.cpp`。
2. 故意在头文件定义普通函数并制造重复符号，再用 inline 修复。
3. 为异常路径和 move 操作增加自动测试。

