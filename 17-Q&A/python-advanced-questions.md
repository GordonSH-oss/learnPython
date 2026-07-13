# Python 高级面试题（易错/复杂）

## 易错陷阱题

### 1. 解释以下代码的输出，为什么会这样？

```python
def append_to_list(element, lst=[]):
    lst.append(element)
    return lst

print(append_to_list(1))
print(append_to_list(2))
print(append_to_list(3))
```

### 2. 以下代码的输出是什么？为什么？

```python
x = [1, 2, 3]
y = x
y.append(4)
print(x)
```

### 3. 以下闭包代码的输出是什么？如何修复？

```python
funcs = []
for i in range(3):
    funcs.append(lambda: i)

for func in funcs:
    print(func())
```

### 4. 解释以下代码的输出

```python
a = [1, 2, 3]
b = a
c = a[:]
d = a.copy()

a.append(4)
a[0] = 100

print(b)
print(c)
print(d)
```

### 5. 以下代码会发生什么？

```python
class MyClass:
    shared_list = []
    
    def add(self, item):
        self.shared_list.append(item)

obj1 = MyClass()
obj2 = MyClass()
obj1.add(1)
obj2.add(2)
print(obj1.shared_list)
print(obj2.shared_list)
```

## 复杂机制题

### 6. 解释 Python 的 MRO（方法解析顺序）在多重继承中如何工作？

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
d.method()  # 输出什么？
print(D.__mro__)  # MRO 顺序是什么？
```

### 7. 什么是描述符（Descriptor）？实现一个验证描述符。

### 8. 解释以下装饰器代码的问题，如何解决？

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

print(greet.__name__)  # 输出什么？
print(greet.__doc__)   # 输出什么？
```

### 9. 以下生成器代码有什么问题？

```python
def generator():
    yield 1
    return 2
    yield 3

g = generator()
print(next(g))
print(next(g))
```

### 10. 解释以下异常处理的输出

```python
def func():
    try:
        return 1
    finally:
        return 2

print(func())
```

### 11. 以下元类代码实现了什么功能？

```python
class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class MyClass(metaclass=SingletonMeta):
    pass
```

### 12. 解释 `is` 和 `==` 的区别，以下代码输出什么？

```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(a == b)
print(a is b)
print(a is c)

x = 256
y = 256
print(x is y)

m = 257
n = 257
print(m is n)
```

### 13. 以下协程代码会发生什么？

```python
import asyncio

async def task1():
    print("Task 1 start")
    await asyncio.sleep(2)
    print("Task 1 end")
    return "Result 1"

async def task2():
    print("Task 2 start")
    result = task1()  # 注意这里没有 await
    print("Task 2 end")
    return result

asyncio.run(task2())
```

### 14. 解释以下变量作用域的输出

```python
x = 10

def outer():
    x = 20
    def inner():
        x = 30
        print("inner:", x)
    inner()
    print("outer:", x)

outer()
print("global:", x)

# 如果修改为以下代码会怎样？
def outer2():
    x = 20
    def inner2():
        global x
        x = 30
    inner2()
    print("outer2:", x)

outer2()
print("global after outer2:", x)
```

### 15. 以下深拷贝代码有什么问题？如何解决？

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

c = copy.deepcopy(a)  # 会发生什么？
```

### 16. 解释以下装饰器链的执行顺序

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

my_function()
```

### 17. 以下字典推导式的输出是什么？

```python
keys = ['a', 'b', 'c']
d1 = {key: [] for key in keys}
d1['a'].append(1)
print(d1)

d2 = dict.fromkeys(keys, [])
d2['a'].append(1)
print(d2)
```

### 18. 解释以下上下文管理器的执行流程

```python
class MyContext:
    def __enter__(self):
        print("Enter")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Exit: {exc_type}")
        return True  # 这行的作用是什么？

with MyContext():
    print("Inside")
    raise ValueError("Error")
print("After with")
```

### 19. 以下多线程代码的输出是确定的吗？如何保证线程安全？

```python
import threading

counter = 0

def increment():
    global counter
    for _ in range(100000):
        counter += 1

threads = [threading.Thread(target=increment) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(counter)  # 期望 1000000，实际是多少？
```

### 20. 解释以下 `__new__` 和 `__init__` 的区别

```python
class MyClass:
    def __new__(cls, *args, **kwargs):
        print("__new__ called")
        instance = super().__new__(cls)
        return instance
    
    def __init__(self, value):
        print("__init__ called")
        self.value = value

obj = MyClass(42)
```

## 数据结构与算法

### 21. 实现一个 LRU 缓存

### 22. 如何检测链表中是否有环？

### 23. 实现一个线程安全的单例模式

### 24. 解释以下代码的时间复杂度

```python
def func(n):
    for i in range(n):
        for j in range(i):
            print(i, j)
```

### 25. 如何反转字典的键和值？处理值重复的情况

## 函数式编程

### 26. 解释 map、filter、reduce 的区别和使用场景

### 27. 什么是柯里化（Currying）？实现一个柯里化函数

### 28. 解释以下代码的输出

```python
from functools import partial

def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
print(square(5))
print(square(base=3))
```

### 29. 什么是纯函数？列举 Python 中的纯函数

### 30. 实现一个函数组合（compose）工具

## 面向对象高级

### 31. 解释 Python 中的抽象基类（ABC）

### 32. 什么是混入（Mixin）？如何使用？

### 33. 解释以下代码的输出

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
c.method()
```

### 34. 实现一个支持链式调用的类

### 35. 解释 `__slots__` 的作用和限制

## 异步编程

### 36. 解释 async/await 与回调的区别

### 37. 如何在同步代码中调用异步函数？

### 38. 解释以下代码的执行顺序

```python
import asyncio

async def main():
    print("1")
    await asyncio.sleep(0)
    print("2")

print("0")
asyncio.run(main())
print("3")
```

### 39. 什么是事件循环？如何获取当前事件循环？

### 40. 如何取消一个正在运行的协程？

## 性能优化

### 41. 使用 `__slots__` 能节省多少内存？

### 42. 解释 Python 的字节码缓存机制

### 43. 如何使用 `dis` 模块查看字节码？

### 44. 列表推导式比循环快多少？为什么？

### 45. 如何优化字符串拼接？

## 网络编程

### 46. 实现一个简单的 TCP 服务器

### 47. 什么是 Socket？如何使用？

### 48. 解释 HTTP 请求的生命周期

### 49. 如何处理网络超时？

### 50. 什么是 WebSocket？与 HTTP 的区别

## 数据库

### 51. 如何防止 SQL 注入？

### 52. 解释数据库连接池的作用

### 53. 如何实现数据库事务？

### 54. ORM 的 N+1 问题是什么？如何解决？

### 55. 如何使用 asyncio 进行异步数据库查询？

## 设计模式

### 56. 实现观察者模式

### 57. 实现工厂模式

### 58. 实现装饰器模式（不使用 @decorator）

### 59. 实现策略模式

### 60. 实现责任链模式

## 正则表达式

### 61. 如何匹配邮箱地址？

### 62. 解释贪婪匹配和非贪婪匹配

### 63. 如何使用正则表达式分组？

### 64. 正则表达式的前瞻和后顾是什么？

### 65. 如何提高正则表达式的性能？

## 文件与 I/O

### 66. 如何高效读取大文件？

### 67. 解释文件的不同打开模式

### 68. 如何实现文件锁？

### 69. 什么是内存映射文件？

### 70. 如何监控文件系统变化？

## 打包与部署

### 71. 如何创建 Python 包？

### 72. setup.py 和 pyproject.toml 的区别

### 73. 如何发布包到 PyPI？

### 74. 什么是 wheel 文件？

### 75. 如何使用 Docker 部署 Python 应用？

## 安全

### 76. 如何安全存储密码？

### 77. 什么是 CSRF 和 XSS？如何防御？

### 78. 如何验证 JWT Token？

### 79. 如何实现 API 限流？

### 80. Python 中的密码学库有哪些？

## 日志与监控

### 81. 如何配置结构化日志？

### 82. 如何实现日志轮转？

### 83. 如何追踪分布式系统的请求？

### 84. 如何监控应用性能？

### 85. 如何实现错误报警？

## 特殊语法

### 86. 解释 Python 的 walrus 操作符（:=）

### 87. 什么是 f-string？有什么高级用法？

### 88. 解释 match-case（结构化模式匹配）

### 89. 什么是类型注解？如何使用？

### 90. 解释 * 和 ** 在函数参数中的用法

## 元编程

### 91. 如何动态创建函数？

### 92. 如何动态导入模块？

### 93. 解释 `__getattr__` 和 `__getattribute__` 的区别

### 94. 如何实现属性代理？

### 95. 什么是 AST？如何操作？

## 高级应用

### 96. 如何实现进程间通信？

### 97. 如何实现分布式锁？

### 98. 如何实现定时任务？

### 99. 如何实现优雅重启？

### 100. 如何进行 Python 程序的性能分析？