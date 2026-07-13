# Python 面试题答案补充（41-100题）

## 目录
- [性能优化（41-45）](#性能优化41-45)
- [网络编程（46-50）](#网络编程46-50)
- [数据库（51-55）](#数据库51-55)
- [设计模式（56-60）](#设计模式56-60)
- [正则表达式（61-65）](#正则表达式61-65)
- [文件与IO（66-70）](#文件与io66-70)
- [打包与部署（71-75）](#打包与部署71-75)
- [安全（76-80）](#安全76-80)
- [日志与监控（81-85）](#日志与监控81-85)
- [特殊语法（86-90）](#特殊语法86-90)
- [元编程（91-95）](#元编程91-95)
- [高级应用（96-100）](#高级应用96-100)

---

## 性能优化（41-45）

### 41. 使用 `__slots__` 能节省多少内存？

约节省50-70%内存。详见 python-advanced-answers.md 第35题。

---

### 42. Python 字节码缓存机制

Python编译.py为.pyc缓存在`__pycache__`目录，加快启动速度。

---

### 43. 使用dis模块查看字节码

```python
import dis
dis.dis(lambda x: x + 1)
```

---

### 44. 列表推导式性能

比循环快20-30%，因为C层优化和减少函数调用。

---

### 45. 字符串拼接优化

使用`''.join()`而不是`+`，性能提升10倍。

---

## 网络编程（46-50）

### 46. TCP服务器实现

```python
import socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 8080))
server.listen(5)
conn, addr = server.accept()
```

---

### 47. Socket编程

Socket是网络通信端点，支持TCP(SOCK_STREAM)和UDP(SOCK_DGRAM)。

---

### 48. HTTP请求生命周期

DNS解析 → TCP握手 → 发送请求 → 服务器处理 → 返回响应 → TCP挥手

---

### 49. 网络超时处理

```python
import requests
requests.get(url, timeout=(3, 10))  # 连接超时3秒，读取超时10秒
```

---

### 50. WebSocket vs HTTP

WebSocket是全双工长连接，HTTP是半双工短连接。适用于实时通信。

---

## 数据库（51-55）

### 51. SQL注入防御

```python
# ❌ 危险
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ 安全：使用参数化查询
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

---

### 52. 数据库连接池

```python
from sqlalchemy import create_engine
engine = create_engine('postgresql://...', pool_size=10, max_overflow=20)
```

作用：复用连接，减少创建开销，提高并发性能。

---

### 53. 数据库事务

```python
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

try:
    session.add(user)
    session.commit()
except:
    session.rollback()
finally:
    session.close()
```

---

### 54. ORM的N+1问题

```python
# ❌ N+1 查询
users = session.query(User).all()
for user in users:
    print(user.posts)  # 每次都查询数据库

# ✅ 使用joinedload
from sqlalchemy.orm import joinedload
users = session.query(User).options(joinedload(User.posts)).all()
```

---

### 55. 异步数据库查询

```python
from databases import Database

database = Database('postgresql://...')

async def get_users():
    await database.connect()
    query = "SELECT * FROM users"
    rows = await database.fetch_all(query)
    return rows
```

---

## 设计模式（56-60）

### 56. 观察者模式

```python
class Subject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def notify(self, data):
        for observer in self._observers:
            observer.update(data)

class Observer:
    def update(self, data):
        print(f"Received: {data}")
```

---

### 57. 工厂模式

```python
class ShapeFactory:
    @staticmethod
    def create(shape_type):
        if shape_type == "circle":
            return Circle()
        elif shape_type == "square":
            return Square()
```

---

### 58. 装饰器模式（非@decorator）

```python
class Component:
    def operation(self):
        pass

class Decorator(Component):
    def __init__(self, component):
        self._component = component
    
    def operation(self):
        self._component.operation()
        # 添加额外功能
```

---

### 59. 策略模式

```python
class Context:
    def __init__(self, strategy):
        self._strategy = strategy
    
    def execute(self):
        return self._strategy.do_algorithm()

class ConcreteStrategyA:
    def do_algorithm(self):
        return "Strategy A"
```

---

### 60. 责任链模式

```python
class Handler:
    def __init__(self, successor=None):
        self._successor = successor
    
    def handle(self, request):
        if self._successor:
            return self._successor.handle(request)
```

---

## 正则表达式（61-65）

### 61. 邮箱地址匹配

```python
import re
pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
re.match(pattern, 'user@example.com')
```

---

### 62. 贪婪vs非贪婪匹配

```python
text = "<div>content</div>"
re.findall(r'<.*>', text)   # 贪婪：['<div>content</div>']
re.findall(r'<.*?>', text)  # 非贪婪：['<div>', '</div>']
```

---

### 63. 正则分组

```python
pattern = r'(\d{3})-(\d{4})-(\d{4})'
match = re.search(pattern, '138-1234-5678')
print(match.group(1))  # 138
print(match.groups())  # ('138', '1234', '5678')
```

---

### 64. 前瞻和后顾

```python
# 前瞻：(?=pattern)
re.findall(r'\w+(?=\.txt)', 'file.txt')  # ['file']

# 后顾：(?<=pattern)
re.findall(r'(?<=@)\w+', 'user@example')  # ['example']
```

---

### 65. 正则性能优化

- 使用`re.compile()`预编译
- 避免回溯（使用原子组）
- 使用非捕获组`(?:...)`
- 限制量词范围

---

## 文件与IO（66-70）

### 66. 高效读取大文件

```python
# 逐行读取
with open('large.txt') as f:
    for line in f:
        process(line)

# 分块读取
def read_in_chunks(file, chunk_size=8192):
    while True:
        data = file.read(chunk_size)
        if not data:
            break
        yield data
```

---

### 67. 文件打开模式

- `r`: 读取（默认）
- `w`: 写入（覆盖）
- `a`: 追加
- `x`: 独占创建
- `b`: 二进制模式
- `+`: 读写模式

---

### 68. 文件锁

```python
import fcntl

with open('file.txt', 'r') as f:
    fcntl.flock(f, fcntl.LOCK_EX)  # 排他锁
    # 操作文件
    fcntl.flock(f, fcntl.LOCK_UN)  # 解锁
```

---

### 69. 内存映射文件

```python
import mmap

with open('large.bin', 'r+b') as f:
    mm = mmap.mmap(f.fileno(), 0)
    print(mm[0:10])  # 读取前10字节
    mm.close()
```

---

### 70. 文件系统监控

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(f'{event.src_path} modified')

observer = Observer()
observer.schedule(MyHandler(), path='.', recursive=True)
observer.start()
```

---

## 打包与部署（71-75）

### 71. 创建Python包

```
my_package/
├── setup.py
├── README.md
├── my_package/
│   ├── __init__.py
│   └── module.py
└── tests/
```

---

### 72. setup.py vs pyproject.toml

- `setup.py`: 传统方式，使用setuptools
- `pyproject.toml`: 现代方式，PEP 518标准

---

### 73. 发布到PyPI

```bash
python setup.py sdist bdist_wheel
twine upload dist/*
```

---

### 74. wheel文件

预编译的二进制包，安装更快，跨平台兼容。

---

### 75. Docker部署

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

---

## 安全（76-80）

### 76. 密码安全存储

```python
import bcrypt

# 加密
password = b"secret"
hashed = bcrypt.hashpw(password, bcrypt.gensalt())

# 验证
bcrypt.checkpw(password, hashed)
```

---

### 77. CSRF和XSS防御

**CSRF**: 使用CSRF token
**XSS**: 转义用户输入，使用Content-Security-Policy

---

### 78. JWT Token验证

```python
import jwt

# 生成
token = jwt.encode({'user_id': 123}, 'secret', algorithm='HS256')

# 验证
payload = jwt.decode(token, 'secret', algorithms=['HS256'])
```

---

### 79. API限流

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route("/api")
@limiter.limit("100/hour")
def api():
    return "OK"
```

---

### 80. 密码学库

- `cryptography`: 现代加密库
- `pycryptodome`: PyCrypto替代
- `bcrypt`: 密码哈希
- `hashlib`: 标准库哈希

---

## 日志与监控（81-85）

### 81. 结构化日志

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            'time': record.created,
            'level': record.levelname,
            'message': record.getMessage()
        })
```

---

### 82. 日志轮转

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

---

### 83. 分布式追踪

使用OpenTelemetry或Jaeger进行请求追踪。

---

### 84. 应用性能监控

```python
from prometheus_client import Counter, Histogram

request_count = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')
```

---

### 85. 错误报警

集成Sentry、Rollbar等错误追踪服务。

---

## 特殊语法（86-90）

### 86. Walrus操作符(:=)

```python
# Python 3.8+
if (n := len(data)) > 10:
    print(f"List is too long ({n} elements)")

# 列表推导式中
[y := x + 1, y**2 for x in range(5)]
```

---

### 87. f-string高级用法

```python
name = "Alice"
value = 12.3456

# 格式化
f"{value:.2f}"  # 12.35
f"{name:>10}"   # "     Alice"
f"{value:0>8}"  # "012.3456"

# 表达式
f"{2 * 3}"  # "6"
f"{name.upper()}"  # "ALICE"

# 调试（Python 3.8+）
f"{name=}"  # "name='Alice'"
```

---

### 88. match-case（Python 3.10+）

```python
def http_status(status):
    match status:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500 | 502 | 503:
            return "Server Error"
        case _:
            return "Unknown"
```

---

### 89. 类型注解

```python
from typing import List, Dict, Optional, Union

def greet(name: str) -> str:
    return f"Hello, {name}"

users: List[Dict[str, Union[str, int]]] = [
    {"name": "Alice", "age": 30}
]
```

---

### 90. *和**在参数中的用法

```python
# * 强制关键字参数
def func(a, *, b, c):
    pass

func(1, b=2, c=3)  # ✅
# func(1, 2, 3)    # ❌

# ** 展开字典
kwargs = {'x': 1, 'y': 2}
func(**kwargs)
```

---

## 元编程（91-95）

### 91. 动态创建函数

```python
def make_function(name):
    def func():
        print(f"Function {name}")
    func.__name__ = name
    return func

# 使用exec
code = "def dynamic_func(): return 42"
exec(code)
```

---

### 92. 动态导入模块

```python
import importlib

module = importlib.import_module('math')
sqrt = getattr(module, 'sqrt')
```

---

### 93. __getattr__ vs __getattribute__

```python
class MyClass:
    def __getattr__(self, name):
        # 属性不存在时调用
        return f"Attribute {name} not found"
    
    def __getattribute__(self, name):
        # 所有属性访问都调用
        return super().__getattribute__(name)
```

---

### 94. 属性代理

```python
class Proxy:
    def __init__(self, obj):
        self._obj = obj
    
    def __getattr__(self, name):
        return getattr(self._obj, name)
```

---

### 95. AST操作

```python
import ast

code = "x = 1 + 2"
tree = ast.parse(code)
print(ast.dump(tree))
```

---

## 高级应用（96-100）

### 96. 进程间通信

```python
from multiprocessing import Process, Queue

def worker(q):
    q.put("result")

q = Queue()
p = Process(target=worker, args=(q,))
p.start()
result = q.get()
p.join()
```

---

### 97. 分布式锁

```python
import redis

r = redis.Redis()
lock = r.lock('my_lock', timeout=10)

with lock:
    # 临界区代码
    pass
```

---

### 98. 定时任务

```python
# 使用APScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', hour=0)
def midnight_task():
    print("Running at midnight")

scheduler.start()
```

---

### 99. 优雅重启

```python
import signal
import sys

def signal_handler(sig, frame):
    print('Graceful shutdown...')
    # 清理资源
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
```

---

### 100. 性能分析

```python
# cProfile
import cProfile
cProfile.run('my_function()')

# line_profiler
@profile
def my_function():
    pass

# memory_profiler
from memory_profiler import profile

@profile
def memory_heavy():
    pass
```

---

## 总结

这100道题目涵盖了Python从基础到高级的所有重要知识点。建议：

1. **系统学习**：按分类逐个攻克
2. **动手实践**：每道题都要自己写代码
3. **理解原理**：不要死记硬背
4. **关注更新**：Python持续演进
5. **结合项目**：理论联系实际

祝面试顺利！🚀