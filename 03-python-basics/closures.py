# ============================================================
# 闭包（Closure）完整示例
# ============================================================


# ============================================================
# 示例 1：最基础的闭包 —— 移动平均值计算器
# ============================================================
#
# 问题：我们需要一个函数，每次调用时传入新数据，
#       自动计算到目前为止所有数据的平均值。
#
# 关键：series 只初始化一次（make_aver 调用时），
#       但在多次调用 aver 之间保持状态。

def make_aver():
    series = []                        # 只初始化一次
    def aver(new_value):
        series.append(new_value)       # 每次调用时累积数据
        return sum(series) / len(series)
    return aver                        # 返回函数本身，不是调用结果


avger = make_aver()
print("=== 示例 1：移动平均值 ===")
print(avger(10))   # 10.0
print(avger(11))   # 10.5
print(avger(12))   # 11.0


# ============================================================
# 示例 2：闭包 vs 全局变量
# ============================================================
#
# 如果不用闭包，需要全局变量 —— 但全局变量会污染命名空间，
# 而且无法创建多个互不干扰的实例。

print("\n=== 示例 2：多个独立的计算器实例 ===")

avger1 = make_aver()   # 独立的 series
avger2 = make_aver()   # 另一个独立的 series

print(avger1(10))   # avger1 的 series: [10]，结果 10.0
print(avger2(5))    # avger2 的 series: [5]，结果 5.0，互不影响
print(avger1(20))   # avger1 的 series: [10, 20]，结果 15.0
print(avger2(15))   # avger2 的 series: [5, 15]，结果 10.0


# ============================================================
# 示例 3：查看闭包捕获了哪些变量
# ============================================================

print("\n=== 示例 3：检查闭包的自由变量 ===")

avger3 = make_aver()
avger3(10)
avger3(20)

# __code__.co_freevars 列出被闭包捕获的变量名
print("捕获的变量名:", avger3.__code__.co_freevars)   # ('series',)

# __closure__ 是捕获变量的实际存储单元
print("捕获的变量值:", avger3.__closure__[0].cell_contents)  # [10, 20]


# ============================================================
# 示例 4：nonlocal —— 修改被捕获的不可变变量
# ============================================================
#
# 如果被捕获的变量是不可变类型（int、str、tuple），
# 直接赋值会报 UnboundLocalError。
# 必须用 nonlocal 声明才能修改。

def make_counter():
    count = 0
    def counter():
        nonlocal count     # 声明 count 来自外层函数
        count += 1         # 修改外层变量
        return count
    return counter

print("\n=== 示例 4：nonlocal 修改不可变变量 ===")
c = make_counter()
print(c())   # 1
print(c())   # 2
print(c())   # 3


# ============================================================
# 示例 5：用类实现相同效果（对比）
# ============================================================
#
# 闭包本质上是轻量级的对象：
# - 外层函数的局部变量  ≈  实例属性
# - 内层函数           ≈  方法
# 两种方式完全等价，选哪种取决于代码复杂度。

class Averager:
    def __init__(self):
        self._series = []

    def __call__(self, new_value):
        self._series.append(new_value)
        return sum(self._series) / len(self._series)


print("\n=== 示例 5：类实现相同效果（对比）===")
avg_obj = Averager()
print(avg_obj(10))   # 10.0
print(avg_obj(11))   # 10.5
print(avg_obj(12))   # 11.0
