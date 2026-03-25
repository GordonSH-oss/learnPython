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

## 内层函数对外层变量的访问规则

内层函数可以**读取**外层变量，也可以**改动外层变量指向的对象内容**，但不能对外层变量本身**重新赋值**——除非用 `nonlocal`。

用便利贴来比喻：`series` 是一张便利贴，上面写着"这里有一个列表"。

- `series.append(x)` — 你找到便利贴，去列表里加了一个元素。**便利贴本身没动**，不需要 `nonlocal`
- `series = []` — 你想把便利贴撕掉，贴一张新的。**这是在动便利贴本身**，需要 `nonlocal`
- `count += 1` — `count` 是 `int`，不可变，你只能撕掉旧便利贴，贴新的。**必须用 `nonlocal`**

**判断是否需要 `nonlocal` 的规则：只要你对外层变量写了赋值号 `=`，就需要 `nonlocal`。** 调用方法（`.append()`、`.update()` 等）不算赋值，不需要。

```python
def outer():
    series = []
    count = 0

    def inner(x):
        series.append(x)   # ✅ 修改列表内容，不需要 nonlocal
        # series = []      # ❌ 对变量重新赋值，需要 nonlocal

        nonlocal count
        count += 1         # count = count + 1，对变量重新赋值，必须 nonlocal

    return inner
```

### 为什么不加 `nonlocal` 会报错？

在内层函数里，**凡是写了赋值号 `=` 的变量**，Python 会自动认为它是**局部变量**。如果你同时又在赋值之前读取了它（例如 `count = count + 1` 里先读 `count`），就会报 `UnboundLocalError`——因为 Python 认为你在读一个还没定义的局部变量。

`nonlocal` 的作用就是告诉 Python："这个变量不是局部的，去外层找。"

## nonlocal：修改外层变量的示例

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
