# Python 基础特性

学习 Python 语言的核心概念和基础特性。

## 核心概念

### 1. self 关键字
- **文件**: `self_examples.py`, `SELF_EXPLANATION.md`
- **内容**: 理解 self 在类中的作用
- **要点**: 实例引用、方法调用、属性访问

### 2. 数据类 (DataClass)
- **文件**: `data_class.py`
- **内容**: 使用 `@dataclass` 装饰器简化类定义
- **要点**: `field()`, `default_factory`, 避免可变默认值陷阱

### 3. 特殊方法（Magic Methods）
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

### 4. 切片机制
- **文件**: `slice_explanation.py`
- **内容**: 深入理解 Python 的切片操作
- **要点**: `__getitem__` 魔法方法、slice 对象、切片语法

### 5. 元组 (Tuple)
- **文件**: 
  - `tuple_immutability_explanation.py` - 元组的不可变性
  - `tuple_equality_explanation.py` - 元组的相等性比较
- **内容**: 元组的特性和使用场景
- **要点**: 不可变性、哈希、解包

### 5. Pydantic 数据校验
- **文件**: 
  - `pydantic_examples.py` - Pydantic 实用案例集合（基础 ⭐⭐）
  - `pydantic-generic.py` - Pydantic 结合泛型的高级用法（进阶 ⭐⭐⭐⭐）
  - `PYDANTIC_GUIDE.md` - Pydantic 完整使用指南
  - `PYDANTIC_FILES.md` - 两个文件的对比和学习建议
- **内容**: 
  - **基础**: 数据校验、类型转换、自定义校验器、字段别名、序列化、嵌套模型、配置管理
  - **进阶**: 泛型与 Pydantic 结合、通用分页器、统一响应格式
- **要点**: BaseModel、Field、校验器、泛型、序列化

### 6. 链表初始化
- **文件**: `LINKED_LIST_INITIALIZATION.md`
- **内容**: 链表数据结构的初始化方法
- **要点**: 节点创建、指针操作

## 学习顺序建议

1. **self_examples.py** - 理解面向对象基础
2. **data_class.py** - 学习简化类定义的方法
3. **special-methods/** - 学习 Python 特殊方法
   - 从 `property_decorator.py` 开始
   - 然后 `str_and_repr.py`
   - 最后 `comparison_operators.py` 和其他
4. **pydantic_examples.py** - 掌握数据校验和 Pydantic 基础
5. **pydantic-generic.py** - Pydantic 与泛型结合的高级用法
6. **slice_explanation.py** - 掌握切片和魔法方法
7. **tuple_immutability_explanation.py** - 理解不可变数据类型
8. **tuple_equality_explanation.py** - 深入元组比较
9. **LINKED_LIST_INITIALIZATION.md** - 数据结构基础

## 关键知识点

### self 的作用
```python
class MyClass:
    def __init__(self, value):
        self.value = value  # self 指向当前实例
    
    def method(self):
        return self.value   # 访问实例属性
```

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

## 实践建议

1. **运行示例代码** - 每个 `.py` 文件都可以直接运行
2. **修改参数** - 尝试修改代码中的参数观察变化
3. **阅读文档** - `.md` 文件提供详细说明
4. **调试练习** - 使用 Python 调试器单步执行

## 扩展阅读

- Python 官方文档: https://docs.python.org/3/
- Real Python 教程: https://realpython.com/
- Fluent Python (书籍)
