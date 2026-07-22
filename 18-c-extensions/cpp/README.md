# 现代 C++ 系统教程

这套教程面向已经完成 [`c-language`](../c-language/README.md) 的开发者。你已经理解 C 的类型、指针、结构体、动态内存、编译链接和系统 API；这里不从循环语法重新开始，而是系统学习现代 C++ 如何用类型、对象生命周期和标准库降低手工资源管理成本。

课程采用 C++20，使用 Clang 或 GCC。核心原则是：

- 优先值语义和 RAII，而不是裸 `new`/`delete`。
- 优先标准容器和算法，而不是手写动态数组和链表。
- 用类型表达所有权、可空性和不变量。
- 默认遵循 Rule of Zero，仅在管理底层资源时编写特殊成员函数。
- 先保证正确性和可测试性，再讨论模板技巧和性能。

## 前置知识

建议已经掌握 C 教程中的：

- 类型、数组、指针、结构体和函数指针
- 动态内存及所有权
- 多文件构建、静态库和共享库
- 调试器、sanitizer 和测试
- 线程、文件描述符与 POSIX 基础

## 学习路线

| 阶段 | 章节 | 核心问题 | 示例 |
| --- | --- | --- | --- |
| 迁移 | [01 从 C 到 C++](chapters/01-from-c-to-cpp.md) | C++ 编译、命名空间和标准库有什么不同？ | `01_hello.cpp` |
| 语言 | [02 类型、引用与 const](chapters/02-types-references-const.md) | 引用、`auto`、值类别如何改变接口设计？ | `02_types.cpp` |
| 对象 | [03 类与不变量](chapters/03-classes-and-invariants.md) | 如何让对象始终保持有效状态？ | `03_classes.cpp` |
| 资源 | [04 RAII](chapters/04-raii.md) | 如何让资源随对象生命周期自动释放？ | `04_raii.cpp` |
| 值语义 | [05 复制与移动](chapters/05-copy-and-move.md) | 复制、移动和 Rule of Zero/Five 是什么？ | `05_move.cpp` |
| 标准库 | [06 容器、字符串与迭代器](chapters/06-containers-and-iterators.md) | 如何选择 vector、map、string 和 view？ | `06_containers.cpp` |
| 算法 | [07 算法、lambda 与 ranges](chapters/07-algorithms-lambdas-ranges.md) | 如何把循环意图交给标准算法？ | `07_algorithms.cpp` |
| 所有权 | [08 智能指针](chapters/08-smart-pointers.md) | `unique_ptr`、`shared_ptr`、`weak_ptr` 分别表达什么？ | `08_smart_pointers.cpp` |
| 失败 | [09 异常与错误设计](chapters/09-errors-and-exceptions.md) | 何时抛异常，何时返回状态？ | `09_errors.cpp` |
| 泛型 | [10 模板与 concepts](chapters/10-templates-and-concepts.md) | 泛型代码如何保持可读和可诊断？ | `10_templates.cpp` |
| 多态 | [11 继承与运行时多态](chapters/11-polymorphism.md) | 何时使用虚函数，何时使用 variant？ | `11_polymorphism.cpp` |
| 工程 | [12 多文件项目、测试与调试](chapters/12-projects-testing-debugging.md) | 如何组织、测试和检查 C++ 工程？ | `12_project.cpp` |
| 并发 | [13 线程、锁与任务](chapters/13-concurrency.md) | C++ 标准并发工具怎样管理线程生命周期？ | `13_concurrency.cpp` |
| 系统 | [14 文件系统与 I/O](chapters/14-filesystem-and-io.md) | 如何用标准库安全处理路径和文件？ | `14_filesystem.cpp` |
| 边界 | [15 性能、ABI 与 C 互操作](chapters/15-performance-and-c-interop.md) | 如何保持 C ABI 边界并验证性能？ | `15_c_interop.cpp` |
| Python | [16 用 C++ 扩展 Python](chapters/16-python-bindings.md) | pybind11 与手写 C API 的边界是什么？ | 概念与可选实验 |

## 构建与验证

```bash
cd 18-c-extensions/cpp
make examples
make solutions
make test
make sanitize
```

单独编译：

```bash
clang++ -std=c++20 -Wall -Wextra -Wpedantic \
  examples/01_hello.cpp -o build/examples/01_hello
```

## C 与现代 C++ 的核心差异

| C 常见做法 | 现代 C++ 默认做法 |
| --- | --- |
| `malloc/free` | 容器、值对象、RAII；必要时智能指针 |
| 结构体加外部函数 | 类封装不变量和操作 |
| 裸数组加长度 | `std::array`、`std::vector`、`std::span` |
| `char *` 字符串 | `std::string`、`std::string_view` |
| 函数指针加 `void *` | lambda、模板、`std::function`（需要类型擦除时） |
| 错误码 | 根据边界选择异常、状态类型或 `std::error_code` |
| 手工 cleanup | 析构函数自动清理 |

不要把 C++ 写成“带类的 C”。如果代码中充满裸 `new`、手工 `delete`、C 风格强制转换和拥有资源的裸指针，通常还没有真正使用现代 C++ 的设计能力。

