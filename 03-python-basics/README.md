# Python 基础特性

学习 Python 语言的核心概念和基础特性。

## 核心概念

### 1. 面向对象编程（OOP）
- **文件**: 
  - `self_examples.py`, `SELF_EXPLANATION.md` - self 关键字详解
  - `decorators.py` - 装饰器完整教程（含带参数装饰器）
  - `polymorphism.py` - 多态详解（10 个案例）
  - `singledispatch.py`, `SINGLEDISPATCH.md` - 单分派泛化函数教程
  - `multiple_dispatch.py`, `MULTIPLEDISPATCH.md` - 多分派函数教程（第三方库）
  - `DUCK_TYPING.md` - 鸭子类型深度解析
  - `args_and_kwargs.py` - 函数参数详解（10 个案例）
- **内容**: 
  - self 在类中的作用
  - 装饰器与装饰器工厂
  - 多态的概念和实现
  - 函数层面的多态（`functools.singledispatch`）
  - 多参数类型组合分派（`multipledispatch`）
  - 方法重写（Override）
  - 抽象基类（ABC）
  - 鸭子类型（Duck Typing）详解
  - Protocol 协议
  - 设计模式应用
  - EAFP vs LBYL
  - `*args` 和 `**kwargs` 使用规则
  - `@wraps` 与元信息保留
  - 函数参数顺序规则
- **要点**: 实例引用、方法调用、继承、多态、接口、行为优先、可变参数

### 2. 闭包（Closure）
- **文件**: `closures.py`, `CLOSURES.md`
- **内容**: 闭包的原理、状态保持、nonlocal、与类的对比
- **要点**: 自由变量、工厂函数、状态隔离、轻量级状态管理

### 3. 数据类 (DataClass)
- **文件**: `data_class.py`
- **内容**: 使用 `@dataclass` 装饰器简化类定义
- **要点**: `field()`, `default_factory`, 避免可变默认值陷阱

### 4. 特殊方法（Magic Methods）
- **文件夹**: `special-methods/`
- **文件**:
  - `property_decorator.py` - @property 装饰器详解
  - `str_and_repr.py` - 对象字符串表示
  - `comparison_operators.py` - 比较运算符重载
  - `arithmetic_operators.py` - 算术运算符重载
  - `container_methods.py` - 容器类型实现
  - `README.md` - 完整指南
- **内容**: Python 魔法方法的完整示例集合（30+ 个实用案例）
- **要点**: 运算符重载、属性控制、迭代器、容器协议

### 5. 切片机制
- **文件**: `slice_explanation.py`
- **内容**: 深入理解 Python 的切片操作
- **要点**: `__getitem__` 魔法方法、slice 对象、切片语法

### 6. 推导式和生成器
- **文件**:
  - `comprehensions.py` - 推导式完整指南（8 个案例）
  - `generators.py` - 生成器详解（10 个案例）
  - `COMPREHENSIONS_VS_GENERATORS.md` - 详细对比文档
- **内容**:
  - 列表/字典/集合推导式
  - 生成器函数和生成器表达式
  - yield, yield from
  - 内存和性能对比
  - 使用场景和最佳实践
- **要点**: 延迟计算、内存优化、迭代器协议

### 7. 压缩（Compression）
- **文件**: `bz2_compression.py`, `COMPRESSION.md`
- **内容**: 对比 `gzip`、`bz2`、`lzma`、`zlib` 的压缩率、速度、文件格式和典型使用场景
- **要点**: bytes 压缩、压缩文件读写、流式压缩、压缩等级、标准库命名冲突

### 8. 元组 (Tuple)
- **文件**: 
  - `tuple_immutability_explanation.py` - 元组的不可变性
  - `tuple_equality_explanation.py` - 元组的相等性比较
- **内容**: 元组的特性和使用场景
- **要点**: 不可变性、哈希、解包

### 9. Pydantic 数据校验
- **文件**: 
  - `pydantic_examples.py` - Pydantic 实用案例集合（基础 ⭐⭐）
  - `pydantic-generic.py` - Pydantic 结合泛型的高级用法（进阶 ⭐⭐⭐⭐）
  - `PYDANTIC_GUIDE.md` - Pydantic 完整使用指南
  - `PYDANTIC_FILES.md` - 两个文件的对比和学习建议
- **内容**: 
  - **基础**: 数据校验、类型转换、自定义校验器、字段别名、序列化、嵌套模型、配置管理
  - **进阶**: 泛型与 Pydantic 结合、通用分页器、统一响应格式
- **要点**: BaseModel、Field、校验器、泛型、序列化

### 10. 链表初始化
- **文件**: `LINKED_LIST_INITIALIZATION.md`
- **内容**: 链表数据结构的初始化方法
- **要点**: 节点创建、指针操作

## 学习顺序建议

1. **self_examples.py** - 理解面向对象基础
2. **decorators.py** - 学习普通装饰器、带参数装饰器和 `@wraps`
3. **polymorphism.py** - 掌握多态概念和应用
4. **singledispatch.py** - 学习函数层面的多态和类型分派
5. **multiple_dispatch.py** - 学习多参数签名分派和第三方多分派库
6. **data_class.py** - 学习简化类定义的方法
7. **closures.py** - 理解闭包和函数式状态管理
8. **comprehensions.py** - 掌握推导式（列表/字典/集合）
9. **generators.py** - 理解生成器和延迟计算
10. **COMPREHENSIONS_VS_GENERATORS.md** - 学习何时使用哪个
11. **bz2_compression.py**, **COMPRESSION.md** - 学习标准库压缩模块
12. **special-methods/** - 学习 Python 特殊方法
   - 从 `property_decorator.py` 开始
   - 然后 `str_and_repr.py`
   - 最后 `comparison_operators.py` 和其他
13. **pydantic_examples.py** - 掌握数据校验和 Pydantic 基础
14. **pydantic-generic.py** - Pydantic 与泛型结合的高级用法
15. **slice_explanation.py** - 掌握切片和魔法方法
16. **tuple_immutability_explanation.py** - 理解不可变数据类型
17. **tuple_equality_explanation.py** - 深入元组比较
18. **LINKED_LIST_INITIALIZATION.md** - 数据结构基础

## 关键知识点

### self 的作用
```python
class MyClass:
    def __init__(self, value):
        self.value = value  # self 指向当前实例
    
    def method(self):
        return self.value   # 访问实例属性
```

### 闭包（Closure）

```python
def make_aver():
    series = []                        # 只初始化一次
    def aver(new_value):
        series.append(new_value)
        return sum(series) / len(series)
    return aver                        # 返回函数本身，不是调用结果

avger = make_aver()
print(avger(10))   # 10.0
print(avger(11))   # 10.5  — series 跨调用保持状态

# 修改不可变的外层变量需要 nonlocal
def make_counter():
    count = 0
    def counter():
        nonlocal count
        count += 1
        return count
    return counter
```

### 带参数的装饰器
```python
from functools import wraps
import time

def clock(format_str="耗时: {duration:.4f}s"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            print(format_str.format(func_name=func.__name__, duration=duration))
            return result
        return wrapper
    return decorator
```

核心要点：
- 带参数装饰器本质上是“外层工厂 + 中层 decorator + 内层 wrapper”
- 外层参数会通过闭包被 `wrapper` 捕获和使用
- 这类装饰器通常要配合 `@wraps(func)` 保留原函数元信息

### DataClass 最佳实践
```python
from dataclasses import dataclass, field

@dataclass
class Student:
    name: str
    scores: list = field(default_factory=list)  # ✅ 正确
    # scores: list = []  # ❌ 错误：可变默认值
```

### 切片的本质
```python
# deck[:3] 实际上是
deck.__getitem__(slice(None, 3, None))
```

### 元组的不可变性
```python
t = (1, [2, 3], 4)
# t[0] = 10  # ❌ 错误：不能修改元组元素
t[1].append(5)  # ✅ 可以：列表内容可变
```

### Pydantic 数据校验
```python
from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    name: str = Field(min_length=3, max_length=20)
    email: EmailStr
    age: int = Field(ge=18, le=120)

user = User(name="张三", email="zhangsan@example.com", age="25")
# 自动类型转换：age 从字符串 "25" 转换为 int 25
```

### 推导式 vs 生成器
```python
# 列表推导式 - 立即计算，占用内存
squares = [i ** 2 for i in range(1000000)]  # 创建完整列表

# 生成器表达式 - 延迟计算，节省内存
squares = (i ** 2 for i in range(1000000))  # 只在需要时计算

# 生成器函数 - 使用 yield
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b
```

### 多态（Polymorphism）
```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "汪汪汪！"

class Cat(Animal):
    def speak(self):
        return "喵喵喵！"

def animal_sound(animal: Animal):
    print(animal.speak())

animal_sound(Dog())  # 输出：汪汪汪！
animal_sound(Cat())  # 输出：喵喵喵！
```

### 单分派泛化函数（Single Dispatch Generic Function）
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

print(handle(10))      # 20
print(handle("hello")) # HELLO
```

核心要点：
- `singledispatch` 只根据第一个参数的类型分派
- 新增类型时只需要补注册函数，不需要回到原函数里继续堆 `if/elif`
- 它是“函数层面的多态”，适合替代不断膨胀的类型判断逻辑

### 多分派函数（Multiple Dispatch）
```python
from multipledispatch import dispatch

@dispatch(int, int)
def combine(left, right):
    return left + right

@dispatch(str, str)
def combine(left, right):
    return left + right

print(combine(1, 2))          # 3
print(combine("Py", "thon"))  # Python
```

核心要点：
- `multipledispatch` 根据完整参数签名分派，不只看第一个参数
- `(str, int)` 和 `(int, str)` 可以是完全不同的实现
- 它是第三方库，使用前需要先安装 `pip install multipledispatch`

## 实践建议

1. **运行示例代码** - 每个 `.py` 文件都可以直接运行
2. **修改参数** - 尝试修改代码中的参数观察变化
3. **阅读文档** - `.md` 文件提供详细说明
4. **调试练习** - 使用 Python 调试器单步执行

## 扩展阅读

- Python 官方文档: https://docs.python.org/3/
- Real Python 教程: https://realpython.com/
- Fluent Python (书籍)
