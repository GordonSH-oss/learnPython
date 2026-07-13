# Python 面试题答案

## 基础知识

### 1. Python 中的数据类型有哪些？

**答案：**
Python 的内置数据类型主要包括：
- **数值类型**：`int`（整数）、`float`（浮点数）、`complex`（复数）
- **序列类型**：`str`（字符串）、`list`（列表）、`tuple`（元组）
- **映射类型**：`dict`（字典）
- **集合类型**：`set`（集合）、`frozenset`（不可变集合）
- **布尔类型**：`bool`（True/False）
- **二进制类型**：`bytes`、`bytearray`、`memoryview`
- **None 类型**：`NoneType`

### 2. 什么是可变类型和不可变类型？请举例说明。

**答案：**
- **不可变类型（Immutable）**：对象创建后内容不能被修改。包括：`int`、`float`、`str`、`tuple`、`frozenset`、`bool`
- **可变类型（Mutable）**：对象创建后内容可以被修改。包括：`list`、`dict`、`set`、`bytearray`

```python
# 不可变类型示例
s = "hello"
s[0] = "H"  # TypeError: 'str' object does not support item assignment

# 可变类型示例
lst = [1, 2, 3]
lst[0] = 10  # 可以修改
print(lst)  # [10, 2, 3]
```

### 3. 解释 Python 中的深拷贝和浅拷贝的区别。

**答案：**
- **浅拷贝（Shallow Copy）**：创建新对象，但内部元素仍引用原对象
- **深拷贝（Deep Copy）**：递归创建新对象，完全独立于原对象

```python
import copy

original = [[1, 2], [3, 4]]

# 浅拷贝
shallow = copy.copy(original)
shallow[0][0] = 99
print(original)  # [[99, 2], [3, 4]]  # 原对象也被修改

# 深拷贝
original = [[1, 2], [3, 4]]
deep = copy.deepcopy(original)
deep[0][0] = 99
print(original)  # [[1, 2], [3, 4]]  # 原对象不受影响
```

### 4. 什么是列表推导式？它和普通循环有什么优势？

**答案：**
列表推导式是一种简洁的创建列表的方法。

```python
# 普通循环
squares = []
for i in range(10):
    squares.append(i ** 2)

# 列表推导式
squares = [i ** 2 for i in range(10)]

# 带条件的列表推导式
even_squares = [i ** 2 for i in range(10) if i % 2 == 0]
```

**优势：**
- 代码更简洁、可读性强
- 执行效率通常更高（C 语言级别优化）
- 一行代码完成过滤、映射操作

### 5. 解释 Python 中的 `*args` 和 `**kwargs`。

**答案：**
- `*args`：接收任意数量的位置参数，作为元组传递
- `**kwargs`：接收任意数量的关键字参数，作为字典传递

```python
def func(*args, **kwargs):
    print("位置参数:", args)
    print("关键字参数:", kwargs)

func(1, 2, 3, name="Alice", age=30)
# 位置参数: (1, 2, 3)
# 关键字参数: {'name': 'Alice', 'age': 30}
```

## 面向对象编程

### 6. Python 中的类和实例有什么区别？

**答案：**
- **类（Class）**：对象的蓝图或模板，定义属性和方法
- **实例（Instance）**：类的具体对象

```python
class Dog:
    species = "Canis familiaris"  # 类属性
    
    def __init__(self, name):
        self.name = name  # 实例属性

dog1 = Dog("Buddy")  # dog1 是 Dog 类的实例
dog2 = Dog("Max")    # dog2 是另一个实例
```

### 7. 什么是继承？Python 支持多重继承吗？

**答案：**
继承允许一个类获取另一个类的属性和方法。Python 支持多重继承。

```python
# 单继承
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof!"

# 多重继承
class Flyable:
    def fly(self):
        return "Flying"

class Swimmable:
    def swim(self):
        return "Swimming"

class Duck(Animal, Flyable, Swimmable):
    def speak(self):
        return "Quack!"

duck = Duck()
print(duck.speak(), duck.fly(), duck.swim())
```

**MRO（方法解析顺序）**：使用 C3 线性化算法确定方法查找顺序。

### 8. 解释 `@staticmethod`、`@classmethod` 和实例方法的区别。

**答案：**

```python
class MyClass:
    class_var = "类变量"
    
    def instance_method(self):
        """实例方法：需要实例，可访问实例和类属性"""
        return f"实例方法: {self.class_var}"
    
    @classmethod
    def class_method(cls):
        """类方法：需要类，可访问类属性，不能访问实例属性"""
        return f"类方法: {cls.class_var}"
    
    @staticmethod
    def static_method():
        """静态方法：不需要实例或类，是独立的函数"""
        return "静态方法：独立功能"

# 调用方式
obj = MyClass()
obj.instance_method()      # 通过实例调用
MyClass.class_method()     # 通过类调用
MyClass.static_method()    # 通过类调用
```

### 9. 什么是魔术方法（Magic Methods）？请举例说明常用的魔术方法。

**答案：**
魔术方法是以双下划线开头和结尾的特殊方法，用于实现运算符重载和特殊行为。

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        """print() 调用"""
        return f"Vector({self.x}, {self.y})"
    
    def __repr__(self):
        """交互式环境显示"""
        return f"Vector(x={self.x}, y={self.y})"
    
    def __add__(self, other):
        """+ 运算符"""
        return Vector(self.x + other.x, self.y + other.y)
    
    def __eq__(self, other):
        """== 运算符"""
        return self.x == other.x and self.y == other.y
    
    def __len__(self):
        """len() 函数"""
        return 2
    
    def __getitem__(self, index):
        """索引访问"""
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError("Index out of range")

v1 = Vector(1, 2)
v2 = Vector(3, 4)
print(v1 + v2)  # Vector(4, 6)
```

### 10. 解释 Python 中的属性装饰器 `@property`。

**答案：**
`@property` 将方法转换为属性，提供 getter、setter 和 deleter 功能。

```python
class Temperature:
    def __init__(self, celsius):
        self._celsius = celsius
    
    @property
    def celsius(self):
        """Getter"""
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        """Setter"""
        if value < -273.15:
            raise ValueError("温度不能低于绝对零度")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        """计算属性"""
        return self._celsius * 9/5 + 32

temp = Temperature(25)
print(temp.celsius)      # 25
temp.celsius = 30        # 使用 setter
print(temp.fahrenheit)   # 86.0
```

## 高级特性

### 11. 什么是装饰器（Decorator）？如何实现一个装饰器？

**答案：**
装饰器是修改函数或类行为的高阶函数。

```python
import time
from functools import wraps

# 基础装饰器
def timer(func):
    @wraps(func)  # 保留原函数元数据
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 执行时间: {end - start:.4f}秒")
        return result
    return wrapper

# 带参数的装饰器
def repeat(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@timer
@repeat(3)
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")
```

### 12. 解释 Python 中的生成器（Generator）和迭代器（Iterator）。

**答案：**

**迭代器（Iterator）**：实现了 `__iter__()` 和 `__next__()` 方法的对象。

```python
class Counter:
    def __init__(self, max_value):
        self.max_value = max_value
        self.current = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current >= self.max_value:
            raise StopIteration
        self.current += 1
        return self.current

for num in Counter(5):
    print(num)  # 1, 2, 3, 4, 5
```

**生成器（Generator）**：使用 `yield` 的函数，自动实现迭代器协议。

```python
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

for num in fibonacci(10):
    print(num, end=" ")  # 0 1 1 2 3 5 8 13 21 34

# 生成器表达式
squares = (x**2 for x in range(10))
```

**优势**：惰性求值，节省内存。

### 13. 什么是上下文管理器？`with` 语句的作用是什么？

**答案：**
上下文管理器管理资源的获取和释放，实现 `__enter__()` 和 `__exit__()` 方法。

```python
# 使用 with 语句
with open('file.txt', 'r') as f:
    content = f.read()
# 文件自动关闭

# 自定义上下文管理器
class DatabaseConnection:
    def __enter__(self):
        print("连接数据库")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("关闭数据库连接")
        if exc_type:
            print(f"发生异常: {exc_val}")
        return False  # 不抑制异常

# 使用 contextlib
from contextlib import contextmanager

@contextmanager
def file_manager(filename, mode):
    f = open(filename, mode)
    try:
        yield f
    finally:
        f.close()

with file_manager('test.txt', 'w') as f:
    f.write("Hello")
```

### 14. 解释 Python 中的闭包（Closure）。

**答案：**
闭包是指内部函数引用外部函数的变量，即使外部函数已经返回。

```python
def outer(x):
    def inner(y):
        return x + y  # inner 捕获了外部变量 x
    return inner

add_5 = outer(5)
print(add_5(3))  # 8
print(add_5(10)) # 15

# 使用 nonlocal 修改外部变量
def counter():
    count = 0
    def increment():
        nonlocal count  # 声明使用外部变量
        count += 1
        return count
    return increment

c = counter()
print(c())  # 1
print(c())  # 2
```

### 15. 什么是 Lambda 表达式？它有什么限制？

**答案：**
Lambda 是匿名函数，适用于简单的单行表达式。

```python
# 普通函数
def square(x):
    return x ** 2

# Lambda 表达式
square = lambda x: x ** 2

# 常用场景
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))
even = list(filter(lambda x: x % 2 == 0, numbers))

# 排序
students = [('Alice', 85), ('Bob', 92), ('Charlie', 78)]
students.sort(key=lambda x: x[1], reverse=True)
```

**限制：**
- 只能包含一个表达式
- 不能包含语句（如 `print`、`return`、循环）
- 不能有注解
- 可读性较差

## 并发与异步

### 16. 解释 Python 中的 GIL（全局解释器锁）。

**答案：**
GIL 是 CPython 的互斥锁，同一时刻只允许一个线程执行 Python 字节码。

**影响：**
- CPU 密集型任务：多线程无法利用多核（受限于 GIL）
- I/O 密集型任务：多线程有效（I/O 等待时释放 GIL）

**解决方案：**
- CPU 密集型：使用 `multiprocessing`（多进程）
- I/O 密集型：使用 `threading` 或 `asyncio`
- 使用其他 Python 解释器（Jython、IronPython）

### 17. 多线程和多进程的区别是什么？分别适用于什么场景？

**答案：**

| 特性 | 多线程 | 多进程 |
|------|--------|--------|
| 内存 | 共享同一进程的内存空间 | 独立内存空间 |
| 通信 | 简单（共享变量） | 复杂（需要 IPC） |
| 开销 | 轻量级 | 重量级 |
| GIL | 受限 | 不受限 |
| 适用场景 | I/O 密集型 | CPU 密集型 |

```python
import threading
import multiprocessing
import time

# 多线程示例（I/O 密集型）
def io_task(name):
    print(f"{name} 开始")
    time.sleep(2)
    print(f"{name} 完成")

threads = [threading.Thread(target=io_task, args=(f"线程{i}",)) 
           for i in range(3)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# 多进程示例（CPU 密集型）
def cpu_task(n):
    return sum(i*i for i in range(n))

if __name__ == '__main__':
    with multiprocessing.Pool(4) as pool:
        results = pool.map(cpu_task, [10000000] * 4)
```

### 18. 什么是协程（Coroutine）？`async`/`await` 的作用是什么？

**答案：**
协程是可以暂停和恢复的函数，用于异步编程。

```python
import asyncio

async def fetch_data(id):
    print(f"开始获取数据 {id}")
    await asyncio.sleep(2)  # 模拟 I/O 操作
    print(f"完成获取数据 {id}")
    return f"数据 {id}"

async def main():
    # 并发执行多个协程
    tasks = [fetch_data(i) for i in range(3)]
    results = await asyncio.gather(*tasks)
    print(results)

# 运行事件循环
asyncio.run(main())
```

**优势：**
- 单线程实现并发
- 避免线程切换开销
- 适合高并发 I/O 场景

### 19. 解释 `threading` 模块和 `multiprocessing` 模块的使用场景。

**答案：**

```python
# threading - I/O 密集型
import threading
import requests

def download(url):
    response = requests.get(url)
    print(f"Downloaded {len(response.content)} bytes")

urls = ["http://example.com"] * 10
threads = [threading.Thread(target=download, args=(url,)) for url in urls]
for t in threads:
    t.start()
for t in threads:
    t.join()

# multiprocessing - CPU 密集型
import multiprocessing

def compute_prime(n):
    return sum(1 for i in range(2, n) if all(i % j != 0 for j in range(2, int(i**0.5)+1)))

if __name__ == '__main__':
    numbers = [100000, 200000, 300000, 400000]
    with multiprocessing.Pool() as pool:
        results = pool.map(compute_prime, numbers)
```

### 20. 什么是线程安全？如何实现线程安全？

**答案：**
线程安全指多线程环境下，共享数据访问不会导致数据不一致。

```python
import threading

# 非线程安全
counter = 0
def increment():
    global counter
    for _ in range(100000):
        counter += 1  # 可能导致竞态条件

# 使用 Lock 实现线程安全
lock = threading.Lock()
safe_counter = 0

def safe_increment():
    global safe_counter
    for _ in range(100000):
        with lock:
            safe_counter += 1

# 使用 RLock（可重入锁）
rlock = threading.RLock()

# 使用线程安全的数据结构
from queue import Queue
q = Queue()  # 线程安全的队列
```

## 性能优化

### 21. Python 代码性能优化的常见方法有哪些？

**答案：**
1. **使用内置函数和库**：如 `map()`、`filter()`、`sum()`
2. **列表推导式代替循环**
3. **使用生成器节省内存**
4. **使用 `set` 进行查找**（O(1) vs O(n)）
5. **缓存结果**：`functools.lru_cache`
6. **避免全局变量**：局部变量访问更快
7. **使用 `__slots__`** 减少内存
8. **使用 NumPy/Pandas** 处理数值计算
9. **使用 Cython/PyPy** 加速关键代码
10. **并发处理**：`asyncio`、`multiprocessing`

```python
# 示例：使用 set 加速查找
# 慢
if item in my_list:  # O(n)
    pass

# 快
if item in my_set:   # O(1)
    pass
```

### 22. 什么是列表、字典、集合的时间复杂度？

**答案：**

| 操作 | List | Dict | Set |
|------|------|------|-----|
| 访问/查找 | O(n) | O(1) | O(1) |
| 插入 | O(1) 末尾 / O(n) 中间 | O(1) | O(1) |
| 删除 | O(n) | O(1) | O(1) |
| 包含检查 | O(n) | O(1) | O(1) |
| 迭代 | O(n) | O(n) | O(n) |

### 23. 如何使用 `cProfile` 或 `timeit` 进行性能分析？

**答案：**

```python
# timeit - 测量小代码片段执行时间
import timeit

code = """
result = sum(range(1000))
"""
time = timeit.timeit(code, number=10000)
print(f"执行时间: {time}秒")

# cProfile - 分析函数调用
import cProfile
import pstats

def my_function():
    result = []
    for i in range(10000):
        result.append(i ** 2)
    return result

cProfile.run('my_function()', 'output.stats')

# 查看结果
stats = pstats.Stats('output.stats')
stats.sort_stats('cumulative')
stats.print_stats(10)  # 显示前 10 项

# 命令行使用
# python -m cProfile -s cumulative script.py
```

### 24. 解释内存泄漏，Python 中如何避免内存泄漏？

**答案：**
内存泄漏是指程序无法释放不再使用的内存。

**常见原因：**
1. 循环引用
2. 全局变量累积
3. 未关闭的文件/数据库连接
4. 缓存无限增长

```python
# 循环引用导致内存泄漏
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

a = Node(1)
b = Node(2)
a.next = b
b.next = a  # 循环引用

# 解决方案 1：使用 weakref
import weakref

class Node:
    def __init__(self, value):
        self.value = value
        self._next = None
    
    @property
    def next(self):
        return self._next() if self._next else None
    
    @next.setter
    def next(self, node):
        self._next = weakref.ref(node) if node else None

# 解决方案 2：使用上下文管理器
with open('file.txt') as f:
    content = f.read()
# 自动关闭，防止泄漏

# 解决方案 3：限制缓存大小
from functools import lru_cache

@lru_cache(maxsize=128)  # 限制缓存大小
def compute(x):
    return x ** 2
```

### 25. 什么是缓存？如何使用 `functools.lru_cache`？

**答案：**
缓存存储函数调用结果，避免重复计算。

```python
from functools import lru_cache
import time

# 不使用缓存
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# 使用 lru_cache
@lru_cache(maxsize=128)
def fibonacci_cached(n):
    if n < 2:
        return n
    return fibonacci_cached(n-1) + fibonacci_cached(n-2)

start = time.time()
print(fibonacci(35))
print(f"无缓存: {time.time() - start:.4f}秒")

start = time.time()
print(fibonacci_cached(35))
print(f"有缓存: {time.time() - start:.4f}秒")

# 查看缓存信息
print(fibonacci_cached.cache_info())

# 清除缓存
fibonacci_cached.cache_clear()
```

## 标准库与常用工具

### 26. 解释 `collections` 模块中的常用数据结构。

**答案：**

```python
from collections import defaultdict, Counter, deque, namedtuple, OrderedDict

# defaultdict - 带默认值的字典
word_count = defaultdict(int)
for word in ["apple", "banana", "apple"]:
    word_count[word] += 1  # 不需要检查 key 是否存在

# Counter - 计数器
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
counter = Counter(words)
print(counter.most_common(2))  # [('apple', 3), ('banana', 2)]

# deque - 双端队列
dq = deque([1, 2, 3])
dq.appendleft(0)  # 左侧添加
dq.append(4)      # 右侧添加
dq.popleft()      # 左侧弹出
dq.rotate(1)      # 旋转

# namedtuple - 命名元组
Point = namedtuple('Point', ['x', 'y'])
p = Point(10, 20)
print(p.x, p.y)

# OrderedDict - 有序字典（Python 3.7+ dict 已保序）
od = OrderedDict()
od['a'] = 1
od['b'] = 2
```

### 27. 什么是正则表达式？如何在 Python 中使用 `re` 模块？

**答案：**
正则表达式是匹配字符串模式的强大工具。

```python
import re

text = "联系方式: 13812345678, 邮箱: user@example.com"

# 查找单个匹配
match = re.search(r'\d{11}', text)
if match:
    print(match.group())  # 13812345678

# 查找所有匹配
emails = re.findall(r'\w+@\w+\.\w+', text)
print(emails)  # ['user@example.com']

# 替换
new_text = re.sub(r'\d{11}', '***', text)

# 分割
parts = re.split(r'[,:]', text)

# 编译正则表达式（提高性能）
pattern = re.compile(r'\d{11}')
result = pattern.search(text)

# 分组捕获
match = re.search(r'(\d{3})(\d{4})(\d{4})', '13812345678')
print(match.groups())  # ('138', '1234', '5678')

# 常用模式
# \d - 数字  \w - 字母数字下划线  \s - 空白字符
# . - 任意字符  ^ - 开头  $ - 结尾
# * - 0或多次  + - 1或多次  ? - 0或1次  {n,m} - n到m次
```

### 28. 如何读写 JSON、CSV 文件？

**答案：**

```python
import json
import csv

# JSON 操作
data = {'name': 'Alice', 'age': 30, 'skills': ['Python', 'SQL']}

# 写入 JSON
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 读取 JSON
with open('data.json', 'r', encoding='utf-8') as f:
    loaded_data = json.load(f)

# JSON 字符串
json_str = json.dumps(data, ensure_ascii=False)
parsed_data = json.loads(json_str)

# CSV 操作
# 写入 CSV
with open('data.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['姓名', '年龄', '城市'])
    writer.writerows([
        ['Alice', 30, '北京'],
        ['Bob', 25, '上海']
    ])

# 读取 CSV
with open('data.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)

# 使用 DictReader 和 DictWriter
with open('data.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row['姓名'], row['年龄'])
```

### 29. 解释 `logging` 模块的使用和配置。

**答案：**

```python
import logging

# 基础配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 日志级别
logger.debug('调试信息')
logger.info('一般信息')
logger.warning('警告信息')
logger.error('错误信息')
logger.critical('严重错误')

# 异常日志
try:
    1 / 0
except Exception as e:
    logger.exception('捕获异常')  # 自动记录堆栈跟踪

# 高级配置
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file']
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### 30. 什么是虚拟环境？如何使用 `venv` 或 `virtualenv`？

**答案：**
虚拟环境是独立的 Python 运行环境，避免包版本冲突。

```bash
# 使用 venv（Python 3.3+）
python3 -m venv myenv

# 激活虚拟环境
# Windows
myenv\Scripts\activate
# macOS/Linux
source myenv/bin/activate

# 安装包
pip install requests

# 导出依赖
pip freeze > requirements.txt

# 安装依赖
pip install -r requirements.txt

# 退出虚拟环境
deactivate

# 使用 virtualenv
pip install virtualenv
virtualenv myenv
```

**优势：**
- 隔离项目依赖
- 避免系统包污染
- 便于部署

## Web 开发

### 31. 解释 WSGI 和 ASGI 的区别。

**答案：**

**WSGI (Web Server Gateway Interface)**：
- 同步协议
- 不支持 WebSocket、HTTP/2
- 适用于传统 Web 应用
- 服务器：Gunicorn、uWSGI

**ASGI (Asynchronous Server Gateway Interface)**：
- 异步协议
- 支持 WebSocket、HTTP/2、长连接
- 适用于实时应用
- 服务器：Uvicorn、Daphne

```python
# WSGI 应用（Flask）
def application(environ, start_response):
    status = '200 OK'
    headers = [('Content-Type', 'text/plain')]
    start_response(status, headers)
    return [b'Hello World']

# ASGI 应用（FastAPI）
async def application(scope, receive, send):
    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [[b'content-type', b'text/plain']],
    })
    await send({
        'type': 'http.response.body',
        'body': b'Hello World',
    })
```

### 32. Flask 和 Django 的主要区别是什么？

**答案：**

| 特性 | Flask | Django |
|------|-------|--------|
| 类型 | 微框架 | 全栈框架 |
| 学习曲线 | 平缓 | 陡峭 |
| 灵活性 | 高（自由组合） | 低（约定俗成） |
| 内置功能 | 少 | 多（ORM、Admin、Auth） |
| 适用场景 | 小型、API | 大型、CMS |

```python
# Flask 示例
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/users')
def get_users():
    return jsonify({'users': []})

# Django 示例
from django.http import JsonResponse
from django.views import View

class UserListView(View):
    def get(self, request):
        return JsonResponse({'users': []})
```

### 33. 什么是 ORM？举例说明如何使用 SQLAlchemy。

**答案：**
ORM（对象关系映射）将数据库表映射为 Python 类。

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# 定义模型
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100), unique=True)
    
    def __repr__(self):
        return f"<User(name={self.name}, email={self.email})>"

# 创建数据库连接
engine = create_engine('sqlite:///example.db')
Base.metadata.create_all(engine)

# 创建会话
Session = sessionmaker(bind=engine)
session = Session()

# 增
new_user = User(name='Alice', email='alice@example.com')
session.add(new_user)
session.commit()

# 查
users = session.query(User).filter(User.name == 'Alice').all()

# 改
user = session.query(User).filter_by(name='Alice').first()
user.email = 'newemail@example.com'
session.commit()

# 删
session.delete(user)
session.commit()
```

### 34. 解释 RESTful API 的设计原则。

**答案：**

**核心原则：**
1. **使用 HTTP 方法**：GET（查）、POST（增）、PUT（改）、DELETE（删）
2. **资源导向**：URL 表示资源，如 `/api/users/123`
3. **无状态**：每个请求包含完整信息
4. **统一接口**：标准化的请求/响应格式
5. **分层系统**：客户端不需知道中间层

```python
# RESTful API 示例
from flask import Flask, request, jsonify

app = Flask(__name__)

users = {1: {'id': 1, 'name': 'Alice'}}

# GET /api/users - 获取所有用户
@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(list(users.values()))

# GET /api/users/1 - 获取单个用户
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = users.get(user_id)
    if user:
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404

# POST /api/users - 创建用户
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    user_id = max(users.keys()) + 1
    users[user_id] = {'id': user_id, **data}
    return jsonify(users[user_id]), 201

# PUT /api/users/1 - 更新用户
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    if user_id in users:
        users[user_id].update(request.json)
        return jsonify(users[user_id])
    return jsonify({'error': 'User not found'}), 404

# DELETE /api/users/1 - 删除用户
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if user_id in users:
        del users[user_id]
        return '', 204
    return jsonify({'error': 'User not found'}), 404
```

### 35. 如何处理跨域请求（CORS）？

**答案：**

```python
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# 允许所有域
CORS(app)

# 限制特定域
CORS(app, resources={r"/api/*": {"origins": "https://example.com"}})

# 手动设置 CORS 头
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# 处理 OPTIONS 预检请求
@app.route('/api/users', methods=['OPTIONS'])
def options():
    return '', 204
```

## 测试与调试

### 36. Python 中有哪些常用的测试框架？

**答案：**
- **unittest**：标准库，类似 JUnit
- **pytest**：功能强大，插件丰富
- **nose2**：unittest 扩展
- **doctest**：从文档字符串提取测试

### 37. 什么是单元测试、集成测试、端到端测试？

**答案：**
- **单元测试**：测试单个函数或方法
- **集成测试**：测试多个模块协作
- **端到端测试**：模拟用户操作测试整个系统

### 38. 如何使用 `unittest` 或 `pytest` 编写测试？

**答案：**

```python
# unittest 示例
import unittest

def add(a, b):
    return a + b

class TestMath(unittest.TestCase):
    def setUp(self):
        """每个测试前执行"""
        self.x = 10
    
    def tearDown(self):
        """每个测试后执行"""
        pass
    
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
    
    def test_add_negative(self):
        self.assertEqual(add(-1, 1), 0)

if __name__ == '__main__':
    unittest.main()

# pytest 示例
import pytest

def test_add():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0

# 参数化测试
@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
])
def test_add_params(a, b, expected):
    assert add(a, b) == expected

# 测试异常
def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        1 / 0

# 运行测试
# pytest test_math.py -v
```

### 39. 什么是 Mock？如何使用 `unittest.mock`？

**答案：**
Mock 用于模拟依赖对象，隔离测试。

```python
from unittest.mock import Mock, patch, MagicMock
import requests

# 基础 Mock
mock_obj = Mock()
mock_obj.method.return_value = 42
print(mock_obj.method())  # 42

# 断言调用
mock_obj.method(1, 2, key='value')
mock_obj.method.assert_called_once_with(1, 2, key='value')

# 使用 patch 模拟外部依赖
def get_user_data(user_id):
    response = requests.get(f'https://api.example.com/users/{user_id}')
    return response.json()

@patch('requests.get')
def test_get_user_data(mock_get):
    # 模拟响应
    mock_response = Mock()
    mock_response.json.return_value = {'id': 1, 'name': 'Alice'}
    mock_get.return_value = mock_response
    
    result = get_user_data(1)
    assert result['name'] == 'Alice'
    mock_get.assert_called_once_with('https://api.example.com/users/1')

# patch 作为上下文管理器
def test_with_context():
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {'name': 'Bob'}
        result = get_user_data(1)
        assert result['name'] == 'Bob'

# MagicMock - 支持魔术方法
mock = MagicMock()
mock.__len__.return_value = 5
print(len(mock))  # 5
```

### 40. 如何使用 `pdb` 进行调试？

**答案：**

```python
import pdb

def buggy_function(x, y):
    result = x + y
    pdb.set_trace()  # 设置断点
    return result * 2

buggy_function(3, 4)

# pdb 命令
# l (list) - 显示当前代码
# n (next) - 执行下一行
# s (step) - 进入函数
# c (continue) - 继续执行
# p variable - 打印变量
# pp variable - 漂亮打印
# w (where) - 显示调用栈
# b line_number - 设置断点
# cl (clear) - 清除断点
# q (quit) - 退出调试

# 使用 breakpoint()（Python 3.7+）
def better_debug(x, y):
    result = x + y
    breakpoint()  # 更现代的方式
    return result * 2

# 命令行调试
# python -m pdb script.py

# 后置调试（程序崩溃后）
import sys
def main():
    try:
        buggy_code()
    except:
        import pdb
        pdb.post_mortem(sys.exc_info()[2])
```

---

## 总结

这份面试题涵盖了 Python 的核心知识点：
- **基础知识**：数据类型、可变性、拷贝
- **面向对象**：类、继承、装饰器、魔术方法
- **高级特性**：装饰器、生成器、闭包、上下文管理器
- **并发编程**：多线程、多进程、协程、GIL
- **性能优化**：时间复杂度、缓存、性能分析
- **标准库**：collections、re、json、logging
- **Web 开发**：WSGI/ASGI、Flask/Django、ORM、RESTful
- **测试调试**：unittest、pytest、mock、pdb

建议：
1. 理解每个概念的原理
2. 动手实践代码示例
3. 结合实际项目经验回答
4. 关注 Python 最新特性（如 Python 3.10+ 的新语法）
