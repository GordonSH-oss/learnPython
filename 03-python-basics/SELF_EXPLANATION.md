# Python 中 `self` 参数详解

## 🎯 核心规则

**简单判断方法：**
- ✅ **实例方法** → 需要 `self`（访问实例属性或方法）
- ✅ **类方法** → 需要 `cls`（访问类属性或方法）
- ❌ **静态方法** → 不需要 `self` 或 `cls`（不访问类或实例）

---

## 📚 三种方法类型

### 1. 实例方法（Instance Method）- 需要 `self`

**特征：**
- 第一个参数必须是 `self`
- 可以访问实例属性（`self.xxx`）
- 可以访问类属性（`self.__class__.xxx` 或 `ClassName.xxx`）
- 通过实例调用：`instance.method()`

**示例：**

```python
class Person:
    species = "Homo sapiens"  # 类属性
    
    def __init__(self, name: str, age: int):
        # ✅ 需要 self：访问实例属性
        self.name = name      # 实例属性
        self.age = age        # 实例属性
    
    def introduce(self):
        # ✅ 需要 self：访问实例属性
        return f"我是 {self.name}，{self.age} 岁"
    
    def get_info(self):
        # ✅ 需要 self：同时访问实例和类属性
        return f"{self.name} ({self.age}) - {self.species}"
    
    def have_birthday(self):
        # ✅ 需要 self：修改实例属性
        self.age += 1
        return self.age

# 使用
person = Person("张三", 25)
print(person.introduce())      # 我是 张三，25 岁
print(person.get_info())       # 张三 (25) - Homo sapiens
person.have_birthday()
print(person.age)              # 26
```

**判断标准：**
- ✅ 方法内部使用了 `self.xxx` → 需要 `self`
- ✅ 方法需要访问或修改实例属性 → 需要 `self`
- ✅ 方法需要调用其他实例方法 → 需要 `self`

---

### 2. 类方法（Class Method）- 需要 `cls`

**特征：**
- 使用 `@classmethod` 装饰器
- 第一个参数必须是 `cls`（类本身）
- 可以访问类属性（`cls.xxx`）
- **不能**直接访问实例属性
- 通过类或实例调用：`ClassName.method()` 或 `instance.method()`

**示例：**

```python
class Person:
    population = 0  # 类属性
    
    def __init__(self, name: str):
        self.name = name
        Person.population += 1
    
    @classmethod
    def get_population(cls):
        # ✅ 需要 cls：访问类属性
        return cls.population
    
    @classmethod
    def create_baby(cls, name: str):
        # ✅ 需要 cls：创建新实例（工厂方法）
        return cls(name)
    
    @classmethod
    def reset_population(cls):
        # ✅ 需要 cls：修改类属性
        cls.population = 0

# 使用
person1 = Person("张三")
person2 = Person("李四")
print(Person.get_population())  # 2
print(person1.get_population()) # 2（也可以通过实例调用）

baby = Person.create_baby("王五")
print(Person.get_population())  # 3
```

**判断标准：**
- ✅ 方法需要访问类属性 → 使用 `@classmethod` + `cls`
- ✅ 方法需要创建新实例（工厂方法）→ 使用 `@classmethod` + `cls`
- ✅ 方法需要修改类属性 → 使用 `@classmethod` + `cls`

---

### 3. 静态方法（Static Method）- 不需要 `self` 或 `cls`

**特征：**
- 使用 `@staticmethod` 装饰器
- **不需要** `self` 或 `cls` 参数
- **不能**访问实例属性或类属性
- 只是一个普通函数，但逻辑上属于这个类
- 通过类或实例调用：`ClassName.method()` 或 `instance.method()`

**示例：**

```python
class MathUtils:
    @staticmethod
    def add(a: int, b: int) -> int:
        # ❌ 不需要 self：不访问任何类或实例属性
        return a + b
    
    @staticmethod
    def is_even(n: int) -> bool:
        # ❌ 不需要 self：纯函数，不依赖类或实例
        return n % 2 == 0
    
    @staticmethod
    def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
        # ❌ 不需要 self：工具函数
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

# 使用
print(MathUtils.add(3, 5))                    # 8
print(MathUtils.is_even(4))                  # True
print(MathUtils.calculate_distance(0, 0, 3, 4))  # 5.0

# 也可以通过实例调用
utils = MathUtils()
print(utils.add(2, 3))                       # 5
```

**判断标准：**
- ✅ 方法不访问任何实例属性（`self.xxx`）→ 不需要 `self`
- ✅ 方法不访问任何类属性（`ClassName.xxx`）→ 不需要 `cls`
- ✅ 方法是纯函数，逻辑上属于这个类 → 使用 `@staticmethod`

---

## 🔍 详细对比表

| 方法类型 | 装饰器 | 第一个参数 | 访问实例属性 | 访问类属性 | 调用方式 |
|---------|--------|-----------|-------------|-----------|---------|
| **实例方法** | 无 | `self` | ✅ 可以 | ✅ 可以 | `instance.method()` |
| **类方法** | `@classmethod` | `cls` | ❌ 不能 | ✅ 可以 | `ClassName.method()` 或 `instance.method()` |
| **静态方法** | `@staticmethod` | 无 | ❌ 不能 | ❌ 不能 | `ClassName.method()` 或 `instance.method()` |

---

## 💡 实际例子：你的 Node 类

```python
class Node:
    def __init__(self, value: int, next: Node | None):
        # ✅ 需要 self：因为要设置实例属性
        self.value = value
        self.next = next
    
    def get_value(self):
        # ✅ 需要 self：访问实例属性 self.value
        return self.value
    
    def get_next(self):
        # ✅ 需要 self：访问实例属性 self.next
        return self.next
    
    def set_next(self, next_node):
        # ✅ 需要 self：修改实例属性 self.next
        self.next = next_node
    
    @staticmethod
    def is_valid_value(value):
        # ❌ 不需要 self：不访问实例或类属性，纯验证函数
        return isinstance(value, int)
    
    @classmethod
    def create_empty(cls):
        # ✅ 需要 cls：创建新实例（工厂方法）
        return cls(0, None)
```

---

## 🎓 判断流程

```
定义方法时，问自己：

1. 这个方法需要访问或修改实例属性（self.xxx）吗？
   ├─ 是 → ✅ 使用实例方法，需要 self
   └─ 否 → 继续

2. 这个方法需要访问或修改类属性（ClassName.xxx）吗？
   ├─ 是 → ✅ 使用类方法，需要 cls，加 @classmethod
   └─ 否 → 继续

3. 这个方法只是逻辑上属于这个类，但不访问任何属性？
   └─ 是 → ✅ 使用静态方法，不需要 self/cls，加 @staticmethod
```

---

## ⚠️ 常见错误

### 错误 1：忘记加 `self`

```python
class Person:
    def __init__(self, name: str):
        self.name = name
    
    def greet():  # ❌ 错误：缺少 self
        return f"Hello, {self.name}"  # ❌ 会报错：name 'self' is not defined

# 正确写法
def greet(self):  # ✅ 正确
    return f"Hello, {self.name}"
```

### 错误 2：实例方法中不需要 `self` 却加了

```python
class Calculator:
    @staticmethod
    def add(self, a: int, b: int):  # ❌ 错误：静态方法不需要 self
        return a + b

# 正确写法
@staticmethod
def add(a: int, b: int):  # ✅ 正确：静态方法不需要 self
    return a + b
```

### 错误 3：类方法用了 `self` 而不是 `cls`

```python
class Person:
    population = 0
    
    @classmethod
    def get_population(self):  # ❌ 错误：应该用 cls
        return self.population  # 虽然能工作，但不规范

# 正确写法
@classmethod
def get_population(cls):  # ✅ 正确：类方法用 cls
    return cls.population
```

---

## 🎯 快速记忆

1. **`__init__` 方法** → 总是需要 `self`（初始化实例属性）
2. **访问 `self.xxx`** → 需要 `self`（实例方法）
3. **访问 `ClassName.xxx` 且不依赖实例** → 用 `@classmethod` + `cls`
4. **纯函数，不访问任何属性** → 用 `@staticmethod`，不需要参数

---

## 📝 总结

| 场景 | 需要什么 |
|------|---------|
| 访问/修改实例属性 | `self`（实例方法） |
| 访问/修改类属性 | `cls`（类方法，`@classmethod`） |
| 纯函数，不访问属性 | 不需要参数（静态方法，`@staticmethod`） |
| `__init__` 方法 | 总是需要 `self` |

**记住：**
- 需要访问实例数据 → `self`
- 需要访问类数据 → `cls` + `@classmethod`
- 不需要访问任何数据 → `@staticmethod`

---

Happy Coding! 🚀

