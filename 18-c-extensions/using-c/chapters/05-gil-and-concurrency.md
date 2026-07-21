# 05 GIL、线程与并发边界

## 学习目标

完成本章后，你应该能够：

- 区分“持有 GIL”“线程安全”和“代码并行”
- 判断一段 C 代码能否安全地在无 GIL 状态运行
- 使用 `Py_BEGIN_ALLOW_THREADS` 包围纯 C 阻塞或长计算
- 在重新获取 GIL 后设置异常和创建 Python 对象
- 为共享 C 状态、回调和 buffer 设计同步协议
- 理解 free-threaded CPython 对扩展提出的新要求

## GIL 保护什么

传统 CPython 构建中的 GIL 主要串行化 Python 字节码执行，并保护大量解释器内部状态。它不是：

- 任意 C 库的线程安全保证
- 用户数据结构的业务事务锁
- 让单个函数自动并行的调度器
- 可以替代 mutex 的通用同步机制

扩展函数从 Python 被调用时通常持有 GIL，因此可以使用 Python/C API。释放 GIL 后，当前线程不能再随意访问 Python 对象或调用要求 GIL 的 API。

## 什么时候考虑释放

适合释放的工作：

- 不操作 Python 对象的长时间 C 数值循环
- 阻塞文件、网络或设备 I/O
- 已知自身线程安全的第三方库调用
- 只访问线程局部或有独立同步保护的 C 数据

不适合盲目释放：

- 只有几十条机器指令的短函数
- 循环中频繁创建 Python 对象
- 需要调用 Python 回调
- 读取可能被其他线程修改的 Python 导出缓冲区
- 操作没有线程安全契约的 C 全局状态

释放和重新获取 GIL 本身有成本，必须通过真实并发负载测量。

## 基本模式

```c
int failed = 0;
long result = 0;

Py_BEGIN_ALLOW_THREADS
/* 这里只操作纯 C 数据。失败写入普通 C 状态。 */
Py_END_ALLOW_THREADS

if (failed) {
    PyErr_SetString(PyExc_RuntimeError, "calculation failed");
    return NULL;
}
return PyLong_FromLong(result);
```

`Py_BEGIN_ALLOW_THREADS` 会保存当前线程状态并释放 GIL，`Py_END_ALLOW_THREADS` 重新获得 GIL。宏形成作用域，变量声明位置要注意。

无 GIL 区域不能直接调用 `PyErr_SetString`，因为异常保存在 Python 线程状态中。应记录 C 错误码，回到持有 GIL 的区域再转换成 Python 异常。

## 释放 GIL 不会自动并行

如果只有一个线程调用函数，释放 GIL 不会让该循环自己使用多个核心。它只允许其他线程在此期间运行。

真正并行需要：

- 多个 Python 线程同时进入可释放 GIL 的扩展代码；或
- C 库内部创建线程；或
- OpenMP、线程池等明确并行实现。

并行还必须考虑工作划分、缓存、内存带宽、合并成本和数据竞争。计算太短时，线程管理成本可能超过收益。

## ctypes 的行为

`ctypes.CDLL` 创建的外部函数调用通常在调用期间释放 GIL，适合普通 C ABI。`ctypes.PyDLL` 保留 GIL，主要用于调用 Python C API。

这意味着同一个 `CDLL` 函数可能被多个 Python 线程并发执行。底层 C 库若使用普通全局变量、静态临时缓冲区或非线程安全句柄，必须由 C 库或 Python 包装层加锁。

不要因为 Python 有 GIL，就假定通过 ctypes 调用的所有 C 函数天然串行。

## 共享 C 状态

考虑一个模块级缓存：

```c
static int initialized;
static Table *cache;
```

它需要回答：

- 初始化是否可能被两个线程同时执行？
- 缓存读取期间是否会被另一线程替换或释放？
- 模块卸载或解释器结束时谁清理？
- 多个 subinterpreter 是否应该共享同一份状态？

优先把状态放进 per-module state，并使用 mutex、原子操作或一次性初始化原语保护。不要依赖“现在调用都持有 GIL”作为永久设计，特别是面向 free-threaded 构建时。

## Buffer 与 GIL

拿到 `Py_buffer` 后，底层地址在 view 生命周期内通常保持有效，但内容可能仍可修改。

```text
线程 A：释放 GIL 后遍历 double buffer
线程 B：修改同一个 array('d') 元素
```

如果双方没有同步，这可能是数据竞争。解决方案包括只接受不可变数据、复制快照、保持 GIL或使用双方认可的锁。

## Python 回调

C 调用 Python 回调前必须确保当前线程拥有有效 Python thread state 和 GIL。由 Python 调入 C、且仍持有 GIL 的同步回调较简单；由 C 创建的外部线程回调 Python 则需要使用适当的 thread-state API。

回调接口还应定义：

- Python callable 的强引用由谁保存
- 何时注销，如何防止注销后调用
- 回调异常如何转换为 C 状态
- C 是否在持锁时调用回调
- 解释器关闭时如何停止后台线程

在持有 C mutex 时调用未知 Python 代码容易形成锁顺序反转和死锁。通常先复制必要状态、释放 C 锁，再调用 Python。

## Free-threaded CPython

较新的 CPython 提供可选的 free-threaded 构建。扩展不能再把 GIL 当作隐式全局互斥锁。即使某些 API 仍提供内部安全机制，扩展自己的全局变量、借用引用、容器迭代和对象字段访问也必须遵守目标版本的官方扩展指南。

生产发布时应明确：

- wheel 是否支持 free-threaded ABI 标签
- 使用的 Python/C API 是否在目标构建中允许
- 第三方 C 库是否线程安全
- 测试是否覆盖真正并发调用，而不只是单线程导入

不要通过旧版 CPython 内部结构推测 free-threaded 行为。

## 常见错误

- 无 GIL 时调用 Python/C API
- 在无 GIL 区域设置 Python 异常
- 释放 GIL 后读取同时可变的 Python buffer
- 认为释放 GIL 会自动并行化循环
- 认为 GIL 会保护 ctypes 调用的 C 全局变量
- C 后台线程在解释器关闭后继续回调 Python
- 持有 C 锁时调用任意 Python callable

## 检查点

1. 释放 GIL 后能否调用 `PyLong_FromLong`？不能。
2. 两个 Python 线程能否同时进入同一个 `ctypes.CDLL` 函数？通常可以。
3. 持有 buffer view 是否保证元素内容不可改变？不保证。
4. free-threaded 构建中普通 C 全局变量由谁保护？扩展作者。

## 动手练习

1. 写一个长计算扩展函数，分别保持和释放 GIL；启动两个 Python 线程观察其他线程响应性。
2. 给一个 C 全局计数器编写并发测试，用 ThreadSanitizer 或锁证明数据竞争。
3. 让两个线程同时调用 `sum_doubles_buffer`，说明输入是否共享以及为什么当前实现保持 GIL。
4. 设计一个 C 后台任务 API，列出 callable、任务句柄和解释器关闭时的所有权关系，但不要在协议未明确前实现。
