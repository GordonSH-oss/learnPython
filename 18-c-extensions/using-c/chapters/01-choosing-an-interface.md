# 01 Python 调用 C 的基础概念与路径选择

## 学习目标

完成本章后，你应该能够：

- 解释 API、ABI、FFI、动态库和 Python 扩展模块的区别
- 描述 `ctypes`、Python/C API 和 Cython 各自怎样连接 Python 与 C
- 从数据转换、异常、GIL、构建、发布和维护成本比较三条路径
- 判断一个性能问题是否适合迁移到 C
- 为具体项目写出有依据的接口选择和验证计划

## “使用 C 加速 Python”包含哪些工作

把一段循环改写成 C 只是中间步骤。完整路径通常包含：

```text
Python 调用者
   ↓ 参数检查
Python 对象 -> C 值或缓冲区
   ↓ 跨语言调用
C 算法或第三方 C 库
   ↓ 状态码、错误或结果
C 值 -> Python 对象
   ↓
Python 调用者
```

还要处理：

- C 代码怎样编译成目标平台能加载的二进制
- Python 和 C 怎样约定参数、返回值和内存布局
- 输入数据是否需要复制
- C 错误怎样变成 Python 异常
- C 代码是否能释放 GIL
- 原生崩溃怎样调试
- macOS、Linux、Windows 和不同 Python 版本怎样发布

因此，“哪条路径最快”通常不是第一个问题。第一个问题是：需要跨越什么边界，谁负责维护这个边界？

## API 与 ABI

### API：源代码层面的契约

API 描述调用者在源代码中使用的名称、类型和行为。例如：

```c
int sum_squares(int32_t limit, int64_t *result);
```

头文件告诉 C 编译器：函数叫什么、参数和返回类型是什么。文档还应说明负数、溢出、空指针和输出参数规则。

Python API 则可能写成：

```python
sum_squares(limit: int) -> int
```

两侧 API 可以不同，包装层负责在它们之间转换。

### ABI：二进制层面的契约

ABI 决定编译后的程序怎样真正互相调用，包括：

- 参数通过哪些寄存器或栈位置传递
- `int`、`long`、指针和结构体的大小与对齐
- 函数符号名称
- 调用约定
- 动态库格式和目标 CPU 架构

API 看起来相同，ABI 仍可能不兼容。例如把声明中的 `int32_t` 错写成 `long`，在当前机器的小输入上可能暂时工作，却在另一平台截断参数或破坏调用。

`ctypes` 直接依赖 C ABI；Python/C API 扩展还依赖目标 Python 提供的扩展 ABI；Cython 最终也会生成使用这些 ABI 的 C 代码。

## FFI 是什么

FFI（Foreign Function Interface）是“一种语言调用另一种语言接口”的机制。

在本教程中：

- `ctypes` 是 Python 运行时提供的动态 FFI。
- Python/C API 是 CPython 原生扩展接口。
- Cython 是生成扩展胶水代码的编译工具。

其他常见工具还有 cffi、pybind11、nanobind、SWIG 和 Rust 的 PyO3。它们解决相似边界问题，但抽象层、目标语言和发布方式不同。本教程先掌握三条基础路径，因为它们能清楚展示 ABI、Python 对象模型和生成代码之间的关系。

## 动态库与 Python 扩展模块

二者都可能是 `.so` 或 `.dylib` 一类原生文件，但加载者和入口契约不同。

### 普通 C 动态库

```text
libarithmetic.dylib / libarithmetic.so
```

它导出普通 C 函数，例如 `sum_squares`。C、Python、Ruby 或其他支持该 ABI 的程序都可以加载它。库本身通常不知道 Python 对象和异常。

### Python 扩展模块

```text
mymath.cpython-314-darwin.so
```

它由 Python 的 import 系统加载，必须导出类似 `PyInit_mymath` 的初始化入口，并使用 Python/C API 创建模块和对象。

```text
import mymath
   ↓ Python import machinery
加载扩展二进制
   ↓
PyInit_mymath()
   ↓
返回 Python 模块对象
```

普通动态库不能只因为后缀是 `.so` 就直接 `import`；Python 扩展也不等于一个适合任意语言调用的普通 C ABI。

## 路径一：`ctypes`

### 基础概念

`ctypes` 是 Python 标准库中的 FFI。Python 在运行时加载已经编译好的动态库，按手工声明的 C 签名调用函数。

```text
Python
  ↓ ctypes.CDLL
动态链接器加载 C 库
  ↓ argtypes/restype 描述 ABI
C 函数
```

示意代码：

```python
library = ctypes.CDLL("libarithmetic.dylib")
library.sum_squares.argtypes = [
    ctypes.c_int32,
    ctypes.POINTER(ctypes.c_int64),
]
library.sum_squares.restype = ctypes.c_int
```

### 谁负责什么

- C 头文件定义真实 ABI。
- Python 包装层手工维护 `argtypes` 和 `restype`。
- C 通常返回状态码；包装层转换为 Python 异常。
- Python 包装层管理 ctypes 对象和传入内存的生命周期。
- 普通 `CDLL` 调用期间通常释放 GIL，但底层库必须自己保证线程安全。

### 适合场景

- 已有供应商或系统 C 库
- 需要先快速验证一个 C ABI
- 接口主要由整数、浮点、指针、结构体和连续缓冲区组成
- 不需要创建复杂 Python 原生类型

### 主要限制

- 不会读取头文件，签名容易与 C 漂移
- 每次调用有 ctypes 调度和转换成本
- 复杂结构体、回调和所有权协议容易出错
- 错误指针会直接破坏 Python 进程
- 动态库仍需随应用正确分发和定位

### 一个常见误区

`ctypes` 不等于“无需编译”。Python 包装层不需要编译，但被调用的 C 库仍然必须为目标操作系统和 CPU 架构编译。

## 路径二：Python/C API

### 基础概念

Python/C API 是 CPython 提供的原生扩展接口。C 代码直接接收和返回 `PyObject *`，可以创建模块、函数、异常和自定义 Python 类型。

```text
Python import
   ↓
PyInit_module
   ↓
方法表注册 C 函数
   ↓
C 函数解析 PyObject 参数
   ↓
返回 PyObject 或设置异常并返回 NULL
```

示意函数：

```c
static PyObject *module_sum_squares(PyObject *module, PyObject *argument) {
    long long limit = PyLong_AsLongLong(argument);
    if (limit == -1 && PyErr_Occurred()) {
        return NULL;
    }
    /* 计算并返回新的 Python int 对象。 */
}
```

### 谁负责什么

- 扩展作者负责参数解析和类型检查。
- Python 异常通过 Python/C API 设置。
- 扩展作者必须遵守新引用、借用引用和 stolen reference 规则。
- buffer view、C 内存和临时 Python 对象必须在失败路径释放。
- 只有纯 C 区域可以考虑释放 GIL。
- 构建产物通常绑定 CPython 版本、平台和架构。

### 适合场景

- 需要直接操作 Python 对象或协议
- 需要创建自定义 Python 类型
- 需要 buffer protocol、vectorcall、模块状态或精确异常控制
- 需要把底层库包装成紧密集成的 Python 模块
- 团队愿意承担原生生命周期和多平台构建成本

### 主要限制

- 胶水代码较多
- 引用计数和错误路径容易出错
- 使用 CPython-specific API 时通常需要为多个 Python 版本构建 wheel
- 越界、空指针或引用错误会让解释器崩溃
- subinterpreter 和 free-threaded CPython 会提高状态管理要求

### Stable ABI 是什么

Python Limited API/Stable ABI 提供一组较稳定的 API 子集，可以减少按 CPython 小版本重新构建的需求。但它不会自动解决：

- 操作系统和 CPU 架构差异
- 第三方动态库 ABI
- 不在 Limited API 中的功能需求
- 自己 C 数据结构的线程安全和兼容性

因此，“Python/C API 一定绑定每个小版本”和“Stable ABI 可以发布一个适用于所有平台的文件”都过于绝对。

## 路径三：Cython

### 基础概念

Cython 是源代码转换器和扩展构建工具。它把 Python-like `.pyx` 代码转换成 C，再生成 Python 扩展模块。

```text
cython_example.pyx
   ↓ Cython
generated C
   ↓ C compiler
Python extension module
```

代码可以从普通 Python 风格开始，再逐步增加 C 类型：

```cython
def sum_values(double[::1] values):
    cdef Py_ssize_t index
    cdef double total = 0
    for index in range(values.shape[0]):
        total += values[index]
    return total
```

### 谁负责什么

- Cython 生成参数解析、对象操作和大量引用管理代码。
- 开发者仍负责类型范围、算法、C 资源和 buffer 契约。
- `nogil` 区域不能任意操作 Python 对象。
- 构建结果仍是需要按平台发布的原生扩展。
- annotation HTML 用于识别仍在与 Python 运行时交互的热点。

### 适合场景

- 已有 Python 数值或扫描循环需要渐进类型化
- 希望保留接近 Python 的实现形式
- 需要 typed memoryview 处理连续数据
- 希望包装现有 C 库，但不想手写全部 Python/C API 胶水
- 团队接受 Cython 作为构建依赖

### 主要限制

- 只增加少量类型不一定消除 Python 对象操作
- 生成的 C 很大，调试时仍需理解 Python/C API
- 关闭边界检查后可能产生原生越界
- C 整数与 Python 整数语义不同
- wheel、ABI、平台和 GIL 问题仍然存在

### 一个常见误区

Cython 不是“自动把任意 Python 程序变成高性能 C”。动态 dict、任意对象调用和 Python list 操作仍然需要 Python 运行时。收益通常来自把热循环中的数据和控制流变成静态 C 操作。

## 三条路径的共同边界

无论选择哪条路径，都必须回答：

1. Python 输入允许哪些类型和值？
2. C 侧使用什么精确类型？
3. 数据是复制、借用还是转移所有权？
4. 指针有效到什么时候？
5. C 失败怎样转换为 Python 异常？
6. 调用期间是否持有 GIL？
7. 多线程是否可能同时进入 C？
8. 二进制怎样为目标平台构建和发布？

工具只能减少部分胶水代码，不能替代边界契约。

## 同维度对比

| 维度 | `ctypes` | Python/C API | Cython |
| --- | --- | --- | --- |
| 主要输入 | 已编译 C 动态库 | C 源码和 Python headers | `.pyx`、Cython 和 C 编译器 |
| Python 侧使用 | 普通 `.py` 包装器 | 直接 `import` 原生模块 | 直接 `import` 生成模块 |
| C 接口形式 | 普通 C ABI | `PyObject *` 和 Python/C API | 生成的 Python/C API 胶水，可声明 C 接口 |
| 参数声明 | Python 中手写 `argtypes/restype` | C 中手写解析逻辑 | Cython 根据类型声明生成 |
| Python 对象操作 | 间接，通常先转 C 值 | 最直接、控制最细 | 支持，开销取决于生成代码 |
| buffer 支持 | `from_buffer`、指针 | `Py_buffer`，控制最细 | typed memoryview 较方便 |
| 错误模型 | C 状态码/errno 转 Python 异常 | 设置异常并返回错误标记 | 可用 Python 异常，也需映射 C 错误 |
| 引用管理 | ctypes 对象生命周期为主 | 手工遵守引用所有权 | 大部分自动生成，C 资源仍需手工管理 |
| GIL | `CDLL` 调用通常释放 | 显式决定何时释放 | `nogil` 显式控制 |
| 初始代码量 | 低 | 高 | 中 |
| 调试透明度 | ABI 边界直接，但签名靠人工 | 最接近 CPython 运行时 | 需结合 `.pyx`、生成 C 和 annotation |
| 发布内容 | Python 包装器加动态库 | Python 扩展 wheel | Python 扩展 wheel |
| 版本风险 | C 库 ABI 和平台 | CPython API/ABI 和平台 | Cython 版本、CPython ABI 和平台 |
| 最适合 | 包装已有 C 库 | 深度集成 Python 对象模型 | 渐进加速 Python 算法 |

## 性能不能只按工具排名

三条路径最终都可能进入同一段 C 循环。真正影响性能的往往是：

- 每次调用做多少工作
- 是否逐元素跨越边界
- 是否复制输入
- 是否创建大量 Python 对象
- C 算法是否更优
- 是否被内存带宽、锁或 I/O 限制

例如：

```text
ctypes 每次调用处理 1 个数       -> 边界成本可能占主导
ctypes 一次处理 100 万个 double -> 可能非常有效
C API 每轮回调 Python           -> 重新引入 Python 开销
Cython 热循环仍操作 dict        -> 类型化收益有限
```

不能简单写出“Python/C API 一定比 ctypes 快”或“Cython 最快”。必须对真实接口和数据流做 benchmark。

## 从热点开始，而不是从 C 开始

程序总耗时可以粗略拆成：

```text
总耗时 = Python 计算 + I/O 等待 + 边界转换 + C 计算
```

C 只能直接减少其中一部分。网络请求慢、数据库查询慢或算法复杂度不合理时，重写循环通常没有价值。

先定位热点：

```bash
python3 -m cProfile -s cumulative program.py
python3 -m timeit -s 'data = list(range(10000))' 'sum(data)'
```

- `cProfile` 适合找函数级累计耗时。
- `timeit` 适合比较小段稳定代码。
- `py-spy`、Scalene 等采样工具适合降低 profiler 扰动或区分 Python/native 时间。

分析时使用接近真实规模的输入，并分别观察 CPU、I/O、内存和端到端延迟。

## C 为什么可能更快

Python 循环中的运算通常涉及对象、动态类型和解释器执行。类型明确的 C 循环可以直接处理机器值：

```text
Python 循环：解释执行 -> 对象类型 -> 操作分派 -> Python 对象结果
C 循环：     加载机器值 -> 算术/比较 -> 存储机器值
```

适合迁移的热点通常具有：

- 大量数值、字节或文本扫描
- 稳定明确的元素类型
- 可以一次提交整批数据
- 较少回调 Python
- profiler 已确认占据显著 CPU 时间

通常不适合：

- 每次调用只做一两个简单操作
- 主要耗时来自网络、数据库或磁盘等待
- Python 层算法复杂度明显不合理
- 业务逻辑仍频繁变化
- NumPy、压缩库、解析器或其他成熟实现已经解决问题

## 选择路径的决策顺序

```text
已有成熟实现或 NumPy 操作？
   ├── 是：优先复用并测量
   └── 否
        ↓
已有稳定 C ABI？
   ├── 是：先用 ctypes 验证
   └── 否
        ↓
需要直接创建/操作 Python 对象、类型或模块状态？
   ├── 是：Python/C API，或评估更高层绑定工具
   └── 否
        ↓
热点主要是已有 Python 循环，适合渐进类型化？
   ├── 是：Cython
   └── 否：重新检查算法和边界设计
```

真实项目可以组合使用：

- Cython 包装现有 C 头文件
- Python/C API 暴露一个零拷贝 buffer 接口
- ctypes 先验证 C ABI，再迁移到可发布扩展
- 纯 Python 提供公共 API，底层根据平台选择原生或回退实现

## 典型场景对比

### 场景一：供应商提供 `.dylib` 和头文件

优先从 ctypes 开始。先验证函数签名、错误码、线程安全和动态库部署。若接口复杂、调用非常频繁或最终需要 wheel，可再评估 Cython/cffi 或手写扩展。

### 场景二：加速 Python 图像数组循环

先确认 NumPy、Pillow、OpenCV 是否已有向量化实现。若没有，并且数据可通过连续 buffer 表示，可考虑 Cython typed memoryview 或 Python/C API buffer。

### 场景三：创建一种新的 Python 容器类型

需要类型 slot、GC、descriptor、模块状态和引用管理，Python/C API 或能生成相应扩展的绑定工具更合适。ctypes 不适合创建深度集成的 Python 类型。

### 场景四：解析一个大型二进制协议

若已有成熟 C 解析库，ctypes 可以快速集成；若要返回大量 Python 对象，应设计批量或结构化结果，避免每个字段跨边界调用。长期产品可能使用 C API/Cython 做更紧密包装。

### 场景五：每次请求只计算两个整数相加

任何原生路径都可能比直接 Python 加法更复杂，调用成本也可能超过收益。不要迁移。

## 加速目标必须包含正确性

Python `int` 是任意精度整数，C 的 `int64_t` 范围有限。Python 下标越界抛异常，错误 C 指针访问可能直接崩溃。

性能目标应写成：

> 对已定义的输入类型和范围，产生与 Python 基线相同的结果和异常语义，并在代表性负载上降低测得的端到端成本。

验证顺序：

```text
定义契约
   ↓
纯 Python 参考实现
   ↓
边界和错误测试
   ↓
原生实现
   ↓
结果一致性
   ↓
benchmark
   ↓
发布和平台测试
```

本教程先运行 `test_using_c.py`，再运行 `benchmark.py`。

## 选择记录模板

为真实项目填写：

```text
热点函数：
输入规模和调用频率：
当前耗时占比：
主要成本：Python 计算 / I/O / 分配 / 数据复制
现有成熟库：
数据能否连续表示：
是否需要操作任意 Python 对象：
是否需要 Python 回调：
是否需要释放 GIL：
目标 Python/OS/CPU：
选择路径：
不选择其他路径的原因：
正确性测试：
benchmark 范围：
回退方案：
```

## 理解检查

1. C API 头文件与 ABI 分别解决什么问题？
2. 普通 `.so` 为什么不一定可以直接 `import`？
3. ctypes 为什么不等于“不需要编译”？
4. Python/C API 为什么能直接创建异常，而普通 C ABI 通常返回状态码？
5. Cython 为什么仍需考虑 C 整数溢出和 wheel 平台？
6. 一个 API 每秒调用一百万次、每次只做一次加法，迁移到 C 为什么可能更慢？
7. 一个请求 90% 时间等待数据库，计算热点加速十倍后为什么整体收益有限？

## 动手练习

1. 选择自己的 Python 程序，用 profiler 找出累计耗时最高的三个函数。
2. 对每个函数记录 CPU、I/O、数据转换和调用频率。
3. 使用本章模板分别评估 ctypes、Python/C API 和 Cython。
4. 为其中一个函数画出 Python 对象进入 C、执行计算、返回 Python 的完整数据流。
5. 写出至少一个“不应该使用 C”的理由，以及在什么测量结果下会重新考虑。
