# 07 使用 Cython 渐进加速

## 学习目标

使用 Cython 渐进类型化热点，理解生成代码、Python 对象交互、typed memoryview、GIL 和构建过程。

## Cython 的位置

Cython 把 `.pyx` 转换成 C，再调用编译器生成 Python 扩展：

```text
Python-like .pyx -> Cython -> generated C -> compiler -> extension module
```

它减少手写参数解析和引用计数，但最终仍是原生扩展，仍需处理范围、内存安全、GIL、平台构建和 ABI。

## 构建示例

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools cython
make cython
PYTHONPATH=build python -c 'import cython_example; print(cython_example.primes(30))'
```

## 类型化改变什么

```cython
cdef int candidate, multiple
```

这些局部变量使用 C `int`，循环控制和算术可以生成 C 操作。但 bytearray 和返回 list 仍是 Python 对象，读取、写入和 append 仍可能调用 Python/C API。

仅给函数参数添加类型不保证整个函数脱离 Python 对象操作。使用 annotation 报告检查生成代码：

```bash
python -m cython -a cython_example.pyx
```

黄色区域表示与 Python 运行时交互较多。目标是优化真实热点，不是让整张页面机械变白。

## C 整数范围

Python `int` 任意精度，`cdef int` 通常范围有限。输入进入类型化函数时需要定义超范围行为。

示例用：

```cython
if candidate <= limit // candidate:
```

避免直接用 `candidate * candidate <= limit` 作为条件时的 C 整数溢出。类型化后必须用 C 的范围规则重新审视原 Python 算法。

## 编译器指令

```text
boundscheck=False, wraparound=False
```

关闭检查能减少热循环分支，但错误索引可能变成原生越界访问。开发阶段先保留检查，使用测试和 annotation 确认热点后，再像配套示例一样用函数装饰器把关闭范围限制在已证明安全的函数或代码块。

不要全局关闭检查后假定 Python 异常仍会保护错误索引。

## Typed memoryview

Cython 可以用 typed memoryview 表达 buffer protocol：

```cython
def sum_values(double[::1] values):
    cdef Py_ssize_t index
    cdef double total = 0
    for index in range(values.shape[0]):
        total += values[index]
    return total
```

`[::1]` 要求最后一维连续。它比手写 `Py_buffer` 简洁，但仍要考虑 dtype、维度、只读、字节序和调用期间修改。

## GIL 与 `nogil`

```cython
with nogil:
    # 只能执行不依赖 Python 对象或 Python/C API 的操作
```

释放 GIL 不会自动多核并行。要使用线程，还需要独立工作区、同步和足够任务粒度。异常、内存分配和 Python 回调也会影响能否保持 nogil。

Cython 允许标注函数 `noexcept`、`nogil` 等契约，但错误的声明可能丢失异常或导致未定义行为，应检查生成代码和文档。

## 包装已有 C 库

可以在 `.pxd` 中声明 C 头文件接口：

```cython
cdef extern from "arithmetic.h":
    int sum_squares(int limit, long long *result)
```

真实声明必须与头文件完全一致，包括固定宽度类型、const、返回状态和调用约定。最好让构建系统直接包含真实头文件，不要维护含义不同的“近似签名”。

## 错误和清理

Cython 能生成引用计数代码，但不会替你定义 C 资源所有权。`malloc`、文件、第三方句柄和 nogil 区域仍需要明确清理。

可以使用 `try/finally` 管理 Python 可见资源，或在 C 层建立统一 cleanup 路径。查看生成的 C 有助于理解异常路径是否释放了资源。

## 常见错误

- 类型化后忽略 C 整数溢出
- 全局关闭边界检查却没有证明索引安全
- 仍在热循环中频繁操作 Python list/dict
- 把 typed memoryview 当作自动支持所有 dtype 和 layout
- `nogil` 中调用 Python API
- 只测试本机生成的扩展，不测试 wheel 安装产物

## 动手练习

1. 为 primes 写纯 Python 基线并测试 `0`、`1`、`2`、`100`。
2. 生成 annotation HTML，标记所有 Python 交互行。
3. 增加 typed-memoryview 求和，与第 04 章 C API buffer 比较。
4. 在局部函数关闭 boundscheck，而不是全文件关闭，比较生成代码。
5. 把 arithmetic.h 作为外部 C 库接入 Cython，保持错误码到 Python 异常的映射。
