# Python 特殊方法（Magic Methods）详解

这个文件夹包含 Python 特殊方法（也称为魔法方法或双下划线方法）的详细示例和说明。

## 什么是特殊方法？

特殊方法是 Python 中以双下划线 `__` 开头和结尾的方法，它们定义了对象如何响应内置操作。例如：
- `__init__`: 初始化对象
- `__str__`: 定义 `str()` 的行为
- `__add__`: 定义 `+` 运算符的行为

## 文件列表

### 1. property_decorator.py
**@property 装饰器详解**

涵盖内容：
- ✅ 只读属性
- ✅ 完整的 getter/setter/deleter
- ✅ 惰性求值和缓存
- ✅ 数据验证和转换
- ✅ 私有属性保护
- ✅ 依赖属性

**6 个实用案例：**
1. 基础使用 - 只读属性（Circle 类）
2. 完整的 getter/setter/deleter（Temperature 类）
3. 惰性求值 - 缓存计算结果（DataAnalyzer 类）
4. 数据验证和转换（Person 类）
5. 私有属性保护（BankAccount 类）
6. 依赖属性（Rectangle 类）

### 2. str_and_repr.py
**__str__ 和 __repr__ 详解**

涵盖内容：
- ✅ `__str__` vs `__repr__` 的区别
- ✅ 用户友好 vs 开发者友好
- ✅ 可重建对象的 repr
- ✅ 复杂对象的格式化
- ✅ 嵌套对象的表示
- ✅ f-string 中的 !s, !r, !a

**8 个案例：**
1. 基础区别（Point 类）
2. 只实现 __repr__（User 类）
3. 可重建对象的 __repr__（Color 类）
4. 复杂对象的字符串表示（Book 类）
5. 嵌套对象的表示（Person 类）
6. 格式化字符串中的使用（Product 类）
7. 调试时的最佳实践（Task 类）
8. 默认行为

### 3. comparison_operators.py
**比较运算符魔法方法**

涵盖内容：
- ✅ `__eq__`, `__ne__` - 相等性比较
- ✅ `__lt__`, `__le__`, `__gt__`, `__ge__` - 大小比较
- ✅ `@total_ordering` 装饰器
- ✅ 多字段比较
- ✅ 与其他类型的比较
- ✅ `__hash__` 与 `__eq__` 的配合

**7 个案例：**
1. 基础比较（Point 类）
2. 完整的比较运算符（Version 类）
3. 使用 @total_ordering 简化（Student 类）
4. 复杂对象的比较（Employee 类）
5. 与其他类型的比较（Money 类）
6. NotImplemented 的使用（Apple 类）
7. 哈希和相等性（ImmutablePoint 类）

### 4. arithmetic_operators.py
**算术运算符魔法方法**

涵盖内容：
- ✅ 基础运算：`__add__`, `__sub__`, `__mul__`, `__truediv__`
- ✅ 反向运算：`__radd__`, `__rmul__` 等
- ✅ 增强赋值：`__iadd__`, `__imul__` 等
- ✅ 其他运算：`__floordiv__`, `__mod__`, `__pow__`, `__divmod__`
- ✅ 一元运算：`__neg__`, `__pos__`, `__abs__`
- ✅ 位运算：`__and__`, `__or__`, `__xor__`

**6 个案例：**
1. 基础算术运算符（Vector 类）
2. 反向运算符（Money 类）
3. 增强赋值运算符（Counter 类）
4. 完整的数学运算（Fraction 类）
5. 整除、取模、divmod（Time 类）
6. 位运算符（BitSet 类）

### 5. container_methods.py
**容器类型魔法方法**

涵盖内容：
- ✅ `__len__`, `__getitem__`, `__setitem__`, `__delitem__`
- ✅ `__contains__` - 成员测试
- ✅ `__iter__`, `__next__` - 迭代器协议
- ✅ 切片支持
- ✅ 多维索引

**7 个案例：**
1. 基础容器实现（SimpleList 类）
2. 迭代器协议（Range 类）
3. 字典类型容器（CaseInsensitiveDict 类）
4. 惰性加载容器（LazyList 类）
5. 多维数组（Matrix 类）
6. 自定义集合（UniqueList 类）
7. 反向索引（CircularList 类）

## 快速查找

### 按功能分类

#### 属性和访问控制
- `@property` → `property_decorator.py`
- `__getattr__`, `__setattr__` → 待补充

#### 对象表示
- `__str__`, `__repr__` → `str_and_repr.py`
- `__format__` → 待补充

#### 运算符重载
- 比较运算 → `comparison_operators.py`
- 算术运算 → `arithmetic_operators.py`
- 位运算 → `arithmetic_operators.py`（案例 6）

#### 容器和迭代
- 容器协议 → `container_methods.py`
- 迭代器协议 → `container_methods.py`（案例 2）

#### 上下文管理
- `__enter__`, `__exit__` → 待补充

#### 可调用对象
- `__call__` → 待补充

## 学习顺序建议

### 初学者路径
1. **property_decorator.py** - 从最常用的 @property 开始
2. **str_and_repr.py** - 学习对象的字符串表示
3. **container_methods.py** - 案例 1、3 了解基础容器
4. **comparison_operators.py** - 案例 1、2 学习比较

### 进阶路径
1. **comparison_operators.py** - 完整学习
2. **arithmetic_operators.py** - 完整学习
3. **container_methods.py** - 完整学习，包括迭代器

## 使用示例

### 快速测试

```bash
cd 03-python-basics/special-methods

# 运行任意示例文件
python property_decorator.py
python str_and_repr.py
python comparison_operators.py
python arithmetic_operators.py
python container_methods.py
```

### 单独运行某个案例

每个文件都包含多个独立的案例，可以复制单个案例代码到新文件中运行。

## 特殊方法完整列表

### 对象创建和销毁
- `__new__`: 创建实例（在 __init__ 之前）
- `__init__`: 初始化实例
- `__del__`: 对象销毁时调用

### 对象表示
- `__repr__`: 开发者友好的字符串表示
- `__str__`: 用户友好的字符串表示
- `__format__`: 格式化字符串
- `__bytes__`: 字节表示

### 属性访问
- `__getattr__`: 访问不存在的属性
- `__setattr__`: 设置属性
- `__delattr__`: 删除属性
- `__getattribute__`: 访问任何属性（慎用）
- `__dir__`: dir() 函数

### 比较运算符
- `__eq__`: ==
- `__ne__`: !=
- `__lt__`: <
- `__le__`: <=
- `__gt__`: >
- `__ge__`: >=

### 算术运算符
- `__add__`, `__sub__`, `__mul__`, `__truediv__`: +, -, *, /
- `__floordiv__`, `__mod__`, `__pow__`: //, %, **
- `__and__`, `__or__`, `__xor__`: &, |, ^
- `__lshift__`, `__rshift__`: <<, >>

### 反向运算符
- `__radd__`, `__rsub__`, `__rmul__`: 右侧运算

### 增强赋值
- `__iadd__`, `__isub__`, `__imul__`: +=, -=, *=

### 一元运算符
- `__neg__`: -x
- `__pos__`: +x
- `__abs__`: abs(x)
- `__invert__`: ~x

### 类型转换
- `__int__`, `__float__`, `__complex__`: int(), float(), complex()
- `__bool__`: bool()
- `__index__`: 索引运算

### 容器类型
- `__len__`: len()
- `__getitem__`: obj[key]
- `__setitem__`: obj[key] = value
- `__delitem__`: del obj[key]
- `__contains__`: in
- `__iter__`: for 循环
- `__reversed__`: reversed()

### 可调用对象
- `__call__`: obj()

### 上下文管理
- `__enter__`: with 语句进入
- `__exit__`: with 语句退出

### 描述符
- `__get__`: 获取描述符
- `__set__`: 设置描述符
- `__delete__`: 删除描述符

## 最佳实践

### 1. 返回合适的值
- 比较运算符：返回 True/False 或 NotImplemented
- 算术运算符：返回新对象（或 self 用于增强赋值）
- 容器方法：抛出合适的异常（IndexError, KeyError）

### 2. 保持一致性
- 实现 `__eq__` 时考虑实现 `__hash__`
- 实现一个比较运算符时，考虑使用 `@total_ordering`
- `__str__` 应该简洁，`__repr__` 应该明确

### 3. 性能考虑
- 不要在 `__getattribute__` 中做耗时操作
- 使用 `__slots__` 减少内存占用
- 缓存计算结果（使用 `@cached_property`）

### 4. 安全性
- 不要在魔法方法中抛出意外的异常
- 验证输入参数
- 返回 NotImplemented 而不是 False

## 相关资源

- [Python 数据模型文档](https://docs.python.org/3/reference/datamodel.html)
- [Python 特殊方法名称](https://docs.python.org/3/reference/datamodel.html#special-method-names)
- [Fluent Python](https://www.oreilly.com/library/view/fluent-python/9781491946237/) - 第1章和第2章

## 待补充的主题

- [ ] `__call__` - 可调用对象
- [ ] `__enter__`/`__exit__` - 上下文管理器
- [ ] `__getattr__`/`__setattr__` - 属性拦截
- [ ] `__slots__` - 内存优化
- [ ] 描述符协议
- [ ] 元类和 `__new__`
- [ ] `__init_subclass__` - 子类初始化

欢迎贡献新的示例！
