# Python 高级面试题答案（易错/复杂）

## 易错陷阱题

### 1. 默认参数陷阱

**代码：**
```python
def append_to_list(element, lst=[]):
    lst.append(element)
    return lst

print(append_to_list(1))  # [1]
print(append_to_list(2))  # [1, 2]  ❌ 不是 [2]
print(append_to_list(3))  # [1, 2, 3]  ❌ 不是 [3]
```

**原因：**
- 默认参数在函数定义时只创建一次，而不是每次调用时创建
- 所有调用共享同一个列表对象

**正确写法：**
```python
def append_to_list(element, lst=None):
    if lst is None:
        lst = []
    lst.append(element)
    return lst

print(append_to_list(1))  # [1]
print(append_to_list(2))  # [2]
print(append_to_list(3))  # [3]
```

**核心原则：** 永远不要使用可变对象作为默认参数！

---

### 2. 引用与赋值

**代码：**
```python
x = [1, 2, 3]
y = x  # y 引用 x，指向同一个对象
y.append(4)
print(x)  # [1, 2, 3, 4]
```

**原因：**
- `y = x` 创建的是引用，不是副本
- `x` 和 `y` 指向同一个列表对象

**区分不同的拷贝方式：**
```python
x = [1, 2, 3]

# 引用（不是拷贝）
y = x
y.append(4)
print(x)  # [1, 2, 3, 4]

# 浅拷贝
x = [1, 2, 3]
z = x[:]  # 或 x.copy() 或 list(x)
z.append(4)
print(x)  # [1, 2, 3]

# 浅拷贝的局限
x = [[1, 2], [3, 4]]
z = x[:]
z[0].append(5)
print(x)  # [[1, 2, 5], [3, 4]]  内部列表仍是引用

# 深拷贝
import copy
x = [[1, 2], [3, 4]]
z = copy.deepcopy(x)
z[0].append(5)
print(x)  # [[1, 2], [3, 4]]
```

---

### 3. 闭包中的变量捕获

**代码：**
```python
funcs = []
for i in range(3):
    funcs.append(lambda: i)

for func in funcs:
    print(func())  # 2, 2, 2  ❌ 不是 0, 1, 2
```

**原因：**
- Lambda 函数捕获的是变量 `i` 的引用，不是值
- 循环结束后 `i = 2`，所有 lambda 都引用这个 `i`

**解决方案：**

```python
# 方案 1：使用默认参数
funcs = []
for i in range(3):
    funcs.append(lambda x=i: x)  # 默认参数在定义时求值

for func in funcs:
    print(func())  # 0, 1, 2

# 方案 2：使用闭包工厂
funcs = []
for i in range(3):
    def make_func(x):
        return lambda: x
    funcs.append(make_func(i))

for func in funcs:
    print(func())  # 0, 1, 2

# 方案 3：使用列表推导式
funcs = [lambda x=i: x for i in range(3)]
for func in funcs:
    print(func())  # 0, 1, 2
```

---

### 4. 赋值与拷贝的区别

**代码：**
```python
a = [1, 2, 3]
b = a        # 引用
c = a[:]     # 浅拷贝
d = a.copy() # 浅拷贝

a.append(4)
a[0] = 100

print(b)  # [100, 2, 3, 4]  引用同一对象
print(c)  # [1, 2, 3]      独立副本，不受影响
print(d)  # [1, 2, 3]      独立副本，不受影响
```

**内存示意：**
```
a, b --> [100, 2, 3, 4]  (同一对象)
c    --> [1, 2, 3]       (独立副本)
d    --> [1, 2, 3]       (独立副本)
```

---

### 5. 类变量与实例变量

**代码：**
```python
class MyClass:
    shared_list = []  # 类变量，所有实例共享
    
    def add(self, item):
        self.shared_list.append(item)

obj1 = MyClass()
obj2 = MyClass()
obj1.add(1)
obj2.add(2)
print(obj1.shared_list)  # [1, 2]
print(obj2.shared_list)  # [1, 2]  ❌ 两个实例共享同一个列表
```

**原因：**
- `shared_list` 是类变量，属于类本身
- 所有实例共享同一个类变量

**正确写法：**
```python
class MyClass:
    def __init__(self):
        self.instance_list = []  # 实例变量，每个实例独立
    
    def add(self, item):
        self.instance_list.append(item)

obj1 = MyClass()
obj2 = MyClass()
obj1.add(1)
obj2.add(2)
print(obj1.instance_list)  # [1]
print(obj2.instance_list)  # [2]
```

**理解类变量与实例变量的查找顺序：**
```python
class MyClass:
    class_var = "类变量"
    
    def __init__(self):
        self.instance_var = "实例变量"

obj = MyClass()
print(obj.instance_var)  # "实例变量"
print(obj.class_var)     # "类变量" (从类中查找)

# 实例赋值会遮蔽类变量
obj.class_var = "实例的类变量"
print(obj.class_var)     # "实例的类变量"
print(MyClass.class_var) # "类变量" (类本身不受影响)
```

---

## 复杂机制题

### 6. MRO（方法解析顺序）

**代码：**
```python
class A:
    def method(self):
        print("A")

class B(A):
    def method(self):
        print("B")

class C(A):
    def method(self):
        print("C")

class D(B, C):
    pass

d = D()
d.method()  # 输出: B
print(D.__mro__)
# (<class '__main__.D'>, <class '__main__.B'>, <class '__main__.C'>, 
#  <class '__main__.A'>, <class 'object'>)
```

**原因：**
- Python 使用 C3 线性化算法确定 MRO
- 规则：深度优先 + 从左到右 + 保持单调性
- D 的 MRO: D → B → C → A → object

**C3 算法原理：**
1. 子类优先于父类
2. 如果有多个父类，按照声明顺序查找
3. 保持每个类的局部优先顺序

**复杂示例（菱形继承）：**
```python
class A:
    def method(self):
        print("A")

class B(A):
    def method(self):
        super().method()
        print("B")

class C(A):
    def method(self):
        super().method()
        print("C")

class D(B, C):
    def method(self):
        super().method()
        print("D")

d = D()
d.method()
# 输出:
# A
# C
# B
# D

print(D.__mro__)
# D → B → C → A → object
```

**super() 的工作原理：**
- `super()` 按照 MRO 顺序调用下一个类的方法
- 不是调用父类，而是 MRO 中的下一个类

---

### 7. 描述符（Descriptor）

**答案：**
描述符是实现了描述符协议的对象，用于自定义属性访问行为。

**描述符协议：**
- `__get__(self, instance, owner)` - 获取属性
- `__set__(self, instance, value)` - 设置属性
- `__delete__(self, instance)` - 删除属性

**实现验证描述符：**
```python
class ValidatedAttribute:
    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value
        self.name = None
    
    def __set_name__(self, owner, name):
        """Python 3.6+ 自动获取属性名"""
        self.name = name
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)
    
    def __set__(self, instance, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"{self.name} 必须是数字")
        
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"{self.name} 不能小于 {self.min_value}")
        
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"{self.name} 不能大于 {self.max_value}")
        
        instance.__dict__[self.name] = value

class Person:
    age = ValidatedAttribute(min_value=0, max_value=150)
    height = ValidatedAttribute(min_value=0)
    
    def __init__(self, age, height):
        self.age = age
        self.height = height

# 使用
p = Person(25, 175)
print(p.age)  # 25

try:
    p.age = -5  # ValueError: age 不能小于 0
except ValueError as e:
    print(e)

try:
    p.age = "abc"  # TypeError: age 必须是数字
except TypeError as e:
    print(e)
```

**常见的内置描述符：**
- `@property` - 属性访问
- `@staticmethod` - 静态方法
- `@classmethod` - 类方法

---

### 8. 装饰器丢失元数据

**问题代码：**
```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before")
        result = func(*args, **kwargs)
        print("After")
        return result
    return wrapper

@my_decorator
def greet(name):
    """Greet someone"""
    return f"Hello, {name}"

print(greet.__name__)  # wrapper  ❌ 应该是 greet
print(greet.__doc__)   # None     ❌ 应该是 "Greet someone"
```

**原因：**
- 装饰器返回的是 `wrapper` 函数
- 原函数的 `__name__`、`__doc__` 等元数据丢失

**解决方案：**
```python
from functools import wraps

def my_decorator(func):
    @wraps(func)  # 保留原函数元数据
    def wrapper(*args, **kwargs):
        print("Before")
        result = func(*args, **kwargs)
        print("After")
        return result
    return wrapper

@my_decorator
def greet(name):
    """Greet someone"""
    return f"Hello, {name}"

print(greet.__name__)  # greet
print(greet.__doc__)   # Greet someone
print(greet.__wrapped__)  # 可以访问原始函数
```

---

### 9. 生成器中的 return

**代码：**
```python
def generator():
    yield 1
    return 2  # 生成器可以 return，但不会像 yield 那样产生值
    yield 3   # 永远不会执行

g = generator()
print(next(g))  # 1
try:
    print(next(g))  # StopIteration: 2
except StopIteration as e:
    print(f"StopIteration: {e.value}")  # 2
```

**关键点：**
- 生成器中的 `return` 会触发 `StopIteration` 异常
- 返回值存储在异常的 `value` 属性中
- `return` 后的代码不会执行

**实际应用（yield from）：**
```python
def generator():
    yield 1
    return 2

def caller():
    result = yield from generator()
    print(f"Generator returned: {result}")  # 2
    yield result

for value in caller():
    print(value)
# 输出:
# 1
# Generator returned: 2
# 2
```

---

### 10. try-finally 中的 return

**代码：**
```python
def func():
    try:
        return 1
    finally:
        return 2

print(func())  # 2  ❌ finally 中的 return 覆盖了 try 中的 return
```

**原因：**
- `finally` 块总是会执行
- `finally` 中的 `return` 会覆盖 `try` 中的 `return`

**更复杂的情况：**
```python
def func1():
    try:
        return 1
    finally:
        print("Finally executed")
    return 2  # 永远不会执行

print(func1())  # 1, 并打印 "Finally executed"

def func2():
    x = 1
    try:
        return x
    finally:
        x = 2  # 不影响返回值，因为 return 已经确定了返回值

print(func2())  # 1

def func3():
    x = [1]
    try:
        return x
    finally:
        x.append(2)  # 影响返回值，因为返回的是引用

print(func3())  # [1, 2]
```

**最佳实践：**
- 避免在 `finally` 中使用 `return`
- `finally` 应该只用于清理资源

---

### 11. 单例模式元类

**代码：**
```python
class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class MyClass(metaclass=SingletonMeta):
    def __init__(self, value):
        self.value = value

obj1 = MyClass(1)
obj2 = MyClass(2)
print(obj1 is obj2)  # True
print(obj1.value)    # 1  (第二次调用不会重新初始化)
```

**工作原理：**
1. 元类控制类的实例化过程
2. `__call__` 在调用 `MyClass()` 时被触发
3. 第一次创建实例并缓存
4. 后续调用返回缓存的实例

**线程安全的单例：**
```python
import threading

class ThreadSafeSingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:  # 双重检查
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
```

**其他单例实现方式：**
```python
# 装饰器方式
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class MyClass:
    pass

# __new__ 方式
class Singleton:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

---

### 12. is 与 == 的区别

**代码：**
```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(a == b)  # True  (值相等)
print(a is b)  # False (不是同一对象)
print(a is c)  # True  (同一对象)

# 小整数缓存（-5 到 256）
x = 256
y = 256
print(x is y)  # True  (Python 缓存了小整数)

m = 257
n = 257
print(m is n)  # False (交互式环境) / True (脚本中，编译器优化)

# 字符串驻留
s1 = "hello"
s2 = "hello"
print(s1 is s2)  # True (字符串驻留)

s3 = "hello world"
s4 = "hello world"
print(s3 is s4)  # False (包含空格，不驻留)

# 显式驻留
import sys
s5 = sys.intern("hello world")
s6 = sys.intern("hello world")
print(s5 is s6)  # True
```

**核心区别：**
- `==` 比较值是否相等（调用 `__eq__`）
- `is` 比较对象身份（内存地址）

**Python 的对象缓存机制：**
1. **小整数缓存**：-5 到 256
2. **字符串驻留**：简单字符串（无空格、特殊字符）
3. **单例对象**：`None`、`True`、`False`

**何时使用 is：**
```python
# 检查 None（推荐）
if value is None:
    pass

# 检查单例
if flag is True:  # 不推荐，应该用 if flag:
    pass

# 检查对象身份
if obj1 is obj2:
    pass
```

---

### 13. 协程中缺少 await

**问题代码：**
```python
import asyncio

async def task1():
    print("Task 1 start")
    await asyncio.sleep(2)
    print("Task 1 end")
    return "Result 1"

async def task2():
    print("Task 2 start")
    result = task1()  # ❌ 缺少 await
    print(f"Result type: {type(result)}")  # <class 'coroutine'>
    print("Task 2 end")
    return result

asyncio.run(task2())
# 输出:
# Task 2 start
# Result type: <class 'coroutine'>
# Task 2 end
# 警告: RuntimeWarning: coroutine 'task1' was never awaited
```

**问题：**
- 不使用 `await`，协程不会执行
- 返回的是协程对象，不是结果

**正确写法：**
```python
async def task2():
    print("Task 2 start")
    result = await task1()  # ✅ 使用 await
    print("Task 2 end")
    return result

asyncio.run(task2())
# 输出:
# Task 2 start
# Task 1 start
# (等待 2 秒)
# Task 1 end
# Task 2 end
```

**并发执行多个协程：**
```python
async def main():
    # 方式 1: asyncio.gather
    results = await asyncio.gather(task1(), task1(), task1())
    
    # 方式 2: asyncio.create_task
    t1 = asyncio.create_task(task1())
    t2 = asyncio.create_task(task1())
    result1 = await t1
    result2 = await t2
    
    # 方式 3: asyncio.wait
    tasks = [task1(), task1()]
    done, pending = await asyncio.wait(tasks)
```

---

### 14. 变量作用域与 global/nonlocal

**代码：**
```python
x = 10

def outer():
    x = 20
    def inner():
        x = 30
        print("inner:", x)  # 30
    inner()
    print("outer:", x)  # 20

outer()
print("global:", x)  # 10

# 使用 global
def outer2():
    x = 20
    def inner2():
        global x  # 引用全局变量
        x = 30
    inner2()
    print("outer2:", x)  # 20 (局部变量未改变)

x = 10
outer2()
print("global after outer2:", x)  # 30 (全局变量被修改)

# 使用 nonlocal
def outer3():
    x = 20
    def inner3():
        nonlocal x  # 引用外层函数的变量
        x = 30
    inner3()
    print("outer3:", x)  # 30 (外层变量被修改)

outer3()
print("global:", x)  # 30 (全局变量不受影响，仍是上次的值)
```

**作用域查找顺序（LEGB）：**
1. **L (Local)**：局部作用域
2. **E (Enclosing)**：嵌套函数的外层作用域
3. **G (Global)**：全局作用域
4. **B (Built-in)**：内置作用域

**常见陷阱：**
```python
x = 10

def func():
    print(x)  # UnboundLocalError
    x = 20

# 原因：Python 看到 x = 20，认为 x 是局部变量
# 在赋值前访问局部变量导致错误

# 正确写法
def func():
    global x
    print(x)  # 10
    x = 20
```

---

### 15. 深拷贝与循环引用

**代码：**
```python
import copy

class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

# 创建循环引用
a = Node(1)
b = Node(2)
a.next = b
b.next = a

# 深拷贝可以正确处理循环引用
c = copy.deepcopy(a)
print(c.value)  # 1
print(c.next.value)  # 2
print(c.next.next.value)  # 1
print(c is a)  # False
print(c.next is b)  # False
```

**deepcopy 的魔法：**
- `deepcopy` 使用 memo 字典跟踪已拷贝对象
- 遇到已拷贝对象直接返回引用，避免无限递归

**自定义深拷贝行为：**
```python
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None
    
    def __deepcopy__(self, memo):
        # 自定义深拷贝逻辑
        if id(self) in memo:
            return memo[id(self)]
        
        new_node = Node(copy.deepcopy(self.value, memo))
        memo[id(self)] = new_node  # 记录已拷贝
        new_node.next = copy.deepcopy(self.next, memo)
        return new_node
```

**浅拷贝 vs 深拷贝：**
```python
import copy

# 嵌套结构
original = {'a': [1, 2, 3], 'b': {'x': 10}}

# 浅拷贝
shallow = copy.copy(original)
shallow['a'].append(4)
print(original['a'])  # [1, 2, 3, 4]  内部列表被修改

# 深拷贝
deep = copy.deepcopy(original)
deep['a'].append(5)
print(original['a'])  # [1, 2, 3, 4]  不受影响
```

---

### 16. 装饰器链的执行顺序

**代码：**
```python
def decorator1(func):
    print("Decorator 1 called")
    def wrapper():
        print("Wrapper 1 before")
        func()
        print("Wrapper 1 after")
    return wrapper

def decorator2(func):
    print("Decorator 2 called")
    def wrapper():
        print("Wrapper 2 before")
        func()
        print("Wrapper 2 after")
    return wrapper

@decorator1
@decorator2
def my_function():
    print("Function called")

# 定义时输出:
# Decorator 2 called
# Decorator 1 called

my_function()
# 调用时输出:
# Wrapper 1 before
# Wrapper 2 before
# Function called
# Wrapper 2 after
# Wrapper 1 after
```

**执行顺序：**
1. **定义时（由下往上）**：先 `decorator2`，后 `decorator1`
2. **调用时（由上往下）**：先 `wrapper1`，再 `wrapper2`，最后原函数

**等价写法：**
```python
def my_function():
    print("Function called")

my_function = decorator1(decorator2(my_function))
```

**理解流程：**
```
定义时:
my_function -> decorator2(my_function) -> wrapper2
           -> decorator1(wrapper2) -> wrapper1

调用时:
wrapper1() -> wrapper2() -> my_function()
```

---

### 17. dict.fromkeys 陷阱

**代码：**
```python
keys = ['a', 'b', 'c']

# 列表推导式：每个 key 有独立的列表
d1 = {key: [] for key in keys}
d1['a'].append(1)
print(d1)  # {'a': [1], 'b': [], 'c': []}

# dict.fromkeys：所有 key 共享同一个列表
d2 = dict.fromkeys(keys, [])
d2['a'].append(1)
print(d2)  # {'a': [1], 'b': [1], 'c': [1]}  ❌ 所有 key 都被修改
```

**原因：**
- `dict.fromkeys(keys, value)` 中的 `value` 只创建一次
- 所有 key 引用同一个对象

**正确写法：**
```python
# 方式 1：使用字典推导式
d = {key: [] for key in keys}

# 方式 2：使用 defaultdict
from collections import defaultdict
d = defaultdict(list)

# 方式 3：不可变默认值可以使用 fromkeys
d = dict.fromkeys(keys, 0)  # 数字是不可变的，安全
```

---

### 18. 上下文管理器的异常处理

**代码：**
```python
class MyContext:
    def __enter__(self):
        print("Enter")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Exit: {exc_type}")
        return True  # 返回 True 抑制异常

with MyContext():
    print("Inside")
    raise ValueError("Error")
print("After with")  # 会执行

# 输出:
# Enter
# Inside
# Exit: <class 'ValueError'>
# After with
```

**`__exit__` 返回值的意义：**
- `return True` 或 `return 1`：抑制异常，继续执行
- `return False` 或 `return None`：传播异常

**实际应用场景：**
```python
class IgnoreException:
    def __init__(self, *exceptions):
        self.exceptions = exceptions
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return False
        return issubclass(exc_type, self.exceptions)

# 使用
with IgnoreException(ValueError, TypeError):
    int("abc")  # 异常被抑制
print("继续执行")

# 数据库事务示例
class Transaction:
    def __enter__(self):
        self.conn.begin()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        return False  # 传播异常
```

---

### 19. 多线程的竞态条件

**问题代码：**
```python
import threading

counter = 0

def increment():
    global counter
    for _ in range(100000):
        counter += 1  # 不是原子操作

threads = [threading.Thread(target=increment) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(counter)  # 期望 1000000，实际可能是 300000-900000
```

**原因：**
- `counter += 1` 实际是三步操作：
  1. 读取 counter
  2. 计算 counter + 1
  3. 写回 counter
- 多线程并发执行时会相互覆盖

**解决方案：**

```python
import threading

# 方式 1：使用 Lock
lock = threading.Lock()
counter = 0

def increment_with_lock():
    global counter
    for _ in range(100000):
        with lock:
            counter += 1

# 方式 2：使用 RLock（可重入锁）
rlock = threading.RLock()

# 方式 3：使用原子操作（threading.local 或 queue）
from queue import Queue

# 方式 4：使用线程安全的数据结构
import queue
q = queue.Queue()

# 方式 5：避免共享状态，使用局部累加
def increment_local():
    local_sum = 0
    for _ in range(100000):
        local_sum += 1
    return local_sum

threads = [threading.Thread(target=increment_local) for _ in range(10)]
results = []
# ... 收集结果
```

---

### 20. __new__ 与 __init__ 的区别

**代码：**
```python
class MyClass:
    def __new__(cls, *args, **kwargs):
        print("__new__ called")
        print(f"  cls: {cls}")
        instance = super().__new__(cls)
        print(f"  instance created: {instance}")
        return instance
    
    def __init__(self, value):
        print("__init__ called")
        print(f"  self: {self}")
        self.value = value

obj = MyClass(42)
# 输出:
# __new__ called
#   cls: <class '__main__.MyClass'>
#   instance created: <__main__.MyClass object at 0x...>
# __init__ called
#   self: <__main__.MyClass object at 0x...>
```

**核心区别：**
| 特性 | `__new__` | `__init__` |
|------|-----------|-----------|
| 调用时机 | 实例创建前 | 实例创建后 |
| 参数 | 接收类 (`cls`) | 接收实例 (`self`) |
| 返回值 | 必须返回实例 | 不返回值 (`None`) |
| 用途 | 控制实例创建 | 初始化实例属性 |

**实际应用场景：**

1. **实现单例模式：**
```python
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        print("Init called")

s1 = Singleton()  # Init called
s2 = Singleton()  # Init called (注意：每次都会调用 __init__)
print(s1 is s2)   # True
```

2. **不可变类型的子类化：**
```python
class PositiveInt(int):
    def __new__(cls, value):
        if value < 0:
            raise ValueError("必须是正数")
        return super().__new__(cls, value)

# int、str、tuple 等不可变类型必须在 __new__ 中设置值
p = PositiveInt(10)
print(p)  # 10
```

3. **工厂模式：**
```python
class Animal:
    def __new__(cls, animal_type):
        if animal_type == "dog":
            return Dog()
        elif animal_type == "cat":
            return Cat()
        else:
            return super().__new__(cls)

class Dog:
    pass

class Cat:
    pass

animal = Animal("dog")
print(type(animal))  # <class '__main__.Dog'>
```

**__new__ 不返回实例的情况：**
```python
class MyClass:
    def __new__(cls):
        return None  # 返回 None
    
    def __init__(self):
        print("Init")  # 不会被调用

obj = MyClass()
print(obj)  # None
```

---

## 额外的复杂题目

### 21. 元类（Metaclass）深入

**什么是元类？**
- 元类是类的类
- 类是元类的实例
- `type` 是 Python 中默认的元类

```python
# 一切皆对象
class MyClass:
    pass

print(type(MyClass))  # <class 'type'>
print(type(type))     # <class 'type'>

# 动态创建类
MyDynamicClass = type('MyDynamicClass', (), {'x': 10})
obj = MyDynamicClass()
print(obj.x)  # 10
```

**自定义元类：**
```python
class Meta(type):
    def __new__(mcs, name, bases, attrs):
        print(f"创建类: {name}")
        # 自动添加方法
        attrs['auto_method'] = lambda self: f"{name} instance"
        return super().__new__(mcs, name, bases, attrs)
    
    def __init__(cls, name, bases, attrs):
        print(f"初始化类: {name}")
        super().__init__(name, bases, attrs)
    
    def __call__(cls, *args, **kwargs):
        print(f"实例化: {cls.__name__}")
        return super().__call__(*args, **kwargs)

class MyClass(metaclass=Meta):
    pass

# 输出:
# 创建类: MyClass
# 初始化类: MyClass

obj = MyClass()
# 输出:
# 实例化: MyClass

print(obj.auto_method())  # MyClass instance
```

**实际应用：ORM 框架：**
```python
class ModelMeta(type):
    def __new__(mcs, name, bases, attrs):
        if name == 'Model':
            return super().__new__(mcs, name, bases, attrs)
        
        # 收集字段
        fields = {}
        for key, value in attrs.items():
            if isinstance(value, Field):
                fields[key] = value
        
        attrs['_fields'] = fields
        return super().__new__(mcs, name, bases, attrs)

class Field:
    def __init__(self, field_type):
        self.field_type = field_type

class Model(metaclass=ModelMeta):
    pass

class User(Model):
    name = Field(str)
    age = Field(int)

print(User._fields)  # {'name': <Field...>, 'age': <Field...>}
```

---

### 22. 内存管理与垃圾回收

**引用计数：**
```python
import sys

a = []
print(sys.getrefcount(a))  # 2 (a 本身 + getrefcount 的参数)

b = a
print(sys.getrefcount(a))  # 3

del b
print(sys.getrefcount(a))  # 2
```

**循环引用与垃圾回收：**
```python
import gc

class Node:
    def __init__(self, value):
        self.value = value
        self.next = None
    
    def __del__(self):
        print(f"Deleting {self.value}")

# 循环引用
a = Node(1)
b = Node(2)
a.next = b
b.next = a

del a
del b
# __del__ 不会立即调用，因为循环引用

gc.collect()  # 手动触发垃圾回收
# 输出:
# Deleting 1
# Deleting 2
```

**弱引用：**
```python
import weakref

class MyClass:
    pass

obj = MyClass()
weak_ref = weakref.ref(obj)

print(weak_ref())  # <__main__.MyClass object>
del obj
print(weak_ref())  # None
```

---

### 23. 猴子补丁（Monkey Patching）

```python
# 动态修改类或模块
class MyClass:
    def method(self):
        return "Original"

obj = MyClass()
print(obj.method())  # Original

# 运行时修改方法
MyClass.method = lambda self: "Patched"
print(obj.method())  # Patched

# 修改实例方法
def new_method(self):
    return "Instance patched"

obj.method = lambda: "Instance patched"
print(obj.method())  # Instance patched
```

---

### 24. 协议（Protocol）与鸭子类型

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None:
        ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

class Square:
    def draw(self) -> None:
        print("Drawing square")

def render(shape: Drawable) -> None:
    shape.draw()

render(Circle())  # OK
render(Square())  # OK
# 不需要显式继承 Drawable
```

---

## 总结

这些高级题目涵盖了 Python 的核心陷阱和复杂机制：

**易错陷阱：**
1. 可变默认参数
2. 引用与拷贝
3. 闭包变量捕获
4. 类变量与实例变量
5. dict.fromkeys 共享值

**复杂机制：**
1. MRO 与多重继承
2. 描述符协议
3. 元类编程
4. 上下文管理器
5. 生成器与协程
6. 线程安全与 GIL
7. 内存管理与垃圾回收

**面试建议：**
- 理解 Python 的对象模型
- 熟悉内存管理机制
- 掌握并发编程的陷阱
- 实践常见的设计模式
- 关注 Python 的性能优化

---

## 数据结构与算法

### 21. 实现一个 LRU 缓存

**答案：**

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        # 移到末尾表示最近使用
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            # 删除最久未使用的（第一个）
            self.cache.popitem(last=False)

# 使用示例
cache = LRUCache(2)
cache.put(1, 1)
cache.put(2, 2)
print(cache.get(1))  # 1
cache.put(3, 3)      # 删除 key 2
print(cache.get(2))  # -1

# 使用双向链表实现（更底层）
class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache2:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> Node
        # 虚拟头尾节点
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
    
    def _add_to_head(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_to_head(node)
        return node.value
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self._remove(self.cache[key])
        node = Node(key, value)
        self._add_to_head(node)
        self.cache[key] = node
        
        if len(self.cache) > self.capacity:
            # 删除尾部节点
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]
```

---

### 22. 如何检测链表中是否有环？

**答案：**

```python
class ListNode:
    def __init__(self, val=0):
        self.val = val
        self.next = None

# 方法 1：快慢指针（Floyd 判圈算法）
def has_cycle(head: ListNode) -> bool:
    if not head or not head.next:
        return False
    
    slow = head
    fast = head.next
    
    while slow != fast:
        if not fast or not fast.next:
            return False
        slow = slow.next
        fast = fast.next.next
    
    return True

# 方法 2：使用集合
def has_cycle_set(head: ListNode) -> bool:
    seen = set()
    while head:
        if head in seen:
            return True
        seen.add(head)
        head = head.next
    return False

# 找到环的入口节点
def detect_cycle(head: ListNode) -> ListNode:
    slow = fast = head
    
    # 检测是否有环
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            break
    else:
        return None
    
    # 找入口：一个指针从头开始，一个从相遇点开始
    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next
    
    return slow
```

---

### 23. 实现一个线程安全的单例模式

**答案：**

```python
import threading

# 方法 1：双重检查锁
class Singleton:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

# 方法 2：使用元类
class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class MySingleton(metaclass=SingletonMeta):
    pass

# 方法 3：使用装饰器
def singleton(cls):
    instances = {}
    lock = threading.Lock()
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@singleton
class MyClass:
    pass

# 方法 4：使用模块（Python 模块天然是单例）
# my_singleton.py
class Singleton:
    pass

instance = Singleton()

# 其他文件导入
# from my_singleton import instance
```

---

### 24. 解释以下代码的时间复杂度

**代码：**
```python
def func(n):
    for i in range(n):
        for j in range(i):
            print(i, j)
```

**答案：**
- **时间复杂度：O(n²)**
- 外层循环：n 次
- 内层循环：0 + 1 + 2 + ... + (n-1) = n(n-1)/2 次
- 总次数：约 n²/2，忽略常数为 O(n²)

**其他复杂度示例：**
```python
# O(n)
for i in range(n):
    print(i)

# O(n²)
for i in range(n):
    for j in range(n):
        print(i, j)

# O(log n) - 二分查找
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# O(n log n) - 归并排序
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

# O(2^n) - 递归斐波那契
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)
```

---

### 25. 如何反转字典的键和值？处理值重复的情况

**答案：**

```python
# 简单反转（值唯一）
d = {'a': 1, 'b': 2, 'c': 3}
reversed_d = {v: k for k, v in d.items()}
print(reversed_d)  # {1: 'a', 2: 'b', 3: 'c'}

# 处理值重复（值到键列表）
d = {'a': 1, 'b': 2, 'c': 1, 'd': 3}

# 方法 1：使用 defaultdict
from collections import defaultdict

reversed_d = defaultdict(list)
for k, v in d.items():
    reversed_d[v].append(k)
print(dict(reversed_d))  # {1: ['a', 'c'], 2: ['b'], 3: ['d']}

# 方法 2：使用 setdefault
reversed_d = {}
for k, v in d.items():
    reversed_d.setdefault(v, []).append(k)

# 方法 3：保留最后出现的键
reversed_d = {v: k for k, v in d.items()}
# 值重复时，后面的键会覆盖前面的

# 方法 4：保留第一个出现的键
reversed_d = {}
for k, v in d.items():
    if v not in reversed_d:
        reversed_d[v] = k
```

---

## 函数式编程

### 26. 解释 map、filter、reduce 的区别和使用场景

**答案：**

```python
from functools import reduce

# map：对每个元素应用函数
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))
print(squared)  # [1, 4, 9, 16, 25]

# filter：过滤满足条件的元素
even = list(filter(lambda x: x % 2 == 0, numbers))
print(even)  # [2, 4]

# reduce：累积运算
sum_all = reduce(lambda x, y: x + y, numbers)
print(sum_all)  # 15

# 实际应用示例
# 计算多个数的乘积
product = reduce(lambda x, y: x * y, numbers)
print(product)  # 120

# 找最大值
max_value = reduce(lambda x, y: x if x > y else y, numbers)
print(max_value)  # 5

# 组合使用
result = reduce(
    lambda x, y: x + y,
    map(lambda x: x**2, filter(lambda x: x % 2 == 0, numbers))
)
print(result)  # 20 (2² + 4² = 4 + 16)

# 等价的列表推导式（更 Pythonic）
result = sum(x**2 for x in numbers if x % 2 == 0)
```

**使用场景：**
- `map`：转换集合中的每个元素
- `filter`：筛选集合中的元素
- `reduce`：聚合操作（求和、求积、找最值）

**注意：** 在 Python 中，列表推导式通常比 `map`/`filter` 更 Pythonic。

---

### 27. 什么是柯里化（Currying）？实现一个柯里化函数

**答案：**
柯里化是将接受多个参数的函数转换为一系列接受单个参数的函数。

```python
# 普通函数
def add(x, y, z):
    return x + y + z

print(add(1, 2, 3))  # 6

# 柯里化版本
def curried_add(x):
    def inner(y):
        def innermost(z):
            return x + y + z
        return innermost
    return inner

print(curried_add(1)(2)(3))  # 6

# 通用柯里化装饰器
def curry(func):
    def curried(*args, **kwargs):
        if len(args) + len(kwargs) >= func.__code__.co_argcount:
            return func(*args, **kwargs)
        return lambda *more_args, **more_kwargs: curried(
            *(args + more_args), **{**kwargs, **more_kwargs}
        )
    return curried

@curry
def add(x, y, z):
    return x + y + z

print(add(1)(2)(3))  # 6
print(add(1, 2)(3))  # 6
print(add(1)(2, 3))  # 6
print(add(1, 2, 3))  # 6

# 实际应用：配置函数
@curry
def log(level, message, timestamp):
    return f"[{timestamp}] {level}: {message}"

# 预配置日志函数
error_log = log("ERROR")
info_log = log("INFO")

print(error_log("Database connection failed", "2024-01-01 10:00:00"))
print(info_log("Server started", "2024-01-01 10:00:01"))
```

---

### 28. 解释 functools.partial 的输出

**代码：**
```python
from functools import partial

def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
print(square(5))          # 25
print(square(base=3))     # 9
```

**答案：**
- `partial` 固定函数的部分参数
- `square(5)` 等价于 `power(5, exponent=2)`
- `square(base=3)` 等价于 `power(base=3, exponent=2)`

**更多示例：**
```python
from functools import partial
import logging

# 固定日志级别
debug = partial(logging.log, logging.DEBUG)
info = partial(logging.log, logging.INFO)

debug("This is a debug message")
info("This is an info message")

# 固定函数的左侧参数
def divide(x, y):
    return x / y

half = partial(divide, y=2)
print(half(10))  # 5.0

# 多次使用 partial
power_of_2 = partial(power, exponent=2)
power_of_3 = partial(power, exponent=3)

print(power_of_2(5))  # 25
print(power_of_3(5))  # 125
```

---

### 29. 什么是纯函数？列举 Python 中的纯函数

**答案：**
纯函数满足两个条件：
1. 相同输入总是产生相同输出
2. 没有副作用（不修改外部状态）

```python
# 纯函数
def add(x, y):
    return x + y

def square(x):
    return x * x

# 不是纯函数（有副作用）
count = 0
def increment():
    global count
    count += 1
    return count

# 不是纯函数（依赖外部状态）
import random
def get_random():
    return random.random()

# Python 内置的纯函数
abs(-5)
len([1, 2, 3])
sum([1, 2, 3])
max(1, 2, 3)
min(1, 2, 3)
sorted([3, 1, 2])

# 注意：list.sort() 不是纯函数（就地修改）
lst = [3, 1, 2]
lst.sort()  # 修改了 lst
```

**纯函数的优势：**
- 易于测试
- 易于并行化
- 易于缓存（memoization）
- 易于推理

---

### 30. 实现一个函数组合（compose）工具

**答案：**

```python
# 简单实现
def compose(*functions):
    def inner(arg):
        result = arg
        for func in reversed(functions):
            result = func(result)
        return result
    return inner

# 使用示例
def add_one(x):
    return x + 1

def double(x):
    return x * 2

def square(x):
    return x ** 2

# compose(f, g, h)(x) = f(g(h(x)))
composed = compose(square, double, add_one)
print(composed(3))  # ((3 + 1) * 2) ** 2 = 64

# 使用 reduce 实现
from functools import reduce

def compose2(*functions):
    return reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)

composed2 = compose2(square, double, add_one)
print(composed2(3))  # 64

# 支持管道风格（从左到右）
def pipe(*functions):
    def inner(arg):
        result = arg
        for func in functions:
            result = func(result)
        return result
    return inner

piped = pipe(add_one, double, square)
print(piped(3))  # 64

# 实际应用：数据处理管道
def clean_text(text):
    return text.strip()

def lowercase(text):
    return text.lower()

def remove_punctuation(text):
    import string
    return text.translate(str.maketrans('', '', string.punctuation))

process_text = pipe(clean_text, lowercase, remove_punctuation)
result = process_text("  Hello, World!  ")
print(result)  # "hello world"
```

---

## 面向对象高级

### 31. 解释 Python 中的抽象基类（ABC）

**答案：**

```python
from abc import ABC, abstractmethod

# 定义抽象基类
class Animal(ABC):
    @abstractmethod
    def make_sound(self):
        """子类必须实现此方法"""
        pass
    
    @abstractmethod
    def move(self):
        pass
    
    def eat(self):
        """具体方法，子类可以选择重写"""
        print("Eating...")

# 尝试实例化抽象类会报错
# animal = Animal()  # TypeError

# 实现抽象基类
class Dog(Animal):
    def make_sound(self):
        return "Woof!"
    
    def move(self):
        return "Running"

dog = Dog()
print(dog.make_sound())  # Woof!
dog.eat()  # Eating...

# 抽象属性
class Shape(ABC):
    @property
    @abstractmethod
    def area(self):
        pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    @property
    def area(self):
        return 3.14 * self.radius ** 2

# 检查是否是子类
print(issubclass(Dog, Animal))  # True
print(isinstance(dog, Animal))  # True

# 虚拟子类（不需要继承）
class Cat:
    def make_sound(self):
        return "Meow!"
    
    def move(self):
        return "Walking"

Animal.register(Cat)  # 注册为虚拟子类
cat = Cat()
print(isinstance(cat, Animal))  # True
```

**使用场景：**
- 定义接口
- 强制子类实现特定方法
- 文档化预期行为

---

### 32. 什么是混入（Mixin）？如何使用？

**答案：**
Mixin 是一种提供可重用功能的类，不单独使用，通过多重继承混入其他类。

```python
# 日志 Mixin
class LoggerMixin:
    def log(self, message):
        print(f"[{self.__class__.__name__}] {message}")

# 序列化 Mixin
class SerializableMixin:
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() 
                if not k.startswith('_')}
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

# 时间戳 Mixin
from datetime import datetime

class TimestampMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def touch(self):
        self.updated_at = datetime.now()

# 使用多个 Mixin
class User(LoggerMixin, SerializableMixin, TimestampMixin):
    def __init__(self, name, email):
        super().__init__()
        self.name = name
        self.email = email
    
    def save(self):
        self.touch()
        self.log(f"Saving user {self.name}")

user = User("Alice", "alice@example.com")
user.save()
print(user.to_dict())
print(user.created_at)

# 比较 Mixin（添加比较功能）
class ComparableMixin:
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
    def __lt__(self, other):
        return self.id < other.id

class Product(ComparableMixin):
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price

p1 = Product(1, "A", 100)
p2 = Product(2, "B", 200)
print(p1 < p2)  # True
```

**Mixin 的特点：**
- 提供特定功能
- 不单独实例化
- 通常没有 `__init__`（或使用 `super()`）
- 遵循单一职责原则

---

### 33. 解释以下代码的输出

**代码：**
```python
class Parent:
    def __init__(self):
        self.value = "parent"
    
    def method(self):
        print(self.value)

class Child(Parent):
    def __init__(self):
        self.value = "child"

c = Child()
c.method()  # 输出: child
```

**答案：**
- `Child` 没有调用 `Parent.__init__()`
- `Child.__init__` 直接设置 `self.value = "child"`
- `method` 使用的是实例的 `value` 属性

**正确的继承方式：**
```python
class Child(Parent):
    def __init__(self):
        super().__init__()  # 调用父类的 __init__
        self.value = "child"  # 覆盖父类的值

# 或者保留父类的值
class Child2(Parent):
    def __init__(self):
        super().__init__()
        self.child_value = "child"
```

---

### 34. 实现一个支持链式调用的类

**答案：**

```python
class QueryBuilder:
    def __init__(self):
        self.query = ""
        self.params = []
    
    def select(self, *fields):
        self.query = f"SELECT {', '.join(fields)}"
        return self  # 返回 self 支持链式调用
    
    def from_table(self, table):
        self.query += f" FROM {table}"
        return self
    
    def where(self, condition):
        self.query += f" WHERE {condition}"
        return self
    
    def order_by(self, field, direction="ASC"):
        self.query += f" ORDER BY {field} {direction}"
        return self
    
    def limit(self, count):
        self.query += f" LIMIT {count}"
        return self
    
    def build(self):
        return self.query

# 链式调用
query = (QueryBuilder()
         .select("id", "name", "email")
         .from_table("users")
         .where("age > 18")
         .order_by("name")
         .limit(10)
         .build())

print(query)
# SELECT id, name, email FROM users WHERE age > 18 ORDER BY name ASC LIMIT 10

# 另一个例子：计算器
class Calculator:
    def __init__(self, value=0):
        self.value = value
    
    def add(self, n):
        self.value += n
        return self
    
    def subtract(self, n):
        self.value -= n
        return self
    
    def multiply(self, n):
        self.value *= n
        return self
    
    def divide(self, n):
        self.value /= n
        return self
    
    def result(self):
        return self.value

result = Calculator(10).add(5).multiply(2).subtract(10).divide(2).result()
print(result)  # 10.0
```

---

### 35. 解释 `__slots__` 的作用和限制

**答案：**
`__slots__` 限制实例可以拥有的属性，节省内存。

```python
# 普通类
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
p.z = 3  # 可以动态添加属性
print(p.__dict__)  # {'x': 1, 'y': 2, 'z': 3}

# 使用 __slots__
class PointWithSlots:
    __slots__ = ['x', 'y']
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = PointWithSlots(1, 2)
# p.z = 3  # AttributeError: 'PointWithSlots' object has no attribute 'z'
# print(p.__dict__)  # AttributeError: 没有 __dict__

# 内存对比
import sys

class Normal:
    def __init__(self):
        self.a = 1
        self.b = 2

class WithSlots:
    __slots__ = ['a', 'b']
    def __init__(self):
        self.a = 1
        self.b = 2

n = Normal()
s = WithSlots()

print(sys.getsizeof(n.__dict__))  # 约 232 字节
print(sys.getsizeof(s))           # 约 64 字节

# __slots__ 的限制
# 1. 不能动态添加属性
# 2. 没有 __dict__
# 3. 继承时需要注意

class Base:
    __slots__ = ['a']

class Derived(Base):
    __slots__ = ['b']  # 继承父类的 slots

d = Derived()
d.a = 1
d.b = 2
# d.c = 3  # AttributeError

# __slots__ 和 __weakref__
class WithWeakRef:
    __slots__ = ['x', '__weakref__']  # 支持弱引用
```

**使用场景：**
- 需要创建大量实例时
- 节省内存
- 防止意外添加属性

**限制：**
- 不能动态添加属性
- 继承复杂
- 没有 `__dict__`