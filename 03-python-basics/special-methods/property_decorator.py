"""
@property 装饰器详解

@property 将方法转换为属性，提供更优雅的 getter/setter 访问方式
"""

# ============================================================
# 案例 1: 基础使用 - 只读属性
# ============================================================
print("=" * 60)
print("案例 1: 基础使用 - 只读属性")
print("=" * 60)

from pydantic import BaseModel, Field
import math

class Circle:
    """圆形类 - 演示只读属性"""
    
    def __init__(self, radius: float):
        self._radius = radius  # 私有属性
    
    @property
    def radius(self) -> float:
        """半径属性（只读）"""
        return self._radius
    
    @property
    def diameter(self) -> float:
        """直径属性（计算得出）"""
        return self._radius * 2
    
    @property
    def area(self) -> float:
        """面积属性（计算得出）"""
        import math
        return math.pi * self._radius ** 2
    
    @property
    def circumference(self) -> float:
        """周长属性（计算得出）"""
        import math
        return 2 * math.pi * self._radius

# 使用示例
circle = Circle(5)
print(f"半径: {circle.radius}")  # 像访问属性一样
print(f"直径: {circle.diameter:.2f}")
print(f"面积: {circle.area:.2f}")
print(f"周长: {circle.circumference:.2f}")

# 尝试修改只读属性会报错
try:
    circle.radius = 10
except AttributeError as e:
    print(f"\n❌ 不能设置只读属性: {e}")


# ============================================================
# 案例 2: 完整的 getter/setter/deleter
# ============================================================
print("\n" + "=" * 60)
print("案例 2: 完整的 getter/setter/deleter")
print("=" * 60)

class Temperature:
    """温度类 - 演示完整的属性控制"""
    
    def __init__(self, celsius: float):
        self._celsius = celsius
    
    @property
    def celsius(self) -> float:
        """摄氏度 getter"""
        print("  → 获取摄氏度")
        return self._celsius
    
    @celsius.setter
    def celsius(self, value: float):
        """摄氏度 setter - 带验证"""
        print(f"  → 设置摄氏度为 {value}")
        if value < -273.15:
            raise ValueError("温度不能低于绝对零度（-273.15°C）")
        self._celsius = value
    
    @celsius.deleter
    def celsius(self):
        """摄氏度 deleter"""
        print("  → 删除温度数据")
        del self._celsius
    
    @property
    def fahrenheit(self) -> float:
        """华氏度（自动转换）"""
        return self._celsius * 9/5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value: float):
        """通过华氏度设置温度"""
        self._celsius = (value - 32) * 5/9
    
    @property
    def kelvin(self) -> float:
        """开尔文（自动转换）"""
        return self._celsius + 273.15

# 使用示例
temp = Temperature(25)
print(f"当前温度: {temp.celsius}°C")
print(f"华氏度: {temp.fahrenheit:.2f}°F")
print(f"开尔文: {temp.kelvin:.2f}K")

print("\n修改温度:")
temp.celsius = 30
print(f"新温度: {temp.celsius}°C")

print("\n通过华氏度设置:")
temp.fahrenheit = 86
print(f"温度: {temp.celsius:.2f}°C")

# 验证温度范围
try:
    temp.celsius = -300
except ValueError as e:
    print(f"\n❌ 验证失败: {e}")

# 删除属性
print("\n删除温度:")
del temp.celsius


# ============================================================
# 案例 3: 惰性求值（Lazy Evaluation）
# ============================================================
print("\n" + "=" * 60)
print("案例 3: 惰性求值 - 缓存计算结果")
print("=" * 60)

class DataAnalyzer:
    """数据分析器 - 演示惰性计算和缓存"""
    
    def __init__(self, data: list):
        self.data = data
        self._mean = None  # 缓存均值
        self._std = None   # 缓存标准差
    
    @property
    def mean(self) -> float:
        """均值（首次计算后缓存）"""
        if self._mean is None:
            print("  → 计算均值（耗时操作）...")
            self._mean = sum(self.data) / len(self.data)
        else:
            print("  → 使用缓存的均值")
        return self._mean
    
    @property
    def std(self) -> float:
        """标准差（首次计算后缓存）"""
        if self._std is None:
            print("  → 计算标准差（耗时操作）...")
            mean = self.mean
            variance = sum((x - mean) ** 2 for x in self.data) / len(self.data)
            self._std = variance ** 0.5
        else:
            print("  → 使用缓存的标准差")
        return self._std
    
    def add_data(self, value: float):
        """添加数据时清除缓存"""
        self.data.append(value)
        self._mean = None  # 清除缓存
        self._std = None

# 使用示例
analyzer = DataAnalyzer([1, 2, 3, 4, 5])

print("第一次访问 mean:")
print(f"均值 = {analyzer.mean}")

print("\n第二次访问 mean（使用缓存）:")
print(f"均值 = {analyzer.mean}")

print("\n第一次访问 std:")
print(f"标准差 = {analyzer.std:.2f}")

print("\n添加新数据:")
analyzer.add_data(6)
print("再次访问 mean（缓存已清除）:")
print(f"均值 = {analyzer.mean}")


# ============================================================
# 案例 4: 数据验证和转换
# ============================================================
print("\n" + "=" * 60)
print("案例 4: 数据验证和转换")
print("=" * 60)

class Person:
    """人员类 - 演示数据验证和转换"""
    
    def __init__(self, name: str, age: int, email: str):
        self.name = name
        self.age = age
        self.email = email
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str):
        """姓名验证和转换"""
        if not isinstance(value, str):
            raise TypeError("姓名必须是字符串")
        value = value.strip()  # 去除空格
        if not value:
            raise ValueError("姓名不能为空")
        if len(value) > 50:
            raise ValueError("姓名长度不能超过50个字符")
        self._name = value.title()  # 转换为标题格式
    
    @property
    def age(self) -> int:
        return self._age
    
    @age.setter
    def age(self, value: int):
        """年龄验证"""
        if not isinstance(value, int):
            # 尝试转换
            try:
                value = int(value)
            except (ValueError, TypeError):
                raise TypeError("年龄必须是整数")
        if value < 0:
            raise ValueError("年龄不能为负数")
        if value > 150:
            raise ValueError("年龄不能超过150")
        self._age = value
    
    @property
    def email(self) -> str:
        return self._email
    
    @email.setter
    def email(self, value: str):
        """邮箱验证"""
        if not isinstance(value, str):
            raise TypeError("邮箱必须是字符串")
        value = value.strip().lower()  # 转换为小写
        if "@" not in value or "." not in value.split("@")[1]:
            raise ValueError("邮箱格式无效")
        self._email = value
    
    @property
    def is_adult(self) -> bool:
        """是否成年（只读）"""
        return self._age >= 18

# 使用示例
person = Person("  john doe  ", "25", "John.Doe@Example.Com")
print(f"姓名: {person.name}")  # 自动转换为 "John Doe"
print(f"年龄: {person.age}")    # 自动转换为 int
print(f"邮箱: {person.email}")  # 自动转换为小写
print(f"是否成年: {person.is_adult}")

# 验证失败示例
print("\n验证测试:")
try:
    person.name = ""
except ValueError as e:
    print(f"❌ {e}")

try:
    person.age = 200
except ValueError as e:
    print(f"❌ {e}")

try:
    person.email = "invalid-email"
except ValueError as e:
    print(f"❌ {e}")


# ============================================================
# 案例 5: 私有属性保护
# ============================================================
print("\n" + "=" * 60)
print("案例 5: 私有属性保护")
print("=" * 60)

class BankAccount:
    """银行账户 - 演示私有属性保护"""
    
    def __init__(self, account_number: str, initial_balance: float):
        self._account_number = account_number
        self._balance = initial_balance
        self._transaction_history = []
    
    @property
    def account_number(self) -> str:
        """账号（只读，隐藏部分）"""
        # 只显示后4位，其他用 * 代替
        return "*" * (len(self._account_number) - 4) + self._account_number[-4:]
    
    @property
    def balance(self) -> float:
        """余额（只读）"""
        return self._balance
    
    def deposit(self, amount: float):
        """存款"""
        if amount <= 0:
            raise ValueError("存款金额必须大于0")
        self._balance += amount
        self._transaction_history.append(f"存款: +{amount}")
        print(f"✅ 存款成功: {amount}")
    
    def withdraw(self, amount: float):
        """取款"""
        if amount <= 0:
            raise ValueError("取款金额必须大于0")
        if amount > self._balance:
            raise ValueError("余额不足")
        self._balance -= amount
        self._transaction_history.append(f"取款: -{amount}")
        print(f"✅ 取款成功: {amount}")
    
    @property
    def transaction_count(self) -> int:
        """交易次数"""
        return len(self._transaction_history)

# 使用示例
account = BankAccount("1234567890", 1000)
print(f"账号: {account.account_number}")  # 显示 ******7890
print(f"余额: ¥{account.balance:.2f}")

account.deposit(500)
print(f"余额: ¥{account.balance:.2f}")

account.withdraw(300)
print(f"余额: ¥{account.balance:.2f}")
print(f"交易次数: {account.transaction_count}")

# 尝试直接修改余额（受保护）
try:
    account.balance = 10000
except AttributeError as e:
    print(f"\n❌ 不能直接修改余额: {type(e).__name__}")


# ============================================================
# 案例 6: 依赖属性（Dependent Properties）
# ============================================================
print("\n" + "=" * 60)
print("案例 6: 依赖属性")
print("=" * 60)

class Rectangle:
    """矩形类 - 演示相互依赖的属性"""
    
    def __init__(self, width: float, height: float):
        self._width = width
        self._height = height
    
    @property
    def width(self) -> float:
        return self._width
    
    @width.setter
    def width(self, value: float):
        if value <= 0:
            raise ValueError("宽度必须大于0")
        self._width = value
    
    @property
    def height(self) -> float:
        return self._height
    
    @height.setter
    def height(self, value: float):
        if value <= 0:
            raise ValueError("高度必须大于0")
        self._height = value
    
    @property
    def area(self) -> float:
        """面积（依赖宽度和高度）"""
        return self._width * self._height
    
    @property
    def perimeter(self) -> float:
        """周长（依赖宽度和高度）"""
        return 2 * (self._width + self._height)
    
    @property
    def diagonal(self) -> float:
        """对角线长度（依赖宽度和高度）"""
        return (self._width ** 2 + self._height ** 2) ** 0.5
    
    @property
    def is_square(self) -> bool:
        """是否为正方形"""
        return self._width == self._height

# 使用示例
rect = Rectangle(4, 5)
print(f"宽度: {rect.width}, 高度: {rect.height}")
print(f"面积: {rect.area}")
print(f"周长: {rect.perimeter}")
print(f"对角线: {rect.diagonal:.2f}")
print(f"是否为正方形: {rect.is_square}")

print("\n修改宽度:")
rect.width = 5
print(f"是否为正方形: {rect.is_square}")
print(f"新面积: {rect.area}")


# ============================================================
# 总结
# ============================================================
print("\n" + "=" * 60)
print("@property 使用总结")
print("=" * 60)
print("""
✅ 优点:
1. 提供类似属性的访问方式，更加 Pythonic
2. 可以添加验证逻辑，保护数据完整性
3. 支持计算属性，延迟计算
4. 可以缓存结果，提高性能
5. 保持 API 的向后兼容性

📌 使用场景:
1. 需要验证或转换输入数据
2. 计算派生属性
3. 保护内部状态
4. 惰性求值和缓存
5. 提供只读访问
6. 维护属性间的一致性

⚠️  注意事项:
1. getter 应该是轻量级的，避免耗时操作
2. setter 中的验证应该清晰明确
3. 不要在 property 中产生副作用
4. 考虑使用 @functools.cached_property 进行缓存
""")