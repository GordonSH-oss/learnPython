# 05 Cython 与生产化

## 学习目标

使用 Cython 渐进类型化热点，理解生成和构建过程，并识别原生扩展从示例走向发布需要解决的问题。

## Cython 的位置

Cython 把 `.pyx` 转换成 C，再调用 C 编译器生成 Python 扩展：

```text
cython_example.pyx
       |
       | Cython
       v
cython_example.c
       |
       | Clang + Python headers
       v
cython_example.cpython-...so
```

它减少了手写参数解析和引用计数的代码，但最终仍是原生扩展，仍然面临整数范围、内存安全、GIL、平台构建和 ABI 兼容问题。

## 构建示例

Cython 不是标准库。使用隔离环境安装：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools cython
make cython
PYTHONPATH=build python -c 'import cython_example; print(cython_example.primes(30))'
```

预期输出：

```text
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

## 类型化真正改变了什么

`cython_example.pyx` 中：

```cython
cdef int candidate, multiple
```

这些循环变量使用 C `int`，循环控制和乘法可以生成 C 操作。但 `bytearray` 和结果 `list` 仍是 Python 对象，访问和 `append` 仍会经过 Python/C API。Cython 不是给函数参数加一个类型就自动消除全部 Python 开销。

示例用：

```cython
if candidate <= limit // candidate:
```

避免直接计算 `candidate * candidate` 作为循环条件时发生 C 整数溢出。输入 `limit < 2` 会提前返回，避免访问不存在的 `sieve[1]`。

## 编译器指令与安全

文件关闭了边界检查和负下标回绕：

```text
boundscheck=False, wraparound=False
```

这能减少热循环检查，但错误索引可能越界访问。只有在测试能够证明边界正确时才关闭。开发初期保留检查，性能分析确认它是热点后再调整。

使用 annotation 报告可以识别仍在调用 Python API 的代码：

```bash
python -m cython -a cython_example.pyx
open cython_example.html
```

黄色越深通常表示与 Python 交互越多。不要追求所有代码变白；只优化测得的热点。

## GIL

Cython 的 `nogil` 代码块不能任意操作 Python 对象：

```cython
with nogil:
    # 只能执行不依赖 Python 对象和 Python/C API 的 C 操作
```

释放 GIL 的作用是允许其他 Python 线程运行，不是让当前代码自动使用多个核心。要并行执行仍需线程划分、无数据竞争的工作区和合适的任务粒度。

## 从本地构建到发布

`make extension` 适合学习和本机实验。真实包应使用 `pyproject.toml` 描述构建系统，并在隔离环境生成 wheel。发布时需要考虑：

- 支持哪些 Python 版本和 CPython ABI。
- macOS wheel 包含 `arm64`、`x86_64` 还是 universal2。
- Linux wheel 的 manylinux/musllinux 兼容目标。
- Windows 编译器和导出符号。
- 第三方动态库如何打包和定位。
- debug、sanitizer 和优化构建如何区分。
- 原生崩溃怎样收集符号和复现。

使用 Python Limited API/Stable ABI 可以减少按 Python 小版本重建的需求，但它只覆盖 API 子集，并不自动解决其他平台兼容问题。

## 生产接口检查表

- 公共函数有明确输入类型、范围、错误和所有权契约。
- C 端从不信任来自 Python 的长度、索引或指针。
- 所有新引用、缓冲区和系统资源在失败路径也会释放。
- 释放 GIL 的代码不调用 Python/C API，并保护共享 C 状态。
- 测试包含空输入、极值、错误类型、嵌入 `NUL` 和分配失败策略。
- 基准包含边界转换和真实调用粒度。
- CI 在所有目标 Python/平台组合构建并导入 wheel。
- 保留纯 Python 回退方案，或明确不支持的平台。

## 动手练习

1. 为 `primes` 写一个纯 Python 参考实现，比较 `0`、`1`、`2`、`100` 的结果。
2. 生成 annotation HTML，标出仍然操作 Python `list` 的行。
3. 将筛数组改成 C 分配的缓冲区，设计好分配失败和释放路径后再实现。
4. 为本目录设计一个 `pyproject.toml`，但在添加发布配置前先决定目标 Python 版本和 wheel 平台矩阵。
