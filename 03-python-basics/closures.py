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
# 示例 4：nonlocal —— 对外层变量重新赋值
# ============================================================
#
# 内层函数可以读取外层变量，也可以修改外层变量指向的对象内容
# （如 list.append），但不能对外层变量本身重新赋值——除非用 nonlocal。
#
# 判断规则：只要写了赋值号 =，就需要 nonlocal。
# 原因：Python 看到 = 就把变量当作局部变量，
#       但读取时发现它没有局部定义 → UnboundLocalError。

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
# 示例 5：循环里创建函数的坑 —— late binding
# ============================================================
#
# playground.py 里的写法会全部输出 2：
#
# func_list = []
# for i in range(3):
#     def func():
#         print(i)
#     func_list.append(func)
#
# 原因不是 append 有问题，而是函数体里的 i 会在“调用函数时”才查找。
# 循环结束后 i 已经是 2，所以所有函数读到的都是同一个 i。
#
# 注意：如果这段代码写在模块顶层，i 是全局变量，不算闭包变量；
# 如果写在外层函数里，i 就是被闭包捕获的自由变量。
# 两者的关键都一样：函数捕获/引用的是变量绑定，不是当时的值。

def build_printers_wrong():
    printers = []
    for i in range(3):
        def printer():
            return i       # 调用时才读取 i
        printers.append(printer)
    return printers


print("\n=== 示例 5：循环闭包的 late binding 问题 ===")
wrong_printers = build_printers_wrong()
print([printer() for printer in wrong_printers])   # [2, 2, 2]

# 可以检查一下：这些函数捕获的自由变量名都是 i。
print("捕获的变量名:", wrong_printers[0].__code__.co_freevars)  # ('i',)


# ============================================================
# 示例 6：修复 late binding —— 把当前值固定下来
# ============================================================
#
# 修法 1：默认参数
# 默认参数会在 def 执行时求值，因此 i=i 会把当轮循环的 i 固定到参数里。
# 这时 i 不再是自由变量，而是函数自己的默认参数。

def build_printers_with_default_arg():
    printers = []
    for i in range(3):
        def printer(i=i):
            return i
        printers.append(printer)
    return printers


print("\n=== 示例 6.1：用默认参数固定当前值 ===")
default_arg_printers = build_printers_with_default_arg()
print([printer() for printer in default_arg_printers])  # [0, 1, 2]
print("默认参数:", [printer.__defaults__ for printer in default_arg_printers])


# 修法 2：工厂函数
# 每次调用 make_printer(value) 都会创建一个新的局部变量 value，
# 因此每个返回的 printer 都捕获自己的 value。

def make_printer(value):
    def printer():
        return value
    return printer


def build_printers_with_factory():
    printers = []
    for i in range(3):
        printers.append(make_printer(i))
    return printers


print("\n=== 示例 6.2：用工厂函数创建独立闭包 ===")
factory_printers = build_printers_with_factory()
print([printer() for printer in factory_printers])  # [0, 1, 2]
print("捕获的变量值:", [printer.__closure__[0].cell_contents for printer in factory_printers])


# ============================================================
# 示例 7：用类实现相同效果（对比）
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


print("\n=== 示例 7：类实现相同效果（对比）===")
avg_obj = Averager()
print(avg_obj(10))   # 10.0
print(avg_obj(11))   # 10.5
print(avg_obj(12))   # 11.0
