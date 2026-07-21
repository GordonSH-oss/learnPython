# 02 使用 `ctypes` 调用 C ABI

## 学习目标

构建并加载动态库，准确映射 C 类型，传递输出参数和数组，并把 C 状态码转换成 Python 异常。

## C ABI 是边界契约

阅读 `arithmetic.h`。头文件定义了 Python 和动态库共同遵守的二进制接口：

```c
int sum_squares(int32_t limit, int64_t *result);
```

参数和结果使用固定宽度整数，减少平台差异。函数返回状态码，计算结果通过输出参数写回：

- `0`：成功，`*result` 已写入。
- `-1`：参数无效。
- `-2`：结果超出 `int64_t`。

动态库不直接创建 Python 异常，因此 Python 包装层负责把状态码翻译成 `ValueError` 或 `OverflowError`。

## 构建和加载

```bash
make ctypes
file build/libarithmetic.dylib
python3 ctypes_demo.py
```

macOS 使用 `.dylib`，Linux 使用 `.so`。`ctypes_demo.py` 根据系统选择名称，并从 `USING_C_BUILD` 或默认 `build/` 加载。

```python
library = ctypes.CDLL(path)
```

加载成功后，动态链接器把符号名称解析为库中的函数地址。找不到文件、架构不匹配或依赖库缺失都会在加载阶段失败。Apple Silicon 上可使用 `file` 检查库是否包含 `arm64`。

## 必须声明函数签名

```python
library.sum_squares.argtypes = [
    ctypes.c_int32,
    ctypes.POINTER(ctypes.c_int64),
]
library.sum_squares.restype = ctypes.c_int
```

`ctypes` 不会读取 C 头文件。`argtypes` 和 `restype` 是 Python 侧手工维护的 ABI 声明。省略或写错可能截断值、破坏调用约定，严重时会让 Python 进程崩溃。

即使签名正确，构造 `c_int32` 时也可能把超范围 Python 整数转换成低 32 位。示例包装层的 `_require_int32` 会在调用 C 前检查 Python 类型和范围，防止这种静默截断成为业务结果。

常用映射：

| C | `ctypes` |
| --- | --- |
| `int32_t` | `c_int32` |
| `int64_t` | `c_int64` |
| `size_t` | `c_size_t` |
| `double` | `c_double` |
| `const char *` | `c_char_p` 或字符指针 |
| `double *` | `POINTER(c_double)` |

不要假设 C 的 `long` 等于 Python 整数或固定为 64 位。按照头文件的真实类型映射。

## 输出参数的数据流

包装函数创建 C 值并传入地址：

```python
result = ctypes.c_int64()
status = LIB.sum_squares(limit, ctypes.byref(result))
```

```text
Python limit -> c_int32 值 -> C 函数
                               |
Python result <- c_int64 对象 <- 写入 int64_t *
```

`byref(result)` 创建轻量的指针参数。C 调用结束后读取 `result.value`。被指向对象必须在整个调用期间存活。

## 数组、复制和生命周期

`sum_doubles` 先把任意可迭代对象转换成 Python `list`，再复制到连续的 C 数组：

```python
data = [float(value) for value in values]
array_type = ctypes.c_double * len(data)
c_values = array_type(*data)
```

这很清晰，但产生两次容器构造。对于大数组，转换成本可能接近甚至超过 C 求和。生产接口应考虑接受 `array.array`、`memoryview` 或 NumPy 连续缓冲区，避免逐元素转换。

C 不应在调用结束后保存 `c_values` 的指针，除非接口另有所有权协议并让 Python 对象保持存活。否则 Python 回收数组后会留下悬空指针。

配套代码还提供 `sum_doubles_buffer(array('d', ...))`。它通过 `memoryview` 验证一维、C 连续、native `double` 格式，再用 `ctypes.from_buffer` 直接借用原数组。这个版本没有逐元素复制，但要求缓冲区可写，因为 `from_buffer` 需要从可写 exporter 建立视图。完整机制见第 04 章。

## 字节串为什么要显式长度

`count_byte` 接收 `(const char *data, size_t length, char needle)`，所以能处理嵌入 `\0`：

```python
count_byte(b"a\x00a", b"a")  # 2
```

如果 C 端使用 `strlen`，第一个 `\0` 会被当作结尾。二进制数据接口应传指针加长度，而不是假定它是 C 字符串。

## 失败边界

`ctypes` 无法保护 Python 免受错误 C 代码影响：

- 越界写可能损坏解释器内存。
- 保存短生命周期指针会造成释放后使用。
- 错误的 `argtypes` 可能破坏寄存器或栈参数。
- C 函数若未释放 GIL，Python 线程调用行为还取决于加载器和函数类型。

`ctypes.CDLL` 调用外部函数时通常会在调用期间释放 GIL；`ctypes.PyDLL` 则用于调用 Python C API，会保留 GIL并在返回后检查 Python 异常。释放 GIL 不会自动让底层 C 库线程安全。若两个 Python 线程同时调用同一 C 全局状态，库本身仍必须同步。

回调方向更危险：C 保存 Python 回调函数地址时，Python 回调对象必须保持强引用，调用线程和回调生命周期必须明确，且回调抛出的异常不能像普通 Python 调用一样自然穿过任意 C 栈帧。生产接口应优先采用同步、调用期间有效的回调，避免让 C 长期保存裸回调指针。

因此 C ABI 应尽量窄、使用明确长度和固定类型，并为每个失败返回写测试。

## 动手练习

1. 运行 `make test`，确认嵌入 `NUL`、负数和溢出测试通过。
2. 给 C 库增加 `int min_double(const double *, size_t, double *)`。空数组返回 `-1`，并在 Python 包装层转换为 `ValueError`。
3. 暂时删掉 `sum_squares.restype`，观察小输入是否仍看似正确。解释为什么“示例能运行”不能证明 ABI 声明正确，然后恢复代码。
4. 比较 `sum_doubles` 和 `sum_doubles_buffer`，画出两者创建的 Python list、C 数组和借用指针。
5. 查询 `ctypes.CDLL(..., use_errno=True)`，设计一个调用 POSIX API 后立即保存 `errno` 的包装器。
