"""
算术运算符魔法方法详解

__add__, __sub__, __mul__, __truediv__, __floordiv__, __mod__, __pow__
__radd__, __iadd__ 等
"""

# ============================================================
# 案例 1: 基础算术运算符
# ============================================================
print("=" * 60)
print("案例 1: 基础算术运算符")
print("=" * 60)

class Vector:
    """二维向量类 - 实现基础运算"""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        """加法: v1 + v2"""
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        return NotImplemented
    
    def __sub__(self, other):
        """减法: v1 - v2"""
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        return NotImplemented
    
    def __mul__(self, scalar):
        """标量乘法: v * 2"""
        if isinstance(scalar, (int, float)):
            return Vector(self.x * scalar, self.y * scalar)
        return NotImplemented
    
    def __truediv__(self, scalar):
        """标量除法: v / 2"""
        if isinstance(scalar, (int, float)):
            if scalar == 0:
                raise ValueError("不能除以零")
            return Vector(self.x / scalar, self.y / scalar)
        return NotImplemented
    
    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y})"

v1 = Vector(3, 4)
v2 = Vector(1, 2)

print(f"v1 = {v1}")
print(f"v2 = {v2}")
print(f"\nv1 + v2 = {v1 + v2}")
print(f"v1 - v2 = {v1 - v2}")
print(f"v1 * 2  = {v1 * 2}")
print(f"v1 / 2  = {v1 / 2}")


# ============================================================
# 案例 2: 反向运算符（右侧运算）
# ============================================================
print("\n" + "=" * 60)
print("案例 2: 反向运算符")
print("=" * 60)

class Money:
    """货币类 - 支持反向运算"""
    
    def __init__(self, amount: float):
        self.amount = amount
    
    def __add__(self, other):
        """m + 100 或 m + m2"""
        if isinstance(other, Money):
            return Money(self.amount + other.amount)
        elif isinstance(other, (int, float)):
            return Money(self.amount + other)
        return NotImplemented
    
    def __radd__(self, other):
        """100 + m（当左侧对象不支持加法时调用）"""
        if isinstance(other, (int, float)):
            return Money(other + self.amount)
        return NotImplemented
    
    def __mul__(self, other):
        """m * 2"""
        if isinstance(other, (int, float)):
            return Money(self.amount * other)
        return NotImplemented
    
    def __rmul__(self, other):
        """2 * m"""
        if isinstance(other, (int, float)):
            return Money(other * self.amount)
        return NotImplemented
    
    def __repr__(self) -> str:
        return f"Money(¥{self.amount:.2f})"

m = Money(100)
print(f"m = {m}")
print(f"\nm + 50    = {m + 50}")     # 调用 __add__
print(f"50 + m    = {50 + m}")       # 调用 __radd__
print(f"m * 2     = {m * 2}")        # 调用 __mul__
print(f"2 * m     = {2 * m}")        # 调用 __rmul__


# ============================================================
# 案例 3: 增强赋值运算符
# ============================================================
print("\n" + "=" * 60)
print("案例 3: 增强赋值运算符（原地修改）")
print("=" * 60)

class Counter:
    """计数器类 - 支持增强赋值"""
    
    def __init__(self, count: int = 0):
        self.count = count
    
    def __add__(self, other):
        """c + 5 返回新对象"""
        if isinstance(other, int):
            print(f"  → 调用 __add__，返回新对象")
            return Counter(self.count + other)
        return NotImplemented
    
    def __iadd__(self, other):
        """c += 5 原地修改"""
        if isinstance(other, int):
            print(f"  → 调用 __iadd__，原地修改")
            self.count += other
            return self  # 返回 self 实现原地修改
        return NotImplemented
    
    def __repr__(self) -> str:
        return f"Counter({self.count})"

# 普通加法（创建新对象）
c1 = Counter(10)
print(f"c1 = {c1}, id = {id(c1)}")
print("执行 c1 + 5:")
c2 = c1 + 5
print(f"c1 = {c1}, id = {id(c1)}")
print(f"c2 = {c2}, id = {id(c2)} (新对象)")

# 增强赋值（原地修改）
print(f"\nc1 = {c1}, id = {id(c1)}")
print("执行 c1 += 5:")
c1 += 5
print(f"c1 = {c1}, id = {id(c1)} (同一对象)")


# ============================================================
# 案例 4: 完整的数学运算
# ============================================================
print("\n" + "=" * 60)
print("案例 4: 完整的数学运算")
print("=" * 60)

class Fraction:
    """分数类 - 实现完整的数学运算"""
    
    def __init__(self, numerator: int, denominator: int):
        if denominator == 0:
            raise ValueError("分母不能为零")
        # 化简分数
        from math import gcd
        g = gcd(abs(numerator), abs(denominator))
        self.numerator = numerator // g
        self.denominator = denominator // g
        # 保证分母为正
        if self.denominator < 0:
            self.numerator = -self.numerator
            self.denominator = -self.denominator
    
    def __add__(self, other):
        """加法"""
        if isinstance(other, Fraction):
            num = self.numerator * other.denominator + other.numerator * self.denominator
            den = self.denominator * other.denominator
            return Fraction(num, den)
        elif isinstance(other, int):
            return Fraction(self.numerator + other * self.denominator, self.denominator)
        return NotImplemented
    
    def __sub__(self, other):
        """减法"""
        if isinstance(other, Fraction):
            num = self.numerator * other.denominator - other.numerator * self.denominator
            den = self.denominator * other.denominator
            return Fraction(num, den)
        return NotImplemented
    
    def __mul__(self, other):
        """乘法"""
        if isinstance(other, Fraction):
            return Fraction(self.numerator * other.numerator, 
                          self.denominator * other.denominator)
        elif isinstance(other, int):
            return Fraction(self.numerator * other, self.denominator)
        return NotImplemented
    
    def __truediv__(self, other):
        """除法"""
        if isinstance(other, Fraction):
            return Fraction(self.numerator * other.denominator,
                          self.denominator * other.numerator)
        return NotImplemented
    
    def __pow__(self, power):
        """幂运算"""
        if isinstance(power, int):
            if power >= 0:
                return Fraction(self.numerator ** power, self.denominator ** power)
            else:
                return Fraction(self.denominator ** (-power), self.numerator ** (-power))
        return NotImplemented
    
    def __neg__(self):
        """负号: -f"""
        return Fraction(-self.numerator, self.denominator)
    
    def __pos__(self):
        """正号: +f"""
        return self
    
    def __abs__(self):
        """绝对值: abs(f)"""
        return Fraction(abs(self.numerator), self.denominator)
    
    def __float__(self) -> float:
        """转换为浮点数"""
        return self.numerator / self.denominator
    
    def __repr__(self) -> str:
        if self.denominator == 1:
            return str(self.numerator)
        return f"{self.numerator}/{self.denominator}"

f1 = Fraction(1, 2)  # 1/2
f2 = Fraction(1, 3)  # 1/3

print(f"f1 = {f1}")
print(f"f2 = {f2}")
print(f"\nf1 + f2 = {f1 + f2}")
print(f"f1 - f2 = {f1 - f2}")
print(f"f1 * f2 = {f1 * f2}")
print(f"f1 / f2 = {f1 / f2}")
print(f"f1 ** 2 = {f1 ** 2}")
print(f"-f1     = {-f1}")
print(f"abs(-f1) = {abs(-f1)}")
print(f"float(f1) = {float(f1)}")


# ============================================================
# 案例 5: 整除、取模、divmod
# ============================================================
print("\n" + "=" * 60)
print("案例 5: 整除、取模、divmod")
print("=" * 60)

class Time:
    """时间类（秒）- 支持整除和取模"""
    
    def __init__(self, seconds: int):
        self.seconds = seconds
    
    def __floordiv__(self, other):
        """整除: time // 60"""
        if isinstance(other, int):
            return Time(self.seconds // other)
        return NotImplemented
    
    def __mod__(self, other):
        """取模: time % 60"""
        if isinstance(other, int):
            return self.seconds % other
        return NotImplemented
    
    def __divmod__(self, other):
        """divmod: divmod(time, 60)"""
        if isinstance(other, int):
            quotient = self.seconds // other
            remainder = self.seconds % other
            return (Time(quotient), remainder)
        return NotImplemented
    
    def __repr__(self) -> str:
        return f"Time({self.seconds}s)"

time = Time(3665)  # 1小时1分5秒
print(f"总时间: {time}")

minutes, seconds = divmod(time, 60)
print(f"\n转换为分钟:")
print(f"  分钟数: {minutes}")
print(f"  剩余秒数: {seconds}s")

hours, minutes = divmod(minutes, 60)
print(f"\n转换为小时:")
print(f"  小时数: {hours}")
print(f"  剩余分钟数: {minutes}s")


# ============================================================
# 案例 6: 位运算符
# ============================================================
print("\n" + "=" * 60)
print("案例 6: 位运算符（用于集合操作）")
print("=" * 60)

class BitSet:
    """位集合 - 使用位运算实现集合操作"""
    
    def __init__(self, value: int = 0):
        self.value = value
    
    def add(self, bit: int):
        """添加元素"""
        self.value |= (1 << bit)
    
    def __or__(self, other):
        """并集: s1 | s2"""
        if isinstance(other, BitSet):
            return BitSet(self.value | other.value)
        return NotImplemented
    
    def __and__(self, other):
        """交集: s1 & s2"""
        if isinstance(other, BitSet):
            return BitSet(self.value & other.value)
        return NotImplemented
    
    def __xor__(self, other):
        """对称差: s1 ^ s2"""
        if isinstance(other, BitSet):
            return BitSet(self.value ^ other.value)
        return NotImplemented
    
    def __sub__(self, other):
        """差集: s1 - s2"""
        if isinstance(other, BitSet):
            return BitSet(self.value & ~other.value)
        return NotImplemented
    
    def __contains__(self, bit: int) -> bool:
        """检查元素: bit in s"""
        return bool(self.value & (1 << bit))
    
    def __repr__(self) -> str:
        bits = [i for i in range(32) if i in self]
        return f"BitSet({bits})"

s1 = BitSet()
s1.add(1)
s1.add(2)
s1.add(3)

s2 = BitSet()
s2.add(2)
s2.add(3)
s2.add(4)

print(f"s1 = {s1}")
print(f"s2 = {s2}")
print(f"\ns1 | s2 (并集) = {s1 | s2}")
print(f"s1 & s2 (交集) = {s1 & s2}")
print(f"s1 ^ s2 (对称差) = {s1 ^ s2}")
print(f"s1 - s2 (差集) = {s1 - s2}")
print(f"\n2 in s1: {2 in s1}")
print(f"5 in s1: {5 in s1}")


# ============================================================
# 总结
# ============================================================
print("\n" + "=" * 60)
print("算术运算符总结")
print("=" * 60)
print("""
📌 算术运算符:
┌──────────────┬─────────────┬───────────────────────┐
│ 方法         │ 运算符      │ 说明                  │
├──────────────┼─────────────┼───────────────────────┤
│ __add__      │ +           │ 加法                  │
│ __sub__      │ -           │ 减法                  │
│ __mul__      │ *           │ 乘法                  │
│ __truediv__  │ /           │ 真除法                │
│ __floordiv__ │ //          │ 整除                  │
│ __mod__      │ %           │ 取模                  │
│ __pow__      │ **          │ 幂运算                │
│ __divmod__   │ divmod()    │ 返回商和余数          │
├──────────────┼─────────────┼───────────────────────┤
│ __neg__      │ -x          │ 负号（一元）          │
│ __pos__      │ +x          │ 正号（一元）          │
│ __abs__      │ abs(x)      │ 绝对值                │
├──────────────┼─────────────┼───────────────────────┤
│ __radd__     │ other + x   │ 反向加法（右侧）      │
│ __iadd__     │ x += other  │ 增强赋值（原地修改）  │
└──────────────┴─────────────┴───────────────────────┘

📌 位运算符:
┌──────────────┬─────────────┬───────────────────────┐
│ __and__      │ &           │ 按位与                │
│ __or__       │ |           │ 按位或                │
│ __xor__      │ ^           │ 按位异或              │
│ __lshift__   │ <<          │ 左移                  │
│ __rshift__   │ >>          │ 右移                  │
│ __invert__   │ ~           │ 按位取反              │
└──────────────┴─────────────┴───────────────────────┘

✅ 最佳实践:
1. 返回新对象，除非使用增强赋值（__iadd__ 等）
2. 不兼容的类型返回 NotImplemented
3. 实现反向运算符支持 other + x 语法
4. 增强赋值应返回 self 实现原地修改
5. 保持运算的数学意义和直觉

💡 使用场景:
- 向量和矩阵运算
- 复数运算
- 分数运算
- 货币计算
- 时间和日期运算
- 集合操作（使用位运算符）
""")