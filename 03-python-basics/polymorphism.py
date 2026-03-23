"""
Python 多态（Polymorphism）详解

多态是面向对象编程的三大特性之一（封装、继承、多态）
允许不同类的对象对同一消息做出响应，但表现出不同的行为
"""

# ============================================================
# 案例 1: 多态基础 - 同一接口，不同实现
# ============================================================
print("=" * 60)
print("案例 1: 多态基础")
print("=" * 60)

class Animal:
    """动物基类"""
    def speak(self):
        """所有动物都会发声"""
        pass

class Dog(Animal):
    """狗"""
    def speak(self):
        return "汪汪汪！🐕"

class Cat(Animal):
    """猫"""
    def speak(self):
        return "喵喵喵！🐱"

class Duck(Animal):
    """鸭子"""
    def speak(self):
        return "嘎嘎嘎！🦆"

# 多态的使用：同一个接口，不同的实现
def animal_sound(animal: Animal):
    """接受任何 Animal 类型的对象"""
    print(f"  动物说：{animal.speak()}")

print("多态演示：")
dog = Dog()
cat = Cat()
duck = Duck()

animal_sound(dog)   # 调用 Dog 的 speak()
animal_sound(cat)   # 调用 Cat 的 speak()
animal_sound(duck)  # 调用 Duck 的 speak()

# 用列表演示
print("\n遍历不同的动物：")
animals = [Dog(), Cat(), Duck(), Dog(), Cat()]
for animal in animals:
    animal_sound(animal)


# ============================================================
# 案例 2: 鸭子类型（Duck Typing）
# ============================================================
print("\n" + "=" * 60)
print("案例 2: 鸭子类型 - Python 的多态特色")
print("=" * 60)

# "如果它走起来像鸭子，叫起来像鸭子，那它就是鸭子"
# Python 不要求继承，只要有相同的方法即可

print("核心理念：只看行为，不看类型\n")

class Bird:
    """不继承 Animal，但有 speak 方法"""
    def speak(self):
        return "叽叽喳喳！🐦"

class Robot:
    """机器人，也不继承 Animal"""
    def speak(self):
        return "Hello, I am a robot! 🤖"

class Car:
    """汽车，有 speak 方法（虽然不太合理）"""
    def speak(self):
        return "嘟嘟嘟！🚗"

print("鸭子类型演示（不需要继承）：")
# 只要有 speak() 方法就可以
things = [Bird(), Robot(), Car()]
for thing in things:
    animal_sound(thing)  # 同样可以调用

print("\n关键点：")
print("  ✅ Bird、Robot、Car 都没有继承 Animal")
print("  ✅ 但它们都有 speak() 方法")
print("  ✅ 所以可以在 animal_sound() 中使用")
print("  ✅ Python 只关心对象有没有需要的方法，不关心类型")


# ============================================================
# 案例 3: 运算符多态
# ============================================================
print("\n" + "=" * 60)
print("案例 3: 运算符多态")
print("=" * 60)

# + 运算符对不同类型有不同行为
print("+ 运算符的多态：")
print(f"  整数相加: 1 + 2 = {1 + 2}")
print(f"  字符串拼接: 'Hello' + ' World' = {'Hello' + ' World'}")
print(f"  列表合并: [1, 2] + [3, 4] = {[1, 2] + [3, 4]}")

# 自定义类的运算符重载
class Vector:
    """向量类"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        """重载 + 运算符"""
        return Vector(self.x + other.x, self.y + other.y)
    
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

print("\n自定义类的运算符多态：")
v1 = Vector(1, 2)
v2 = Vector(3, 4)
v3 = v1 + v2  # 调用 __add__
print(f"  {v1} + {v2} = {v3}")


# ============================================================
# 案例 4: 方法重写（Override）
# ============================================================
print("\n" + "=" * 60)
print("案例 4: 方法重写")
print("=" * 60)

class Shape:
    """图形基类"""
    def __init__(self, name):
        self.name = name
    
    def area(self):
        """计算面积（基类提供默认实现）"""
        return 0
    
    def describe(self):
        """描述图形"""
        return f"{self.name}，面积：{self.area():.2f}"

class Rectangle(Shape):
    """矩形"""
    def __init__(self, width, height):
        super().__init__("矩形")
        self.width = width
        self.height = height
    
    def area(self):
        """重写 area 方法"""
        return self.width * self.height

class Circle(Shape):
    """圆形"""
    def __init__(self, radius):
        super().__init__("圆形")
        self.radius = radius
    
    def area(self):
        """重写 area 方法"""
        import math
        return math.pi * self.radius ** 2

class Triangle(Shape):
    """三角形"""
    def __init__(self, base, height):
        super().__init__("三角形")
        self.base = base
        self.height = height
    
    def area(self):
        """重写 area 方法"""
        return 0.5 * self.base * self.height

print("方法重写演示：")
shapes = [
    Rectangle(4, 5),
    Circle(3),
    Triangle(6, 4)
]

for shape in shapes:
    print(f"  {shape.describe()}")


# ============================================================
# 案例 5: 抽象基类（ABC）
# ============================================================
print("\n" + "=" * 60)
print("案例 5: 抽象基类 - 强制子类实现方法")
print("=" * 60)

from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    """支付方式抽象基类"""
    
    @abstractmethod
    def pay(self, amount: float) -> str:
        """抽象方法：必须由子类实现"""
        pass
    
    @abstractmethod
    def refund(self, amount: float) -> str:
        """抽象方法：退款"""
        pass

class CreditCard(PaymentMethod):
    """信用卡支付"""
    def __init__(self, card_number: str):
        self.card_number = card_number[-4:]  # 只保留后4位
    
    def pay(self, amount: float) -> str:
        return f"信用卡 ****{self.card_number} 支付 ¥{amount:.2f}"
    
    def refund(self, amount: float) -> str:
        return f"信用卡 ****{self.card_number} 退款 ¥{amount:.2f}"

class Alipay(PaymentMethod):
    """支付宝"""
    def __init__(self, account: str):
        self.account = account
    
    def pay(self, amount: float) -> str:
        return f"支付宝账户 {self.account} 支付 ¥{amount:.2f}"
    
    def refund(self, amount: float) -> str:
        return f"支付宝账户 {self.account} 退款 ¥{amount:.2f}"

class WechatPay(PaymentMethod):
    """微信支付"""
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    def pay(self, amount: float) -> str:
        return f"微信用户 {self.user_id} 支付 ¥{amount:.2f}"
    
    def refund(self, amount: float) -> str:
        return f"微信用户 {self.user_id} 退款 ¥{amount:.2f}"

def process_payment(payment: PaymentMethod, amount: float):
    """处理支付（多态）"""
    print(f"  → {payment.pay(amount)}")

print("抽象基类演示：")
credit = CreditCard("1234567890123456")
alipay = Alipay("user@example.com")
wechat = WechatPay("wx_12345")

process_payment(credit, 100.00)
process_payment(alipay, 200.50)
process_payment(wechat, 50.75)

# 尝试创建抽象类实例会报错
print("\n尝试创建抽象类实例：")
try:
    payment = PaymentMethod()  # ❌ 不能实例化抽象类
except TypeError as e:
    print(f"  ❌ 错误: {e}")


# ============================================================
# 案例 6: 接口隔离 - Protocol（Python 3.8+）
# ============================================================
print("\n" + "=" * 60)
print("案例 6: Protocol - 更灵活的接口定义")
print("=" * 60)

from typing import Protocol

class Flyable(Protocol):
    """可飞行的协议（不需要显式继承）"""
    def fly(self) -> str:
        ...

class Airplane:
    """飞机"""
    def fly(self) -> str:
        return "飞机在天空中飞行 ✈️"

class Helicopter:
    """直升机"""
    def fly(self) -> str:
        return "直升机在盘旋 🚁"

class Superman:
    """超人（不是交通工具，但能飞）"""
    def fly(self) -> str:
        return "超人在天空中飞翔 🦸"

def make_it_fly(obj: Flyable):
    """让对象飞起来"""
    print(f"  {obj.fly()}")

print("Protocol 演示（结构化子类型）：")
airplane = Airplane()
helicopter = Helicopter()
superman = Superman()

make_it_fly(airplane)
make_it_fly(helicopter)
make_it_fly(superman)


# ============================================================
# 案例 7: 多态在设计模式中的应用 - 策略模式
# ============================================================
print("\n" + "=" * 60)
print("案例 7: 策略模式 - 多态的实际应用")
print("=" * 60)

class DiscountStrategy(ABC):
    """折扣策略抽象基类"""
    @abstractmethod
    def calculate(self, amount: float) -> float:
        """计算折扣后的价格"""
        pass

class NoDiscount(DiscountStrategy):
    """无折扣"""
    def calculate(self, amount: float) -> float:
        return amount

class PercentageDiscount(DiscountStrategy):
    """百分比折扣"""
    def __init__(self, percentage: float):
        self.percentage = percentage
    
    def calculate(self, amount: float) -> float:
        return amount * (1 - self.percentage / 100)

class FixedDiscount(DiscountStrategy):
    """固定金额折扣"""
    def __init__(self, discount: float):
        self.discount = discount
    
    def calculate(self, amount: float) -> float:
        return max(0, amount - self.discount)

class VIPDiscount(DiscountStrategy):
    """VIP 折扣（阶梯折扣）"""
    def calculate(self, amount: float) -> float:
        if amount >= 1000:
            return amount * 0.7  # 7折
        elif amount >= 500:
            return amount * 0.8  # 8折
        elif amount >= 200:
            return amount * 0.9  # 9折
        return amount

class Order:
    """订单类"""
    def __init__(self, amount: float, strategy: DiscountStrategy):
        self.amount = amount
        self.strategy = strategy
    
    def get_final_price(self) -> float:
        """获取最终价格"""
        return self.strategy.calculate(self.amount)

print("策略模式演示：")
original_price = 500.0

strategies = {
    "无折扣": NoDiscount(),
    "10%折扣": PercentageDiscount(10),
    "减50元": FixedDiscount(50),
    "VIP折扣": VIPDiscount()
}

for name, strategy in strategies.items():
    order = Order(original_price, strategy)
    final_price = order.get_final_price()
    print(f"  {name}: ¥{original_price:.2f} → ¥{final_price:.2f}")


# ============================================================
# 案例 8: 方法不可重写（Python 的实现方式）
# ============================================================
print("\n" + "=" * 60)
print("案例 8: 防止方法被重写")
print("=" * 60)

class Parent:
    """父类"""
    def __final_method(self):
        """双下划线：触发名称改写（Name Mangling）"""
        print("  → 父类的核心方法，无法被重写")
    
    def call_final(self):
        """公共方法调用私有方法"""
        self.__final_method()

class Child(Parent):
    """子类"""
    def __final_method(self):
        """子类尝试重写，但实际创建的是 _Child__final_method"""
        print("  → 子类试图重写（不会生效）")

print("名称改写演示：")
child = Child()
child.call_final()  # 调用父类的 __final_method

print("\n子类的方法是独立的：")
child._Child__final_method()  # 显式调用子类的版本

print("\n查看实际的方法名：")
print(f"  父类方法: {[m for m in dir(Parent) if 'final' in m]}")
print(f"  子类方法: {[m for m in dir(Child) if 'final' in m]}")


# ============================================================
# 案例 9: 多态与类型检查
# ============================================================
print("\n" + "=" * 60)
print("案例 9: 多态与类型检查")
print("=" * 60)

class Vehicle:
    """交通工具基类"""
    def move(self):
        return "移动"

class Car(Vehicle):
    """汽车"""
    def move(self):
        return "汽车在路上行驶"

class Boat(Vehicle):
    """船"""
    def move(self):
        return "船在水上航行"

def transport(vehicle: Vehicle):
    """运输（类型提示）"""
    print(f"  {vehicle.move()}")

print("类型检查：")
car = Car()
boat = Boat()

# isinstance 检查
print(f"car 是 Vehicle? {isinstance(car, Vehicle)}")
print(f"car 是 Car? {isinstance(car, Car)}")
print(f"boat 是 Vehicle? {isinstance(boat, Vehicle)}")

# issubclass 检查
print(f"Car 是 Vehicle 的子类? {issubclass(Car, Vehicle)}")
print(f"Boat 是 Vehicle 的子类? {issubclass(Boat, Vehicle)}")


# ============================================================
# 案例 10: 实战示例 - 日志系统
# ============================================================
print("\n" + "=" * 60)
print("案例 10: 实战 - 多态的日志系统")
print("=" * 60)

from datetime import datetime

class Logger(ABC):
    """日志记录器抽象基类"""
    @abstractmethod
    def log(self, level: str, message: str):
        """记录日志"""
        pass

class ConsoleLogger(Logger):
    """控制台日志"""
    def log(self, level: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

class FileLogger(Logger):
    """文件日志"""
    def __init__(self, filename: str):
        self.filename = filename
    
    def log(self, level: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 实际应该写入文件，这里只演示
        print(f"→ 写入文件 {self.filename}: [{timestamp}] [{level}] {message}")

class DatabaseLogger(Logger):
    """数据库日志"""
    def __init__(self, db_name: str):
        self.db_name = db_name
    
    def log(self, level: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 实际应该写入数据库，这里只演示
        print(f"→ 写入数据库 {self.db_name}: [{timestamp}] [{level}] {message}")

class Application:
    """应用程序"""
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def run(self):
        """运行应用"""
        self.logger.log("INFO", "应用程序启动")
        self.logger.log("DEBUG", "正在处理数据...")
        self.logger.log("ERROR", "发生错误！")

print("日志系统演示：")
print("\n1. 使用控制台日志:")
app1 = Application(ConsoleLogger())
app1.run()

print("\n2. 使用文件日志:")
app2 = Application(FileLogger("app.log"))
app2.run()

print("\n3. 使用数据库日志:")
app3 = Application(DatabaseLogger("logs_db"))
app3.run()


# ============================================================
# 总结
# ============================================================
print("\n" + "=" * 60)
print("多态总结")
print("=" * 60)
print("""
📌 多态的核心概念:
- 同一接口，不同实现
- 父类引用指向子类对象
- 方法重写（Override）
- 运行时动态绑定

✅ Python 实现多态的方式:
1. 继承 + 方法重写
2. 鸭子类型（Duck Typing）
3. 抽象基类（ABC）
4. Protocol（结构化子类型）

🎯 多态的优势:
1. 提高代码的灵活性和可扩展性
2. 降低代码耦合度
3. 符合开闭原则（对扩展开放，对修改关闭）
4. 便于代码复用

💡 使用场景:
- 设计模式（策略、工厂、模板方法等）
- 插件系统
- 框架设计
- API 接口设计
- 数据库抽象层
- 日志系统
- 支付系统

⚠️  注意事项:
1. Python 是动态类型，不强制类型检查
2. 使用鸭子类型时要注意方法签名一致性
3. 抽象基类用于强制子类实现特定方法
4. Protocol 更灵活，不需要显式继承
5. 双下划线方法会触发名称改写（不是真正的 private）

🔑 关键概念:
- 继承（Inheritance）：is-a 关系
- 组合（Composition）：has-a 关系
- 接口（Interface）：can-do 关系
- 多态（Polymorphism）：不同对象响应相同消息

📚 相关术语:
- Override（重写）：子类重新定义父类方法
- Overload（重载）：同名方法不同参数（Python不直接支持）
- Duck Typing：鸭子类型，只关心行为不关心类型
- EAFP：宁可请求原谅，也不请求许可（Pythonic）
- LBYL：三思而后行（非 Pythonic）
""")