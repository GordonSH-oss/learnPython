# Python `multipledispatch` 多分派函数

## 先说结论

- `singledispatch` 只根据**第一个参数**的类型分派
- `multipledispatch` 可以根据**多个参数的类型组合**分派
- `multipledispatch` 是**第三方库**，不是标准库

安装方式：

```bash
pip install multipledispatch
```

## 什么是多分派？

看一个普通的双参数函数：

```python
def combine(left, right):
    ...
```

如果你希望：

- `combine(int, int)` 做整数加法
- `combine(str, str)` 做字符串拼接
- `combine(list, list)` 做列表合并
- `combine(str, int)` 做字符串重复
- `combine(int, str)` 做数字加单位

那你就不是只靠“第一个参数类型”就能决定行为了。  
这时候，`singledispatch` 不够用，多分派才更合适。

## 最基础的写法

```python
from multipledispatch import dispatch


@dispatch(int, int)
def combine(left, right):
    return left + right


@dispatch(str, str)
def combine(left, right):
    return left + right


@dispatch(list, list)
def combine(left, right):
    return left + right
```

调用时：

```python
print(combine(1, 2))          # 3
print(combine("Py", "thon"))  # Python
print(combine([1], [2, 3]))   # [1, 2, 3]
```

这里和 `singledispatch` 最大的区别是：

- `@dispatch(int, int)` 注册的是**完整签名**
- 不是只看第一个参数
- 参数顺序也属于签名的一部分

## 参数顺序不同，就是不同实现

```python
from multipledispatch import dispatch


@dispatch(str, int)
def format_pair(left, right):
    return left * right


@dispatch(int, str)
def format_pair(left, right):
    return f"{left}{right}"
```

所以：

```python
format_pair("ha", 3)  # hahaha
format_pair(3, "kg")  # 3kg
```

这正是多分派的价值之一：  
`(str, int)` 和 `(int, str)` 虽然参数个数相同，但语义完全可以不同。

## 可以使用抽象类型

官方文档说明，`multipledispatch` 支持抽象类型，例如 `Number`、`Iterable` 这类基类。

```python
from numbers import Number
from multipledispatch import dispatch


@dispatch(Number, Number)
def multiply(left, right):
    return left * right
```

这样：

- `multiply(2, 3)` 可以命中
- `multiply(2.5, 4)` 也可以命中

这是因为 `int`、`float` 都满足 `Number` 的抽象层级。

## 可以写联合签名

官方文档还提到，你可以用元组表示多个可接受类型。

```python
@dispatch((list, tuple), Number)
def multiply(items, factor):
    return [item * factor for item in items]
```

这表示第一个参数既可以是 `list`，也可以是 `tuple`。

## 更具体的签名优先

多分派系统会尽量选择“更具体”的签名。

```python
from multipledispatch import dispatch


@dispatch(object, object)
def f(x, y):
    return "default"


@dispatch(object, float)
def f(x, y):
    return "right is float"


@dispatch(float, float)
def f(x, y):
    return "both float"
```

那么：

```python
f("x", 2.0)   # right is float
f(2.0, 3.0)   # both float
```

因为 `(float, float)` 比 `(object, float)` 更具体。

## 歧义问题

多分派比单分派更强大，但也更容易出现**歧义**。

比如你定义了：

```python
@dispatch(object, float)
def f(x, y):
    ...


@dispatch(float, object)
def f(x, y):
    ...
```

那 `f(2.0, 3.0)` 到底应该命中哪一个？

- 左边是 `float`，符合第二个
- 右边是 `float`，也符合第一个

这时两个签名都“很像正确答案”，就会产生歧义。

官方文档说明，这种情况下库会发出歧义警告，并建议你补一个更具体的实现：

```python
@dispatch(float, float)
def f(x, y):
    ...
```

这是一个很重要的实践原则：

- 当你发现两个签名都可能匹配同一组输入时
- 最好补上一个更具体的签名来消除歧义

## 和 `singledispatch` 的区别

| 维度 | `singledispatch` | `multipledispatch` |
|------|------------------|--------------------|
| 来源 | Python 标准库 `functools` | 第三方库 |
| 分派依据 | 只看第一个参数 | 看完整参数签名 |
| 适用场景 | 单参数类型分派 | 多参数类型组合分派 |
| 复杂度 | 更低 | 更高 |
| 依赖 | 无额外依赖 | 需要安装 |

## 什么时候适合用？

适合：

- 函数行为取决于多个参数的类型组合
- 你想把不同类型组合的逻辑拆成独立实现
- 你不想写一长串嵌套的 `if isinstance(...)`

不太适合：

- 你只是根据第一个参数分派
- 你只有很少的分支
- 你不希望引入第三方依赖

## 学习建议

建议先学：

1. `singledispatch`
2. 再看 `multipledispatch`

原因很简单：

- `singledispatch` 更接近标准库思路
- 概念更简单
- 理解“泛化函数 + 注册实现”之后，再理解多参数签名会容易很多

## 本仓库中的对应示例

- `03-python-basics/singledispatch.py`
- `03-python-basics/SINGLEDISPATCH.md`
- `03-python-basics/multiple_dispatch.py`

如果本地还没安装依赖，运行 `multiple_dispatch.py` 时会先提示安装命令，而不是直接抛出导入错误。
