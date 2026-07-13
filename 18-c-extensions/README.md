# C 语言强化 Python 与 CPython 源码阅读

本模块涵盖两个主题：

1. **系统学习 C 语言** — 从编译、语法和指针到内存管理与工程实践
2. **用 C 强化 Python** — 通过 ctypes、C 扩展模块和 Cython 提升性能
3. **阅读 CPython 源码** — 理解 Python 解释器内部机制

如果还不熟悉 C，请先完成 [`c-language/README.md`](c-language/README.md) 中的 12 章教程和配套练习。

## 为什么需要 C？

Python 是解释型语言，循环和数值计算比 C 慢 10-100 倍。关键热点用 C 实现可以：
- 将计算密集型代码提速 10-100x
- 复用已有的 C/C++ 库（OpenSSL、SQLite、zlib）
- 理解 Python 底层实现（CPython 本身就是 C 写的）

## 文件列表

### C 语言基础

| 路径 | 说明 |
|------|------|
| `c-language/README.md` | 完整学习路线、环境准备和命令索引 |
| `c-language/chapters/` | 12 章系统教程 |
| `c-language/examples/` | 可编译运行的章节示例 |
| `c-language/exercises/` | 7 个递进练习 |
| `c-language/solutions/` | 练习参考答案 |

### 用 C 强化 Python

| 文件 | 说明 |
|------|------|
| `arithmetic.c` | 供 ctypes 调用的共享库源码 |
| `ctypes_demo.py` | ctypes 加载 C 库并调用函数 |
| `mymath_module.c` | Python C 扩展模块（使用 Python/C API）|
| `setup_mymath.py` | 编译 C 扩展的 setup.py |
| `c_extension_demo.py` | 演示 C 扩展模块的使用和性能对比 |
| `cython_example.pyx` | Cython 示例：类型声明加速循环 |
| `setup_cython.py` | 编译 Cython 的 setup.py |

### 阅读 CPython 源码

| 文件 | 说明 |
|------|------|
| `CPYTHON_SOURCE_GUIDE.md` | CPython 源码阅读指南 |
| `object_model.c` | 注释版：PyObject 结构和引用计数 |
| `list_internals.c` | 注释版：list 的内存布局和 append 实现 |

## 学习路径

```
0. C 语言教程 → 1. ctypes → 2. C 扩展模块 → 3. Cython
                                                   ↓
                                       4. CPython 源码阅读
```

## 前置知识

- C 语言基础（指针、结构体、函数）
- Python 基础（模块、函数、类）
- 命令行编译（gcc/clang）
