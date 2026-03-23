# Python 鸭子类型（Duck Typing）详解

## 核心理念

> "如果它走起来像鸭子，叫起来像鸭子，那它就是鸭子。"
> 
> "If it walks like a duck and quacks like a duck, then it is a duck."

**鸭子类型的本质：Python 不关心对象的类型，只关心对象的行为（方法）。**

## 你的例子分析

```python
class Human:
    def eat(self):
        print("Human is eating")
    
    def sing(self):
        print("Human is singing")
    
    def dance(self):
        print("Human is dancing")

class Duck:
    def eat(self):
        print("Duck is eating")

def perform_action(animal):
    animal.eat()  # 只要有 eat() 方法就行

perform_action(Duck())   # ✅ 可以调用
perform_action(Human())  # ✅ 也可以调用
```

### 为什么可以工作？

1. **没有继承关系** - `Human` 和 `Duck` 互不相关
2. **只看方法** - `perform_action` 只关心参数是否有 `eat()` 方法
3. **运行时检查** - Python 在运行时才检查对象是否有这个方法

## 对比：静态类型语言

### Java 必须有继承或接口
```java
// Java 需要显式定义接口
interface Eatable {
    void eat();
}

class Human implements Eatable {
    public void eat() { 
        System.out.println("Human is eating"); 
    }
}

class Duck implements Eatable {
    public void eat() { 
        System.out.println("Duck is eating"); 
    }
}

// 必须声明类型
void performAction(Eatable animal) {
    animal.eat();
}
```

### Python 不需要
```python
# Python 不需要任何声明，只要有方法就行
def perform_action(animal):
    animal.eat()  # 运行时检查

# 任何有 eat() 方法的对象都可以
perform_action(Human())
perform_action(Duck())
perform_action(Robot())   # 只要 Robot 有 eat() 方法
perform_action(Car())     # 只要 Car 有 eat() 方法
```

## 完整示例

```python
# ============================================================
# 示例 1: 基础鸭子类型
# ============================================================

class Dog:
    def speak(self):
        return "汪汪汪"

class Cat:
    def speak(self):
        return "喵喵喵"

class Robot:
    def speak(self):
        return "Beep Boop"

class Car:
    def speak(self):
        return "嘟嘟嘟"

# 不需要继承，只要有 speak() 方法就行
def make_sound(obj):
    print(obj.speak())

make_sound(Dog())    # ✅
make_sound(Cat())    # ✅
make_sound(Robot())  # ✅
make_sound(Car())    # ✅


# ============================================================
# 示例 2: 文件类型接口
# ============================================================

class File:
    def read(self):
        return "从文件读取数据"
    
    def write(self, data):
        print(f"写入文件: {data}")

class Database:
    def read(self):
        return "从数据库读取数据"
    
    def write(self, data):
        print(f"写入数据库: {data}")

class Network:
    def read(self):
        return "从网络读取数据"
    
    def write(self, data):
        print(f"发送到网络: {data}")

# 通用的数据处理函数
def process_data(storage):
    """只要有 read() 和 write() 方法就行"""
    data = storage.read()
    print(f"读取: {data}")
    storage.write("处理后的数据")

process_data(File())      # ✅
process_data(Database())  # ✅
process_data(Network())   # ✅


# ============================================================
# 示例 3: 迭代器接口
# ============================================================

class CustomRange:
    """自定义 range，只需要有 __iter__ 和 __next__"""
    def __init__(self, start, stop):
        self.current = start
        self.stop = stop
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current >= self.stop:
            raise StopIteration
        value = self.current
        self.current += 1
        return value

class EvenNumbers:
    """偶数生成器"""
    def __init__(self, limit):
        self.current = 0
        self.limit = limit
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current >= self.limit:
            raise StopIteration
        value = self.current
        self.current += 2
        return value

# Python 的 for 循环只要对象有 __iter__ 就行
for i in CustomRange(0, 5):
    print(i)  # ✅ 可以迭代

for i in EvenNumbers(10):
    print(i)  # ✅ 也可以迭代
```

## 优势

### 1. 灵活性高
```python
# 不需要修改现有代码，只要新类有对应方法
def save_data(storage):
    storage.save()

# 后来添加新的存储方式，不需要改 save_data
class CloudStorage:
    def save(self):
        print("保存到云端")

save_data(CloudStorage())  # ✅ 直接可用
```

### 2. 代码简洁
```python
# 不需要定义接口或抽象类
def process(obj):
    obj.start()
    obj.run()
    obj.stop()

# 任何有这三个方法的对象都可以
```

### 3. 快速开发
```python
# 不需要事先设计复杂的类层次结构
# 只要方法名对了就行
```

## 劣势

### 1. 类型安全较弱
```python
def greet(obj):
    obj.say_hello()  # 如果 obj 没有这个方法会报错

# 运行时才会发现错误
try:
    greet(123)  # ❌ int 没有 say_hello() 方法
except AttributeError as e:
    print(f"错误: {e}")
```

### 2. IDE 支持较弱
```python
def process(obj):
    obj.unknown_method()  # IDE 无法提示这个方法是否存在
```

## 改进：使用类型提示

### 方法 1: Protocol（Python 3.8+）
```python
from typing import Protocol

class Speakable(Protocol):
    """定义协议：必须有 speak() 方法"""
    def speak(self) -> str:
        ...

def make_sound(obj: Speakable):
    """类型提示，但不强制继承"""
    print(obj.speak())

# IDE 可以检查，但运行时仍然是鸭子类型
```

### 方法 2: 抽象基类
```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self):
        pass

# 强制子类实现 speak() 方法
class Dog(Animal):
    def speak(self):
        return "汪汪汪"
```

## 实际应用场景

### 1. 文件操作
```python
# 任何类似文件的对象（file-like object）
def save_to_file(file_obj):
    file_obj.write("data")

# 可以是：
# - 真实文件
# - StringIO
# - BytesIO
# - 网络流
# - 自定义对象
```

### 2. 日志系统
```python
def log_message(logger):
    logger.info("消息")
    logger.error("错误")

# 任何有 info() 和 error() 方法的对象都可以
```

### 3. 数据库操作
```python
def query_data(db):
    db.connect()
    result = db.query("SELECT * FROM users")
    db.close()
    return result

# 可以用于 MySQL, PostgreSQL, SQLite, MongoDB...
```

## 最佳实践

### 1. EAFP vs LBYL

**EAFP（Easier to Ask for Forgiveness than Permission）**
```python
# Pythonic 风格：先做再说，出错再处理
def call_method(obj):
    try:
        obj.method()
    except AttributeError:
        print("对象没有这个方法")
```

**LBYL（Look Before You Leap）**
```python
# 非 Pythonic：先检查再做
def call_method(obj):
    if hasattr(obj, 'method'):
        obj.method()
    else:
        print("对象没有这个方法")
```

### 2. 使用 hasattr 检查
```python
def safe_call(obj):
    if hasattr(obj, 'method'):
        obj.method()
```

### 3. 使用 Protocol 提供类型提示
```python
from typing import Protocol

class HasSpeak(Protocol):
    def speak(self) -> str: ...

def make_sound(obj: HasSpeak):
    print(obj.speak())
```

### 4. 文档说明
```python
def process(obj):
    """
    处理对象
    
    参数:
        obj: 必须有 start(), run(), stop() 方法
    """
    obj.start()
    obj.run()
    obj.stop()
```

## 总结

| 特性 | 鸭子类型 | 静态类型 |
|-----|---------|---------|
| **检查时机** | 运行时 | 编译时 |
| **需要继承** | ❌ 不需要 | ✅ 需要 |
| **灵活性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **类型安全** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **IDE 支持** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **开发速度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

### 核心要点

1. ✅ **只看行为，不看类型** - 有相同方法就能调用
2. ✅ **无需继承** - 不需要共同的父类或接口
3. ✅ **运行时检查** - 在实际调用时才检查方法是否存在
4. ✅ **灵活扩展** - 后续可以添加任何有相同方法的类
5. ⚠️ **类型安全较弱** - 建议使用 Protocol 或抽象基类增强

### 记住

**Python 的哲学是："成年人应该为自己的行为负责"**

不强制类型检查，给予开发者最大的灵活性，但也要求开发者自己注意类型安全。

这就是为什么你的 `Human` 和 `Duck` 虽然没有任何继承关系，但只要都有 `eat()` 方法，就可以在 `perform_action()` 中互换使用！
