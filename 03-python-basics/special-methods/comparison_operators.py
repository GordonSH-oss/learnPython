"""
比较运算符魔法方法详解

__eq__, __lt__, __le__, __gt__, __ge__, __ne__
"""

from functools import total_ordering

# ============================================================
# 案例 1: 基础比较 - __eq__ 和 __ne__
# ============================================================
print("=" * 60)
print("案例 1: 基础比较 - 相等性判断")
print("=" * 60)

class Point:
    """点类 - 实现相等性比较"""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __eq__(self, other) -> bool:
        """相等比较 =="""
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y
    
    def __ne__(self, other) -> bool:
        """不等比较 !=（可选，Python 3+ 会自动基于 __eq__ 生成）"""
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result
    
    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

p1 = Point(3, 4)
p2 = Point(3, 4)
p3 = Point(5, 6)

print(f"p1 = {p1}")
print(f"p2 = {p2}")
print(f"p3 = {p3}")
print(f"\np1 == p2: {p1 == p2}")  # True
print(f"p1 == p3: {p1 == p3}")    # False
print(f"p1 != p3: {p1 != p3}")    # True


# ============================================================
# 案例 2: 完整的比较运算符
# ============================================================
print("\n" + "=" * 60)
print("案例 2: 完整的比较运算符")
print("=" * 60)

class Version:
    """版本号类 - 实现所有比较运算符"""
    
    def __init__(self, major: int, minor: int, patch: int):
        self.major = major
        self.minor = minor
        self.patch = patch
    
    def _as_tuple(self):
        """转换为元组便于比较"""
        return (self.major, self.minor, self.patch)
    
    def __eq__(self, other) -> bool:
        """=="""
        if not isinstance(other, Version):
            return NotImplemented
        return self._as_tuple() == other._as_tuple()
    
    def __lt__(self, other) -> bool:
        """<"""
        if not isinstance(other, Version):
            return NotImplemented
        return self._as_tuple() < other._as_tuple()
    
    def __le__(self, other) -> bool:
        """<="""
        if not isinstance(other, Version):
            return NotImplemented
        return self._as_tuple() <= other._as_tuple()
    
    def __gt__(self, other) -> bool:
        """>"""
        if not isinstance(other, Version):
            return NotImplemented
        return self._as_tuple() > other._as_tuple()
    
    def __ge__(self, other) -> bool:
        """>="""
        if not isinstance(other, Version):
            return NotImplemented
        return self._as_tuple() >= other._as_tuple()
    
    def __repr__(self) -> str:
        return f"Version({self.major}.{self.minor}.{self.patch})"

v1 = Version(1, 0, 0)
v2 = Version(1, 2, 3)
v3 = Version(2, 0, 0)

print(f"v1 = {v1}, v2 = {v2}, v3 = {v3}")
print(f"\nv1 < v2:  {v1 < v2}")   # True
print(f"v2 < v3:  {v2 < v3}")     # True
print(f"v1 <= v2: {v1 <= v2}")    # True
print(f"v3 > v2:  {v3 > v2}")     # True
print(f"v3 >= v2: {v3 >= v2}")    # True
print(f"v1 == v1: {v1 == v1}")    # True

# 排序
versions = [v3, v1, v2]
print(f"\n排序前: {versions}")
versions.sort()
print(f"排序后: {versions}")


# ============================================================
# 案例 3: 使用 @total_ordering 装饰器简化
# ============================================================
print("\n" + "=" * 60)
print("案例 3: 使用 @total_ordering 简化")
print("=" * 60)

@total_ordering
class Student:
    """学生类 - 只需实现 __eq__ 和一个比较运算符"""
    
    def __init__(self, name: str, score: int):
        self.name = name
        self.score = score
    
    def __eq__(self, other) -> bool:
        """必须实现"""
        if not isinstance(other, Student):
            return NotImplemented
        return self.score == other.score
    
    def __lt__(self, other) -> bool:
        """只需实现一个比较运算符，其他的会自动生成"""
        if not isinstance(other, Student):
            return NotImplemented
        return self.score < other.score
    
    def __repr__(self) -> str:
        return f"Student('{self.name}', {self.score})"

s1 = Student("张三", 85)
s2 = Student("李四", 90)
s3 = Student("王五", 85)

print(f"s1 = {s1}")
print(f"s2 = {s2}")
print(f"s3 = {s3}")

print(f"\ns1 < s2:  {s1 < s2}")   # True
print(f"s1 <= s2: {s1 <= s2}")    # True（自动生成）
print(f"s2 > s1:  {s2 > s1}")     # True（自动生成）
print(f"s2 >= s1: {s2 >= s1}")    # True（自动生成）
print(f"s1 == s3: {s1 == s3}")    # True

students = [s2, s1, s3]
print(f"\n排序前: {students}")
students.sort()
print(f"排序后: {students}")


# ============================================================
# 案例 4: 复杂对象的比较
# ============================================================
print("\n" + "=" * 60)
print("案例 4: 复杂对象的比较")
print("=" * 60)

@total_ordering
class Employee:
    """员工类 - 多字段比较"""
    
    def __init__(self, name: str, department: str, salary: int, hire_date: str):
        self.name = name
        self.department = department
        self.salary = salary
        self.hire_date = hire_date
    
    def _comparison_key(self):
        """定义比较的关键字段和顺序"""
        return (self.department, -self.salary, self.hire_date)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Employee):
            return NotImplemented
        return self._comparison_key() == other._comparison_key()
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, Employee):
            return NotImplemented
        return self._comparison_key() < other._comparison_key()
    
    def __repr__(self) -> str:
        return f"Employee('{self.name}', '{self.department}', {self.salary})"

employees = [
    Employee("张三", "技术部", 15000, "2020-01-01"),
    Employee("李四", "技术部", 20000, "2019-06-15"),
    Employee("王五", "销售部", 12000, "2021-03-20"),
    Employee("赵六", "技术部", 15000, "2019-08-10"),
]

print("排序前:")
for emp in employees:
    print(f"  {emp}")

employees.sort()
print("\n排序后（按部门、薪资降序、入职日期）:")
for emp in employees:
    print(f"  {emp}")


# ============================================================
# 案例 5: 与其他类型的比较
# ============================================================
print("\n" + "=" * 60)
print("案例 5: 与其他类型的比较")
print("=" * 60)

class Money:
    """货币类 - 可以与数字比较"""
    
    def __init__(self, amount: float):
        self.amount = amount
    
    def __eq__(self, other) -> bool:
        """支持与 Money 或数字比较"""
        if isinstance(other, Money):
            return self.amount == other.amount
        elif isinstance(other, (int, float)):
            return self.amount == other
        return NotImplemented
    
    def __lt__(self, other) -> bool:
        """支持与 Money 或数字比较"""
        if isinstance(other, Money):
            return self.amount < other.amount
        elif isinstance(other, (int, float)):
            return self.amount < other
        return NotImplemented
    
    def __gt__(self, other) -> bool:
        """> 支持与 Money 或数字比较"""
        if isinstance(other, Money):
            return self.amount > other.amount
        elif isinstance(other, (int, float)):
            return self.amount > other
        return NotImplemented
    
    def __repr__(self) -> str:
        return f"Money({self.amount})"

m1 = Money(100)
m2 = Money(200)

print(f"m1 = {m1}, m2 = {m2}")
print(f"\nm1 == 100:    {m1 == 100}")      # True
print(f"m1 < m2:      {m1 < m2}")          # True
print(f"m1 < 150:     {m1 < 150}")         # True
print(f"m2 > 150:     {m2 > 150}")         # True


# ============================================================
# 案例 6: 不可比较的对象
# ============================================================
print("\n" + "=" * 60)
print("案例 6: 返回 NotImplemented")
print("=" * 60)

class Apple:
    """苹果类"""
    
    def __init__(self, weight: float):
        self.weight = weight
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Apple):
            return NotImplemented  # 不是苹果，无法比较
        return self.weight == other.weight
    
    def __repr__(self) -> str:
        return f"Apple({self.weight}g)"

class Orange:
    """橙子类"""
    
    def __init__(self, weight: float):
        self.weight = weight
    
    def __repr__(self) -> str:
        return f"Orange({self.weight}g)"

apple = Apple(150)
orange = Orange(150)

print(f"apple = {apple}")
print(f"orange = {orange}")
print(f"\napple == Orange(150): {apple == orange}")  # False（苹果和橙子无法比较）


# ============================================================
# 案例 7: 哈希和相等性
# ============================================================
print("\n" + "=" * 60)
print("案例 7: 实现 __hash__ 配合 __eq__")
print("=" * 60)

class ImmutablePoint:
    """不可变点类 - 可以作为字典键或集合元素"""
    
    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y
    
    @property
    def x(self) -> float:
        return self._x
    
    @property
    def y(self) -> float:
        return self._y
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, ImmutablePoint):
            return NotImplemented
        return self.x == other.x and self.y == other.y
    
    def __hash__(self) -> int:
        """必须与 __eq__ 保持一致"""
        return hash((self.x, self.y))
    
    def __repr__(self) -> str:
        return f"ImmutablePoint({self.x}, {self.y})"

p1 = ImmutablePoint(1, 2)
p2 = ImmutablePoint(1, 2)
p3 = ImmutablePoint(3, 4)

print(f"p1 = {p1}, p2 = {p2}, p3 = {p3}")
print(f"\np1 == p2: {p1 == p2}")
print(f"hash(p1) == hash(p2): {hash(p1) == hash(p2)}")

# 可以作为字典键
point_data = {
    p1: "点1",
    p3: "点3"
}
print(f"\n字典: {point_data}")
print(f"point_data[p2]: {point_data[p2]}")  # p2 和 p1 相等，可以找到

# 可以作为集合元素
point_set = {p1, p2, p3}  # p1 和 p2 会被去重
print(f"\n集合: {point_set}")
print(f"集合大小: {len(point_set)}")  # 2（p1 和 p2 相等）


# ============================================================
# 总结
# ============================================================
print("\n" + "=" * 60)
print("比较运算符总结")
print("=" * 60)
print("""
📌 六个比较运算符:
┌──────────┬─────────────┬───────────────────┐
│ 方法     │ 运算符      │ 说明              │
├──────────┼─────────────┼───────────────────┤
│ __eq__   │ x == y      │ 相等              │
│ __ne__   │ x != y      │ 不等（自动生成）  │
│ __lt__   │ x < y       │ 小于              │
│ __le__   │ x <= y      │ 小于等于          │
│ __gt__   │ x > y       │ 大于              │
│ __ge__   │ x >= y      │ 大于等于          │
└──────────┴─────────────┴───────────────────┘

✅ 最佳实践:
1. 总是检查 other 的类型，不兼容时返回 NotImplemented
2. 使用 @total_ordering 简化代码（只需实现 __eq__ 和一个比较运算符）
3. 如果实现了 __eq__，考虑是否需要实现 __hash__
4. 保持 __eq__ 和 __hash__ 的一致性
5. 不要在比较方法中抛出异常，应返回 NotImplemented

💡 使用场景:
- 排序: sort(), sorted(), min(), max()
- 集合操作: set, frozenset
- 字典键: dict (需要 __hash__)
- 条件判断: if, while
- 数据结构: 堆、优先队列等

⚠️  注意事项:
1. Python 3+ 中 __ne__ 会自动基于 __eq__ 生成
2. 返回 NotImplemented 而不是 False（让其他类型有机会处理）
3. 如果对象可变，不要实现 __hash__
4. __eq__ 返回 True 的对象，__hash__ 应该返回相同值
""")