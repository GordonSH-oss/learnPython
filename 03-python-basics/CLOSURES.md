# Python 闭包（Closure）详解

## 核心问题

先看一段代码：

```python
def make_aver():
    series = []
    def aver(new_value):
        series.append(new_value)
        return sum(series) / len(series)
    return aver   # 返回函数本身，不是调用结果
```

这里有两个容易混淆的写法：

| 写法 | 含义 |
|------|------|
| `return aver` | 把 `aver` **函数对象**作为返回值 |
| `return aver()` | **调用** `aver`，返回它的执行结果（一个数字） |

`make_aver()` 返回的是 `aver` 这个函数，因此：

```python
avger = make_aver()   # avger 就是 aver 函数
avger(10)             # 这才是真正调用它
```

## 为什么需要闭包？

**目的：让 `series` 只初始化一次，但在多次调用之间保持状态。**

对比几种方案：

```python
# ❌ 方案一：全局变量（污染命名空间，且无法创建多个独立实例）
series = []
def aver(new_value):
    series.append(new_value)
    return sum(series) / len(series)

# ❌ 方案二：每次调用都重置（记不住历史数据）
def aver(new_value):
    series = [new_value]
    return sum(series) / len(series)

# ✅ 方案三：闭包（series 藏在外层函数的局部作用域里）
def make_aver():
    series = []
    def aver(new_value):
        series.append(new_value)
        return sum(series) / len(series)
    return aver
```

## 闭包的工作原理

`aver` 函数被返回后，`make_aver` 的调用栈已经结束，但 `series` 并没有消失。Python 把它保存在 `aver` 的 `__closure__` 属性里：

```python
avger = make_aver()
avger(10)
avger(20)

print(avger.__code__.co_freevars)         # ('series',)  — 捕获的变量名
print(avger.__closure__[0].cell_contents) # [10, 20]     — 实际存储的值
```

这个被捕获并保存在内层函数中的外层变量，就叫做**自由变量（free variable）**。闭包 = 函数 + 它捕获的自由变量。

## 闭包的核心优势

### 状态隔离

每次调用 `make_aver()` 都会创建一个全新的 `series`，不同实例之间完全独立：

```python
avger1 = make_aver()
avger2 = make_aver()

avger1(10)   # avger1 的 series: [10]
avger2(5)    # avger2 的 series: [5]，互不影响

print(avger1(20))  # 15.0（基于 [10, 20]）
print(avger2(15))  # 10.0（基于 [5, 15]）
```

如果用全局变量，就无法做到这一点。

## nonlocal：修改不可变的外层变量

如果被捕获的变量是不可变类型（`int`、`str`、`tuple`），直接赋值会报错。必须用 `nonlocal` 声明：

```python
def make_counter():
    count = 0
    def counter():
        nonlocal count   # 声明 count 来自外层函数
        count += 1       # 如果不加 nonlocal，这里会报 UnboundLocalError
        return count
    return counter

c = make_counter()
print(c())   # 1
print(c())   # 2
print(c())   # 3
```

> **为什么列表不需要 `nonlocal`？**
>
> `series.append(new_value)` 是在修改列表的**内容**，变量 `series` 本身（即它指向的对象）没有变。而 `count += 1` 等价于 `count = count + 1`，是对变量本身重新赋值，所以需要 `nonlocal`。

## 闭包 vs 类（等价对比）

闭包本质上是一种轻量级的状态管理方式，与类完全等价：

| 概念 | 闭包 | 类 |
|------|------|----|
| 状态存储 | 外层函数的局部变量 | 实例属性（`self.xxx`） |
| 行为 | 内层函数 | 方法 |
| 实例化 | 调用外层函数 | `ClassName()` |

```python
# 闭包写法
def make_aver():
    series = []
    def aver(new_value):
        series.append(new_value)
        return sum(series) / len(series)
    return aver

# 等价的类写法
class Averager:
    def __init__(self):
        self._series = []

    def __call__(self, new_value):
        self._series.append(new_value)
        return sum(self._series) / len(self._series)
```

两种方式的输出完全一致：

```python
avger = make_aver()
avg_obj = Averager()

print(avger(10))    # 10.0
print(avg_obj(10))  # 10.0
```

**何时选闭包，何时选类？**

- **闭包**：逻辑简单、只有一个内部函数时，代码更简洁
- **类**：内部状态复杂、有多个方法，或需要继承时，类更清晰

## 总结

| 要点 | 说明 |
|------|------|
| **闭包的目的** | 让状态（自由变量）在多次调用之间保持，同时避免全局变量 |
| **`return 函数` vs `return 函数()`** | 前者返回函数对象，后者返回调用结果 |
| **自由变量** | 被内层函数捕获的外层变量，保存在 `__closure__` 中 |
| **`nonlocal`** | 修改不可变外层变量时必须声明 |
| **状态隔离** | 每次调用外层函数都创建独立的闭包实例 |
| **与类的关系** | 闭包是轻量级的单方法对象，完全可以用类替代 |
