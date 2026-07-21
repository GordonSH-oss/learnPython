# 04 Buffer protocol 与零拷贝数据边界

## 学习目标

完成本章后，你应该能够：

- 解释 Python buffer exporter、consumer 和 `Py_buffer` 的关系
- 判断一个对象是否满足元素格式、维度、连续性和可写性要求
- 使用 ctypes 或 Python/C API 借用连续数据而不逐元素复制
- 在所有退出路径正确释放 buffer view
- 识别“零拷贝”接口的生命周期、并发和字节序限制

## 为什么数据转换会吞掉加速收益

如果包装层先把 Python iterable 转成 list，再逐元素创建 C 数组，调用路径是：

```text
任意 iterable
   ↓ Python 迭代和 float 转换
Python list
   ↓ 逐元素复制
C double[]
   ↓
C 循环
```

对于只做一次求和的算法，准备数据可能比 C 循环更贵。更适合批量数值接口的数据对象通常已经保存连续机器值，例如：

- `array.array`
- `bytearray`
- `memoryview`
- NumPy ndarray
- `mmap`
- 其他实现 buffer protocol 的扩展类型

## exporter、consumer 和 view

buffer exporter 拥有底层内存，consumer 请求一个描述该内存的 view：

```text
array('d') / NumPy array / bytearray
          |
          | 导出
          v
      Py_buffer
      - buf: 数据地址
      - len: 总字节数
      - itemsize: 单元素字节数
      - format: 元素格式
      - ndim/shape/strides
      - readonly
```

consumer 借用内存，不自动获得所有权。view 有效期间 exporter 必须保持底层存储稳定；consumer 完成后必须释放 view。

## Python 侧先用 `memoryview` 检查

```python
from array import array

values = array("d", [1.0, 2.5, -0.5])
view = memoryview(values)

print(view.format)       # d
print(view.itemsize)     # 通常为 8
print(view.ndim)         # 1
print(view.c_contiguous) # True
print(view.readonly)     # False
```

格式 `d` 表示 native C double。协议、文件或网络数据常带有固定字节序，不能因为长度恰好是 8 的倍数就直接解释成当前机器的 native double。

## ctypes 借用缓冲区

`ctypes_demo.sum_doubles` 会复制 iterable；`sum_doubles_buffer` 使用：

```python
array_type = ctypes.c_double * length
pointer = array_type.from_buffer(view)
```

`from_buffer` 不复制数据，创建的 ctypes 对象引用 exporter。它要求缓冲区可写；只读 `bytes` 或只读 memoryview 应使用其他接口或显式复制。

调用期间要同时保持 `view` 和 ctypes 对象存活。不能只返回裸地址后让这些对象离开作用域。

## Python/C API 获取 view

```c
Py_buffer view;
if (PyObject_GetBuffer(argument, &view,
                       PyBUF_FORMAT | PyBUF_C_CONTIGUOUS) < 0) {
    return NULL;
}
```

请求 flags 表达 consumer 需要的能力。获取成功后，不论后续验证成功还是失败，都必须：

```c
PyBuffer_Release(&view);
```

典型清理结构：

```c
PyObject *result = NULL;

if (invalid_format) {
    PyErr_SetString(PyExc_TypeError, "expected native doubles");
    goto cleanup;
}

result = PyFloat_FromDouble(total);

cleanup:
PyBuffer_Release(&view);
return result;
```

## 必须验证哪些字段

本例要求一维、C 连续、native double：

```c
view.ndim == 1
view.itemsize == sizeof(double)
view.format != NULL && strcmp(view.format, "d") == 0
view.len % sizeof(double) == 0
```

真实接口还可能需要检查：

- `readonly`：算法是否会写入数据
- `shape`：每一维元素数量
- `strides`：相邻元素的字节步长
- alignment：地址是否满足目标 C 类型对齐
- endianness：格式是否为 native 或指定字节序
- total length：乘法和索引是否可能溢出

不要只强制转换 `view.buf` 后假定所有对象都是连续 `double[]`。

## 连续与 strided 数据

二维数组切片可能不是连续内存：

```text
原数组:  [a b c d e f]
切片:     a   c   e       stride = 2 * itemsize
```

可以选择：

1. 只接受 C-contiguous 输入，接口简单且热循环紧凑。
2. 接受 strides，在 C 循环中按步长访问。
3. 包装层创建连续副本。

三种方案没有绝对优劣。应把是否复制写进接口契约并纳入 benchmark。

## 生命周期和并发

持有 `Py_buffer` 通常能阻止 exporter 调整底层内存大小，但不一定阻止另一个线程修改元素。若释放 GIL 后读取可写缓冲区，其他线程同时写入可能形成 C 数据竞争或不一致快照。

本教程的 `sum_doubles_buffer` 保持 GIL，以便先建立清楚的安全基线。若要释放 GIL，应额外满足：

- exporter 提供不可变数据；或
- 调用者承诺期间不修改；或
- consumer 自己复制快照；或
- 双方共享明确的锁。

“没有复制”会把一部分性能成本转换成生命周期和同步责任。

## NumPy 边界

NumPy 数组实现 buffer protocol，但生产数值扩展常使用 NumPy C API、Cython typed memoryview 或 pybind11/nanobind 等工具获得更丰富的 dtype 和 shape 支持。

无论使用哪种工具，仍需验证：

- dtype 是否匹配
- 是否 contiguous
- 字节序是否匹配
- 是否允许修改
- 输出由谁分配

已有 NumPy ufunc 能完成任务时，应先使用成熟实现，而不是重新编写简单 C 循环。

## 常见错误

- 把任意 iterable 当成零拷贝输入
- 只检查总字节数，不检查 format 和 itemsize
- 获取 view 后某个错误分支忘记 `PyBuffer_Release`
- 保存 `view.buf` 到函数返回以后
- 忽略非连续切片的 strides
- 释放 GIL 后让其他线程同时修改可写缓冲区
- 把 native double 内存直接当作跨平台文件格式

## 检查点

1. `memoryview` 对象是否拥有底层数据？通常不拥有，它保持 exporter 引用。
2. zero-copy 是否意味着没有生命周期约束？恰恰相反。
3. 为什么 `len` 是 80 字节不能证明它包含 10 个合法 double？
4. `PyObject_GetBuffer` 成功后哪个操作必须恰好执行一次？`PyBuffer_Release`。

## 动手练习

1. 运行 `make test`，观察 `array('d')` 成功、`array('f')` 被拒绝。
2. 比较 `sum_doubles` 和 `sum_doubles_buffer` 的对象创建与计时。
3. 用 memoryview 创建非连续切片，确认当前接口拒绝它。
4. 扩展 C API，使其接受 strided 一维 double view，并测试负 stride。
5. 设计一个原地缩放接口，明确 writable、别名和异常时部分修改的契约。
