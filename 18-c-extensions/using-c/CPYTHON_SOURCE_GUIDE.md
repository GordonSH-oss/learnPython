# CPython 源码阅读指南

## 这份指南的定位

CPython 源码阅读能帮助你理解 Python/C API 背后的对象、解释器和内存机制，但它不是编写扩展的稳定接口文档。扩展代码应优先使用公开 Python/C API，不要复制内部结构、私有函数或某个版本的宏实现。

CPython 内部会随版本、构建选项和实验特性变化。阅读前必须固定一个 tag，并始终把页面或笔记标注到该版本：

```bash
git clone https://github.com/python/cpython.git
cd cpython
git checkout v3.14.0   # 示例；选择与你实际使用的版本一致的 tag
```

不要一边阅读 `main` 分支，一边用旧博客中的 3.10 结构解释代码。

## 学习目标

阅读完成后，你应该能够：

- 从一个 Python 行为定位到公开 API、类型 slot 和具体实现函数
- 区分 stable/public API、CPython-specific API 和内部私有实现
- 解释对象头、类型对象、引用所有权和循环 GC 的职责边界
- 识别传统 GIL 构建、free-threaded 构建和 immortal objects 对旧心智模型的影响
- 使用测试、`dis`、debug build 和调试器验证源码理解

## 源码目录地图

常见入口如下；精确文件会随版本调整：

```text
Include/             公开和 CPython-specific 头文件
Include/cpython/     通常不是 Limited API 的具体结构或接口
Include/internal/    CPython 内部接口，不供普通扩展使用
Objects/             list、dict、long、type 等对象实现
Python/              执行器、编译、解释器状态和运行时核心
Modules/             标准库 C 模块和示例扩展
Parser/              解析器相关实现
Lib/                 Python 编写的标准库
Tools/               构建、调试和开发工具
```

先查看当前 tag 的实际目录，不要把这张地图当成永久文件清单。

## 三层 API 边界

阅读任何符号前，先判断它属于哪一层：

| 层次 | 常见位置或标记 | 扩展能否依赖 |
| --- | --- | --- |
| Limited API / Stable ABI | 受 `Py_LIMITED_API` 约束的公开 API | 可用于更宽 CPython 版本范围，但功能是子集 |
| CPython public API | `Python.h` 暴露但可能绑定 CPython 小版本 ABI | 普通 CPython 扩展可用，需要按支持版本构建测试 |
| Internal API | `_Py` 前缀、`Include/internal`、实现文件私有符号 | 不应由第三方扩展依赖 |

看到一个 `_Py...` 函数能解决问题，不代表它适合复制到扩展中。

## 对象模型：使用概念图，不背字段布局

传统教学模型是：

```text
PyObject-compatible prefix
├── 引用管理相关状态
└── 类型指针 -> PyTypeObject
```

变长对象还具有逻辑长度信息。具体字段类型、顺序和宏展开可能因版本、debug、trace-refs、free-threaded 或其他构建选项变化。

稳定结论是：

- Python/C API 通过 `PyObject *` 表示一般 Python 对象。
- 类型决定对象支持的协议和 slot。
- 扩展应通过 `Py_INCREF`、`Py_DECREF`、类型检查和公开访问 API 操作对象。
- 不应在第三方扩展中直接修改 `ob_refcnt` 或猜测对象内存布局。

## 引用所有权

阅读函数时，为每个 `PyObject *` 标注：

```text
borrowed   当前代码不拥有
new/strong 当前代码拥有，必须转交或 DECREF
stolen     被调用函数成功后接管当前引用
```

检查失败路径时画资源表：

| 资源 | 获取位置 | 成功时去向 | 失败时释放 |
| --- | --- | --- | --- |
| 临时 tuple | `PyTuple_New` | 返回或放入容器 | `Py_DECREF` |
| 元素引用 | API 返回约定 | 转交/保存 | 根据 borrowed/new 决定 |
| `Py_buffer` | `PyObject_GetBuffer` | 只在调用期间使用 | `PyBuffer_Release` |

引用计数归零通常触发对象析构流程，但不能把“每个变量赋值都简单 +1”“每个对象都能观察到普通递增计数”当成现代 CPython 的完整模型。immortal objects、优化和 free-threaded 实现会改变内部细节。扩展只依赖公开引用 API 的语义。

循环引用由 cyclic GC 处理，而不是单靠引用计数。拥有容器字段的自定义类型需要正确实现 traverse 和 clear 协议。

## 类型对象和 slot

`PyTypeObject` 描述类型行为。阅读一个 Python 操作时，先把语法映射到协议：

| Python 行为 | 可能相关的 API/slot |
| --- | --- |
| `len(obj)` | sequence/mapping length slot |
| `obj[index]` | mapping 或 sequence subscription |
| `a + b` | number add slot和通用分派 |
| `iter(obj)` | iteration slot |
| `obj.name` | attribute access、descriptor protocol |
| `obj()` | call/vectorcall 路径 |

不要假定方法调用只是在线性 `tp_methods` 数组中搜索。现代 CPython 包含描述符、缓存、vectorcall 和专门化等多层机制。

## 从行为追踪 list

以 `list.append` 为例：

1. 在 Python 中写最小行为和边界测试。
2. 使用 `list.append.__doc__`、公开 C API 文档确认契约。
3. 在当前 tag 搜索 `list.append` 的 Argument Clinic 生成入口或实现函数。
4. 继续跟到调整容量和写入元素的位置。
5. 标注错误返回、引用所有权和锁/GIL 假设。

可以确认的高层模型是：list 保存对象引用的动态数组，append 通常具有均摊 O(1) 复杂度。具体过分配公式和同步实现属于版本细节，必须从所选 tag 的真实 `listobject.c` 验证。

配套的 `list_internals.c` 只是一份概念伪代码，不是可复制实现。

## 从行为追踪 dict

建议问题：

- 哈希值在哪里计算和缓存？
- 查找如何处理碰撞？
- 插入顺序由哪些结构保存？
- resize 的触发条件是什么？
- split/combined table 在当前版本如何使用？
- free-threaded 构建需要哪些同步或临界区？

“平均 O(1)”是算法复杂度结论，不代表每次操作固定成本，也不代表恶意碰撞、resize 或对象比较没有影响。

## 字节码与执行器

先用当前解释器查看字节码：

```python
import dis

def add(left, right):
    return left + right

dis.dis(add, adaptive=True, show_caches=True)
```

现代 CPython 可能使用 adaptive specialization、inline cache 和生成的 opcode case。旧资料中的 `BINARY_ADD`、`CALL_FUNCTION` 或固定 `switch` 结构可能已经不对应当前版本。

阅读顺序：

1. `dis` 输出当前 opcode。
2. 搜索 opcode 定义、生成模板或 executor 实现。
3. 找到 fallback 的通用对象操作。
4. 比较首次执行和热身后的专门化行为。

不要先假定所有版本都在 `Python/ceval.c` 的同一个巨大 switch 中执行。

## GIL、解释器和 free-threaded

阅读并发实现时先确认构建类型：

- 传统 GIL 构建
- 可选 free-threaded 构建
- subinterpreter 和 per-interpreter 状态

问题清单：

- 当前代码需要持有什么锁或 critical section？
- 对象是否可能被另一个线程修改？
- 全局状态是 process-wide 还是 per-interpreter？
- borrowed reference 在并发修改下是否仍稳定？
- 扩展是否声明或实际支持 free-threaded 运行？

不要把“持有 GIL 所以所有 C 全局状态安全”作为长期扩展设计。

## 推荐阅读路线

| 阶段 | 目标 | 推荐入口 |
| --- | --- | --- |
| 1 | 扩展模块生命周期 | `Modules/` 中较小模块、module definition |
| 2 | 对象和引用 API | `Include/object.h`、公开 C API 文档 |
| 3 | list 动态数组 | `Objects/listobject.c` |
| 4 | long 任意精度整数 | `Objects/longobject.c` |
| 5 | dict 哈希表 | `Objects/dictobject.c` |
| 6 | 类型与 descriptor | `Objects/typeobject.c` |
| 7 | 字节码执行和专门化 | `Python/`、generated cases、`dis` |
| 8 | GC 和解释器状态 | GC、interpreter/runtime state 相关文件 |

每次只追踪一个可观察行为，不要按目录从头通读。

## 验证工具

构建 debug CPython：

```bash
./configure --with-pydebug
make -j4
./python -X dev -m test test_list
```

常用工具：

```bash
git grep 'symbol_name'
./python -m dis script.py
lldb -- ./python -c 'code'
```

给源码加日志前先写一个最小测试。修改实现后运行对应 CPython 测试，不要只运行自己的演示脚本。

## 阅读记录模板

每次源码追踪记录：

```text
CPython tag / commit:
构建选项:
Python 可观察行为:
公开 API 契约:
入口符号:
关键调用路径:
对象/资源所有权:
异常或错误返回:
锁/GIL 假设:
版本敏感实现细节:
验证测试:
```

最终目标不是背诵结构体字段，而是能从公开行为追踪到实现，再回到公开契约判断哪些知识可以用于扩展设计。
