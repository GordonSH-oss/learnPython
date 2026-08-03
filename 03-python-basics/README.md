# Python 基础：从语法到运行时

本目录不是按文件创建时间排列的笔记，而是一条从“能读懂 Python 代码”到“能解释 Python 行为”的学习路线。建议按单元顺序学习；每个单元先看本页的目标，再运行对应的 `.py` 示例，最后阅读专题文档和完成练习。

## 先看这张地图

| 单元 | 要回答的问题 | 主要文件 | 前置 |
| --- | --- | --- | --- |
| 1. 对象、函数与作用域 | Python 如何绑定名称、调用函数和保存状态？ | `self_examples.py`、`args_and_kwargs.py`、`legb_scope.py`、`closures.py`、`data_class.py`、`copy.py` | Python 基础语法 |
| 2. 对象协议与面向对象 | 为什么 `len(x)`、`x + y`、`for x in y` 能作用于自定义对象？ | `special-methods/`、`slice_explanation.py`、`polymorphism.py`、`DUCK_TYPING.md` | 单元 1 |
| 3. 可组合的控制流 | 什么时候应该立即计算，什么时候应该延迟计算？ | `generator-comprehension/`、`generator.py`、`decorators.py` | 单元 1 |
| 4. 模块、错误与运行时 | 代码如何被加载？错误如何传播？并发和 GIL 影响什么？ | `module_loading_tutorial.py`、`error_handling.py`、`asyn.py`、`gil.py` | 单元 1 |
| 5. 数据边界与标准库 | 如何把外部数据变成可靠的内部对象，并组合标准库解决实际问题？ | `pydantic/`、`standard_library_tour.py`、`COMPRESSION.md` | 单元 1、2 |

## 单元 1：对象、函数与作用域

目标：建立“名称指向对象”的模型，理解实例方法、参数绑定、LEGB 作用域和闭包状态。

1. [`SELF_EXPLANATION.md`](SELF_EXPLANATION.md) / [`self_examples.py`](self_examples.py)：实例方法、类方法和静态方法。
2. [`args_and_kwargs.py`](args_and_kwargs.py)：位置参数、关键字参数、解包和参数顺序。
3. [`legb_scope.py`](legb_scope.py)：局部、嵌套、全局和内置作用域。
4. [`CLOSURES.md`](CLOSURES.md) / [`closures.py`](closures.py)：自由变量、`nonlocal` 和状态隔离。
5. [`data_class.py`](data_class.py)：用 `@dataclass` 表达数据，避免可变默认值陷阱。
6. [`copy.py`](copy.py)：区分赋值、浅拷贝和深拷贝；注意该示例文件名会遮蔽标准库 `copy`，代码中已展示规避方式。

检查点：解释 `obj.method()` 为什么等价于把 `obj` 作为第一个参数传入；解释闭包和类分别适合表达什么状态。

## 单元 2：对象协议与面向对象

目标：从“继承”扩展到“协议”：对象只要提供约定的方法，就能参与 Python 的运算、索引、迭代和比较。

1. [`special-methods/README.md`](special-methods/README.md)：先读总览，再按 `property`、表示、比较、算术、容器顺序运行示例。
2. [`slice_explanation.py`](slice_explanation.py)：理解 `items[:3]` 如何变成 `__getitem__(slice(...))`。
3. [`DUCK_TYPING.md`](DUCK_TYPING.md)：鸭子类型、`Protocol`、ABC 与 EAFP/LBYL。
4. [`polymorphism.py`](polymorphism.py)：继承、多态和方法重写。
5. [`SINGLEDISPATCH.md`](SINGLEDISPATCH.md) / [`singledispatch.py`](singledispatch.py)：按第一个参数类型分派。
6. [`MULTIPLEDISPATCH.md`](MULTIPLEDISPATCH.md) / [`multiple_dispatch.py`](multiple_dispatch.py)：第三方库的多参数分派；先掌握 `singledispatch` 再学习。

检查点：为一个自定义容器补齐 `__len__`、`__getitem__` 和 `__iter__`，让它能被 `len()`、索引和 `for` 使用。

## 单元 3：可组合的控制流

目标：理解“表达式生成集合”和“迭代器逐项产出”的边界，并看懂装饰器如何包装调用。

- [`generator-comprehension/COMPREHENSIONS_VS_GENERATORS.md`](generator-comprehension/COMPREHENSIONS_VS_GENERATORS.md)：推导式、生成器表达式和生成器函数的对比。
- [`generator-comprehension/comprehensions.py`](generator-comprehension/comprehensions.py)、[`generator-comprehension/generators.py`](generator-comprehension/generators.py)、[`generator.py`](generator.py)：运行示例，观察求值时机和一次性消费。
- [`decorators.py`](decorators.py)：普通装饰器、带参数装饰器和 `functools.wraps`。
- [`tuple_immutability_explanation.py`](tuple_immutability_explanation.py)、[`tuple_equality_explanation.py`](tuple_equality_explanation.py)：不可变容器、嵌套可变对象，以及 `==` 与 `is` 的区别。

检查点：把一个列表推导式改成生成器，并说明内存、可重复遍历和提前终止的变化。

## 单元 4：模块、错误与运行时

目标：知道 Python 文件何时执行、异常如何沿调用栈传播，以及异步和 GIL 分别解决什么问题。

- [`module_loading_tutorial.py`](module_loading_tutorial.py)：导入、模块缓存和 `__name__`。
- [`error_handling.py`](error_handling.py)：异常类型、捕获边界、清理和自定义异常。
- [`asyn.py`](asyn.py)：协程、事件循环和 `await` 的控制权交接。
- [`gil.py`](gil.py)：CPython GIL 对 CPU 密集型和 I/O 密集型任务的影响。

检查点：画出一次 `try/except/finally` 的控制流，并指出哪些工作适合协程、哪些工作需要多进程。

## 单元 5：数据边界与标准库

目标：把外部输入校验为明确的数据模型，再用标准库完成文件、文本、缓存、分组、JSON 和压缩任务。

1. [`pydantic/PYDANTIC_GUIDE.md`](pydantic/PYDANTIC_GUIDE.md)：`BaseModel`、字段约束、嵌套、序列化和配置。
2. [`pydantic/PYDANTIC_FILES.md`](pydantic/PYDANTIC_FILES.md)：基础示例与泛型示例的关系；再运行 `pydantic_examples.py` 和 `pydantic-generic.py`。
3. [`standard_library_tour.py`](standard_library_tour.py)：`pathlib`、`json`、`re`、`collections`、`functools`、`itertools` 的组合。
4. [`COMPRESSION.md`](COMPRESSION.md) / [`bz2_compression.py`](bz2_compression.py)：`gzip`、`bz2`、`lzma`、`zlib` 的选择与流式处理。
5. [`LINKED_LIST_INITIALIZATION.md`](LINKED_LIST_INITIALIZATION.md)：作为数据结构练习，放在基础对象模型之后阅读。
6. [`template-handle.py`](template-handle.py)：f-string、`string.Template` 和 Python 3.14+ t-string；运行前确认解释器版本。

检查点：为一个外部 JSON 响应建立 Pydantic 模型，校验失败时返回可定位的错误；再用生成器逐行处理输入。

## 如何运行示例

在仓库根目录执行：

```bash
python 03-python-basics/<文件路径>.py
```

部分示例依赖第三方包，请先查看文件顶部的 import；例如多分派和 Pydantic 示例需要安装对应依赖。示例目录中的 `__pycache__/` 是 Python 自动生成的缓存，不属于学习材料，可以忽略。

## 推荐学习方式

- 每次只学习一个问题：先预测输出，再运行代码，最后回到专题文档解释差异。
- 优先阅读执行路径和“为什么”，不要把 README 当作所有专题的重复正文。
- 遇到不确定行为，使用 `type()`、`repr()`、`inspect` 或最小化示例验证，而不是凭记忆猜测。

完成本目录后，应能解释：对象协议如何驱动语法糖、闭包如何保存状态、生成器如何暂停与恢复、模块如何缓存，以及外部数据为什么需要显式校验。
