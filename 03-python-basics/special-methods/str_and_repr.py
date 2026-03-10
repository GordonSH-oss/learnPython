"""
__str__ 和 __repr__ 魔法方法详解

这两个方法用于定义对象的字符串表示
"""

# ============================================================
# 案例 1: __str__ vs __repr__ 基础区别
# ============================================================
print("=" * 60)
print("案例 1: __str__ vs __repr__ 基础区别")
print("=" * 60)

class Point:
    """点类 - 演示基础区别"""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __str__(self) -> str:
        """用户友好的字符串表示（给终端用户看）"""
        return f"点({self.x}, {self.y})"
    
    def __repr__(self) -> str:
        """开发者友好的字符串表示（用于调试）"""
        return f"Point(x={self.x}, y={self.y})"

point = Point(3, 4)

print(f"str(point):  {str(point)}")    # 调用 __str__
print(f"repr(point): {repr(point)}")   # 调用 __repr__
print(f"print(point): ", end="")
print(point)                            # 默认调用 __str__

print("\n在容器中:")
points = [Point(1, 2), Point(3, 4)]
print(f"列表: {points}")  # 容器使用 __repr__


# ============================================================
# 案例 2: 只实现 __repr__
# ============================================================
print("\n" + "=" * 60)
print("案例 2: 只实现 __repr__（推荐）")
print("=" * 60)

class User:
    """用户类 - 只实现 __repr__"""
    
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email
    
    def __repr__(self) -> str:
        """如果没有 __str__，__repr__ 会被用作后备"""
        return f"User(username='{self.username}', email='{self.email}')"

user = User("zhangsan", "zhangsan@example.com")
print(f"str(user):  {str(user)}")   # 使用 __repr__
print(f"repr(user): {repr(user)}")  # 使用 __repr__


# ============================================================
# 案例 3: 可重建对象的 __repr__
# ============================================================
print("\n" + "=" * 60)
print("案例 3: 可重建对象的 __repr__")
print("=" * 60)

class Color:
    """颜色类 - __repr__ 返回可执行代码"""
    
    def __init__(self, r: int, g: int, b: int):
        self.r = r
        self.g = g
        self.b = b
    
    def __repr__(self) -> str:
        """返回能重建对象的表达式"""
        return f"Color(r={self.r}, g={self.g}, b={self.b})"
    
    def __str__(self) -> str:
        """返回用户友好的格式"""
        return f"RGB({self.r}, {self.g}, {self.b})"

color = Color(255, 128, 0)
print(f"用户看到: {color}")
print(f"开发者看到: {repr(color)}")

# 可以直接用 repr 的结果重建对象
print("\n重建对象:")
color_repr = repr(color)
print(f"repr 字符串: {color_repr}")
color_copy = eval(color_repr)  # 用 eval 执行字符串代码
print(f"重建的对象: {color_copy}")
print(f"是否相等: r={color.r == color_copy.r}, g={color.g == color_copy.g}, b={color.b == color_copy.b}")


# ============================================================
# 案例 4: 复杂对象的字符串表示
# ============================================================
print("\n" + "=" * 60)
print("案例 4: 复杂对象的字符串表示")
print("=" * 60)

class Book:
    """书籍类 - 复杂对象的格式化"""
    
    def __init__(self, title: str, author: str, year: int, pages: int):
        self.title = title
        self.author = author
        self.year = year
        self.pages = pages
    
    def __str__(self) -> str:
        """多行格式化输出"""
        return f"""
📚 《{self.title}》
   作者: {self.author}
   出版年份: {self.year}
   页数: {self.pages}
        """.strip()
    
    def __repr__(self) -> str:
        """简洁的开发者表示"""
        return f"Book('{self.title}', '{self.author}', {self.year}, {self.pages})"

book = Book("Python 编程", "张三", 2024, 500)
print("用户友好的格式:")
print(book)
print("\n开发者格式:")
print(repr(book))


# ============================================================
# 案例 5: 嵌套对象的表示
# ============================================================
print("\n" + "=" * 60)
print("案例 5: 嵌套对象的表示")
print("=" * 60)

class Address:
    """地址类"""
    
    def __init__(self, street: str, city: str):
        self.street = street
        self.city = city
    
    def __repr__(self) -> str:
        return f"Address('{self.street}', '{self.city}')"
    
    def __str__(self) -> str:
        return f"{self.city} {self.street}"

class Person:
    """人员类 - 包含嵌套对象"""
    
    def __init__(self, name: str, age: int, address: Address):
        self.name = name
        self.age = age
        self.address = address
    
    def __repr__(self) -> str:
        """注意：地址对象自动调用其 __repr__"""
        return f"Person(name='{self.name}', age={self.age}, address={self.address!r})"
    
    def __str__(self) -> str:
        """注意：地址对象自动调用其 __str__"""
        return f"{self.name}, {self.age}岁, 住在{self.address}"

address = Address("中关村大街1号", "北京")
person = Person("李四", 30, address)

print("用户友好:")
print(person)
print("\n开发者格式:")
print(repr(person))


# ============================================================
# 案例 6: 格式化字符串中的使用
# ============================================================
print("\n" + "=" * 60)
print("案例 6: f-string 中的 !s, !r, !a")
print("=" * 60)

class Product:
    """产品类"""
    
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price
    
    def __repr__(self) -> str:
        return f"Product(name='{self.name}', price={self.price})"
    
    def __str__(self) -> str:
        return f"{self.name} - ¥{self.price:.2f}"

product = Product("iPhone 15", 5999.00)

print(f"默认:     {product}")       # 使用 __str__
print(f"!s 转换: {product!s}")     # 显式使用 __str__
print(f"!r 转换: {product!r}")     # 显式使用 __repr__
print(f"!a 转换: {product!a}")     # 使用 ascii()，转义非 ASCII 字符


# ============================================================
# 案例 7: 调试时的最佳实践
# ============================================================
print("\n" + "=" * 60)
print("案例 7: 调试时的最佳实践")
print("=" * 60)

class Task:
    """任务类 - 调试友好的设计"""
    
    def __init__(self, title: str, status: str, priority: int):
        self.title = title
        self.status = status
        self.priority = priority
        self._internal_id = id(self)  # 内部 ID
    
    def __repr__(self) -> str:
        """包含所有关键信息，方便调试"""
        return (f"Task(title='{self.title}', status='{self.status}', "
                f"priority={self.priority}, id={self._internal_id})")
    
    def __str__(self) -> str:
        """简洁的用户表示"""
        status_emoji = "✅" if self.status == "完成" else "⏳"
        return f"{status_emoji} [{self.priority}] {self.title}"

tasks = [
    Task("修复 Bug #123", "进行中", 1),
    Task("编写文档", "完成", 2),
    Task("代码审查", "待处理", 3)
]

print("用户界面显示:")
for task in tasks:
    print(f"  {task}")

print("\n调试信息:")
for task in tasks:
    print(f"  {task!r}")


# ============================================================
# 案例 8: 没有实现这些方法时的默认行为
# ============================================================
print("\n" + "=" * 60)
print("案例 8: 默认行为")
print("=" * 60)

class DefaultClass:
    """没有实现 __str__ 或 __repr__ 的类"""
    
    def __init__(self, value):
        self.value = value

obj = DefaultClass(42)
print(f"默认的 str():  {str(obj)}")   # 输出类似 <__main__.DefaultClass object at 0x...>
print(f"默认的 repr(): {repr(obj)}")  # 相同的输出


# ============================================================
# 总结
# ============================================================
print("\n" + "=" * 60)
print("__str__ 和 __repr__ 总结")
print("=" * 60)
print("""
📌 核心区别:
┌─────────────┬──────────────────────┬────────────────────────┐
│             │ __str__              │ __repr__               │
├─────────────┼──────────────────────┼────────────────────────┤
│ 目标用户    │ 终端用户             │ 开发者                 │
│ 调用方式    │ str(), print()       │ repr(), 容器中显示     │
│ 目的        │ 可读性               │ 明确性、可调试         │
│ 格式        │ 人类友好             │ 机器友好（可重建对象） │
│ 是否必需    │ 可选                 │ 推荐                   │
│ 后备方案    │ 使用 __repr__        │ 使用默认实现           │
└─────────────┴──────────────────────┴────────────────────────┘

✅ 最佳实践:
1. 总是实现 __repr__，让它返回能重建对象的表达式
2. 只在需要特别友好的用户输出时才实现 __str__
3. __repr__ 应该尽可能明确，包含类名和关键参数
4. 避免在这些方法中抛出异常
5. 保持输出简洁，避免过长的字符串

💡 使用场景:
- __repr__: 日志记录、调试、开发者工具
- __str__: 用户界面、报告、友好输出

📝 格式化技巧:
- f"{obj}"      → 调用 __str__
- f"{obj!r}"    → 调用 __repr__
- f"{obj!s}"    → 显式调用 __str__
- f"{obj!a}"    → 调用 ascii(obj)
""")