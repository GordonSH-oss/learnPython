# 03 编写 Python/C API 扩展

## 学习目标

理解 Python 原生模块的初始化、参数转换、异常协议、对象返回和 GIL，并能沿调用路径阅读 `mymath_module.c`。

## 构建并导入

```bash
make extension
PYTHONPATH=build python3 c_extension_demo.py
```

构建结果类似：

```text
build/mymath.cpython-314-darwin.so
```

文件名包含解释器版本和平台标记。它不是普通 C 动态库接口，而是由 Python 导入系统加载、并导出约定初始化函数的扩展模块。

在 macOS 上，Makefile 使用 `-bundle -undefined dynamic_lookup`。扩展中的 `Py*` 符号由加载它的 Python 进程在导入时解析，而不是在构建时单独链接一个 Python 动态库。Linux 则使用 `-shared -fPIC`。

## 从 `import` 到 C 函数

```text
import mymath
   |
   | 动态加载扩展文件
   v
PyInit_mymath()
   |
   | PyModule_Create(&mymath_module)
   v
模块对象，方法表中注册 sum_squares 和 count_byte
```

初始化符号必须是 `PyInit_<模块名>`。模块定义保存名称、文档、状态大小和方法表。方法表把 Python 可见名称映射到 C 函数、调用约定和文档。

## 参数转换与异常协议

`sum_squares` 使用 `METH_O`，所以 C 函数直接收到一个 Python 参数对象：

```c
long long limit = PyLong_AsLongLong(argument);
if (limit == -1 && PyErr_Occurred()) {
    return NULL;
}
```

`-1` 也可能是合法转换结果，因此必须同时检查 `PyErr_Occurred()`。Python/C API 的常见失败协议是：

```text
成功：返回非 NULL 的 PyObject *，没有待处理异常
失败：设置 Python 异常，返回 NULL
```

只返回 `NULL` 却不设置异常，会触发 `SystemError`；设置异常后又返回普通对象也会破坏调用协议。

业务校验使用对应异常类型：

```c
PyErr_SetString(PyExc_ValueError, "limit must be non-negative");
return NULL;
```

类型无法转换由 `PyLong_AsLongLong` 设置 `TypeError`，数值范围失败使用 `OverflowError`。

## 返回 Python 对象

C 的 `int64_t` 不能直接返回给 Python。扩展创建一个新的 Python 整数对象：

```c
return PyLong_FromLongLong(total);
```

大多数返回对象的构造函数返回“新引用”。把它交给调用者后，调用者拥有该引用。本例没有临时 Python 对象，所以引用管理简单；更复杂函数应为每个新引用设计成功和失败清理路径。

基本规则：

- 新引用：当前代码拥有，转交或用 `Py_DECREF` 释放。
- 借用引用：当前代码不拥有，若要长期保存应先 `Py_INCREF`。
- `Py_XDECREF` 允许参数为 `NULL`，`Py_DECREF` 不允许。

## GIL 与纯 C 热点

`sum_squares` 的循环只访问局部 C 整数，不调用 Python/C API，因此可以暂时释放 GIL：

```c
Py_BEGIN_ALLOW_THREADS
/* 不调用 Python/C API 的长计算 */
Py_END_ALLOW_THREADS
```

释放后，其他 Python 线程可以运行。但这不会让单次循环自动并行，也不能在释放期间操作 Python 对象或设置 Python 异常。因此代码先记录 `overflowed`，重新获得 GIL 后再调用 `PyErr_SetString`。

短计算不应盲目释放 GIL，释放和重新获取本身有成本。共享的 C 数据还需要自己的同步策略。

## Buffer 和字节数据

`count_byte` 使用 `PyArg_ParseTuple(args, "y#y#", ...)` 获取只读字节缓冲区及长度。`PY_SSIZE_T_CLEAN` 必须在 `Python.h` 前定义，确保 `#` 格式使用 `Py_ssize_t` 长度。

解析成功后，输入 Python 对象在函数调用期间保持存活，因此指针在返回前有效。函数不能把该指针保存到全局并在以后使用。

## 崩溃影响

扩展与解释器运行在同一进程。越界访问、错误引用计数或空指针解引用会使整个 Python 进程崩溃，而不是产生普通 Python 异常。调试时先构建带符号版本，并使用：

```bash
lldb -- python3 -c 'import sys; sys.path.insert(0, "build"); import mymath; print(mymath.sum_squares(10))'
```

## 动手练习

1. 增加 `triangular_number(n)`，对类型、负数和 `int64_t` 溢出分别测试。
2. 故意让参数错误分支返回 `Py_None` 而保留异常，运行测试观察协议错误，然后恢复。
3. 阅读 `PyLong_FromLongLong` 和 `PyArg_ParseTuple` 的官方文档，分别标记返回引用所有权和每个格式字符的目标 C 类型。
