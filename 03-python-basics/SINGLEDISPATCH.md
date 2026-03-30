# Python `singledispatch` 单分派泛化函数

## 什么是单分派泛化函数？

`functools.singledispatch` 可以把一个普通函数变成**泛化函数（generic function）**：

- 函数名只有一个
- 实现可以有很多个
- Python 会根据**第一个参数的类型**，自动选择最合适的实现

它本质上是“函数层面的多态”。

如果你以前是这样写的：

```python
def handle(value):
    if isinstance(value, int):
        return value * 2
    if isinstance(value, str):
        return value.upper()
    if isinstance(value, list):
        return sum(value)
    raise TypeError("不支持的类型")
```

那么 `singledispatch` 就是把这些分支拆开，让每种类型的处理逻辑独立注册。

## 最基础的写法

```python
from functools import singledispatch


@singledispatch
def handle(value):
    raise TypeError(f"不支持类型: {type(value).__name__}")


@handle.register
def _(value: int):
    return value * 2


@handle.register
def _(value: str):
    return value.upper()


@handle.register(list)
def _(value):
    return sum(value)
```

调用时：

```python
print(handle(10))        # 20
print(handle("hello"))   # HELLO
print(handle([1, 2, 3])) # 6
```

这里有两个关键点：

1. `@singledispatch` 装饰的是“默认实现”
2. `@handle.register(...)` 用来给不同类型补充实现

## 它为什么叫“单分派”？

因为它只根据**一个参数**做分派，而且这个参数必须是**第一个参数**。

```python
from functools import singledispatch


@singledispatch
def combine(left, right):
    return "默认分支"


@combine.register
def _(left: list, right):
    return left + [right]


combine([1, 2], 3)       # 命中 list 分支
combine("x", [1, 2, 3])  # 不会命中 list 分支
```

第二个调用里，虽然 `right` 是 `list`，但没有用，因为 `singledispatch` 不看第二个参数。

## 注册方式

### 写法 1：用类型注解注册

```python
@handle.register
def _(value: int):
    return value * 2
```

这种写法最简洁。`register` 会从参数注解里推断类型。

### 写法 2：显式指定类型

```python
@handle.register(list)
def _(value):
    return sum(value)
```

这种写法适合：

- 你不想写类型注解
- 你想让代码更显式
- 你要注册抽象基类

## 默认实现的作用

默认实现相当于兜底逻辑。常见有两种风格。

### 风格 1：直接报错

```python
@singledispatch
def handle(value):
    raise TypeError(f"不支持类型: {type(value).__name__}")
```

适合“必须明确支持哪些类型”的场景。

### 风格 2：给一个通用处理

```python
@singledispatch
def stringify(value):
    return f"默认处理: {value!r}"
```

适合日志、展示、调试这类“任何对象都能先兜底处理”的场景。

## 继承关系会影响分派结果

`singledispatch` 不是简单地“精确匹配类型”，它会沿着继承链找最合适的实现。

```python
from functools import singledispatch


@singledispatch
def show(value):
    return "default"


@show.register
def _(value: int):
    return "int"


print(show(True))  # int
```

为什么？因为 `bool` 是 `int` 的子类：

```python
issubclass(bool, int)  # True
```

如果你再注册一个 `bool` 版本：

```python
@show.register
def _(value: bool):
    return "bool"
```

那么 `show(True)` 就会优先命中 `bool`。

## 可以为抽象基类注册

这点很实用。你不一定非要为 `list`、`dict`、`tuple` 分别注册，也可以直接为抽象基类注册。

```python
from collections.abc import Mapping, Sequence
from functools import singledispatch


@singledispatch
def summarize(value):
    return "default"


@summarize.register
def _(value: Mapping):
    return f"映射对象, key 数量: {len(value)}"


@summarize.register
def _(value: Sequence):
    return f"序列对象, 长度: {len(value)}"
```

这样：

- `dict` 会走 `Mapping`
- `tuple`、`list` 会走 `Sequence`

但也要注意，`str` 也是 `Sequence`。如果你不想让字符串走“普通序列逻辑”，应该单独再注册一个 `str`。

## 查看当前注册了什么

`singledispatch` 提供两个很有用的接口：

### `函数.dispatch(类型)`

返回某个类型最终会命中的实现函数。

```python
impl = handle.dispatch(int)
print(impl)
```

这个适合调试“某个类型到底会走哪个分支”。

### `函数.registry`

返回当前注册表。

```python
print(handle.registry)
```

它能帮助你确认：

- 哪些类型已经注册
- 默认实现是否仍然存在
- 某个分支是不是忘了注册

## 和 `if/elif isinstance(...)` 相比有什么优势？

### 1. 扩展更自然

新增类型时，只需要补一个注册函数，不需要回到原函数里继续堆分支。

```python
@handle.register
def _(value: tuple):
    return list(value)
```

### 2. 每种类型的逻辑更独立

每个处理函数只关心一种类型，代码更容易读。

### 3. 更接近“开放封闭原则”

对扩展开放，对修改关闭。尤其适合插件式扩展或类型分发逻辑。

## 常见误区

### 1. 以为它会检查所有参数

不会。它只看第一个参数。

### 2. 以为它只支持精确类型

不会。它会考虑继承关系和 MRO。

### 3. 以为注册 `Sequence` 后字符串不会进来

错。`str` 也是序列类型，通常需要单独处理。

### 4. 以为它能替代所有分支判断

也不行。如果你的逻辑是按“值”分支，而不是按“类型”分支，比如：

```python
def handle_status(code: int):
    if code < 400:
        ...
    elif code < 500:
        ...
```

这种场景就不适合 `singledispatch`。

## 什么时候适合使用？

适合：

- 输入类型明确不同，处理逻辑也明显不同
- 类型分支会持续增长
- 你想把分支逻辑拆散，避免一个大函数不断膨胀

不太适合：

- 只有一两个简单分支
- 分派依据不是第一个参数
- 分派依据是值、状态、配置，而不是类型

## 相关示例

可运行示例见：

- `03-python-basics/singledispatch.py`

建议学习顺序：

1. 先运行 `singledispatch.py`
2. 对照这个文档理解“默认实现、注册、继承链、ABC 注册”
3. 再回头看你自己的 `playground.py` 示例，会更容易理解它为什么这样工作

## 延伸

如果你后面想把这个思路用到类方法上，可以继续了解：

- `functools.singledispatchmethod`

它和 `singledispatch` 思路一致，但用于方法定义。
