"""
Python LEGB 作用域规则详解

Python 按照 L → E → G → B 的顺序查找变量：
  L (Local)    - 局部作用域：当前函数内部
  E (Enclosing)- 闭包作用域：嵌套函数的外层函数
  G (Global)   - 全局作用域：模块顶层
  B (Built-in) - 内置作用域：len、print、range 等内置名称
"""

# ============================================================
# 案例 1: Local（局部作用域）
# ============================================================
print("=" * 60)
print("案例 1: Local（局部作用域）")
print("=" * 60)

x = "全局 x"

def show_local():
    x = "局部 x"   # 遮蔽了全局 x
    print(f"  函数内: {x}")

show_local()
print(f"函数外: {x}")

print("""
说明：
  函数内的 x 是一个独立的局部变量，和全局 x 互不影响。
  函数结束后，局部 x 销毁，全局 x 保持不变。
""")


# ============================================================
# 案例 2: Global（全局作用域）
# ============================================================
print("=" * 60)
print("案例 2: Global（全局作用域）")
print("=" * 60)

b = 100

def read_global():
    # 没有局部 b，Python 自动向上查找到全局
    print(f"  函数内读取全局 b: {b}")

read_global()

print("""
说明：
  函数内没有定义 b，Python 沿 LEGB 链向上找到全局 b=100。
  只读不写时，不需要 global 声明。
""")


# ============================================================
# 案例 3: 修改全局变量必须声明 global
# ============================================================
print("=" * 60)
print("案例 3: 修改全局变量必须声明 global")
print("=" * 60)

counter = 0

def increment_wrong():
    try:
        counter += 1   # ❌ UnboundLocalError
    except UnboundLocalError as e:
        print(f"  ❌ 报错: {e}")

def increment_correct():
    global counter
    counter += 1       # ✅ 显式声明后才能修改
    print(f"  ✅ counter 变为: {counter}")

increment_wrong()
increment_correct()
increment_correct()

print("""
说明：
  函数内只要出现 counter = ...（赋值语句），
  Python 编译阶段就把整个函数里的 counter 视为局部变量。
  这包括赋值语句之前的读取操作，所以会报 UnboundLocalError。

  必须用 global counter 声明，才能在函数内修改全局变量。
""")


# ============================================================
# 案例 4: Enclosing（闭包/嵌套作用域）
# ============================================================
print("=" * 60)
print("案例 4: Enclosing（闭包作用域）")
print("=" * 60)

def outer():
    message = "来自 outer 的消息"   # outer 的局部变量

    def inner():
        # inner 没有 message，向上找到 outer 的 Enclosing 层
        print(f"  inner 读取: {message}")

    inner()

outer()

print("""
说明：
  inner() 在 L（自身）找不到 message，
  向上一层到 E（outer 的局部），找到了。
  不需要 global，因为 message 不在全局层。
""")


# ============================================================
# 案例 5: 修改闭包变量必须声明 nonlocal
# ============================================================
print("=" * 60)
print("案例 5: 修改闭包变量必须声明 nonlocal")
print("=" * 60)

def make_counter():
    count = 0

    def increment():
        nonlocal count   # 声明修改的是外层函数的 count
        count += 1
        print(f"  count: {count}")

    return increment

counter_fn = make_counter()
counter_fn()
counter_fn()
counter_fn()

print("""
说明：
  nonlocal 对应 Enclosing 层，global 对应 Global 层。
  闭包中修改外层变量必须用 nonlocal 声明，否则同样会报 UnboundLocalError。
""")


# ============================================================
# 案例 6: Built-in（内置作用域）
# ============================================================
print("=" * 60)
print("案例 6: Built-in（内置作用域）")
print("=" * 60)

def show_builtin():
    # len、range、print 等都在内置作用域
    items = [1, 2, 3]
    print(f"  len([1,2,3]) = {len(items)}")
    print(f"  type(42) = {type(42)}")

show_builtin()

print("""
说明：
  Built-in 是查找链的最后一层，Python 的内置函数（len、range、
  print、type 等）都在这里。L → E → G 都找不到时才到这一层。
""")


# ============================================================
# 案例 7: 遮蔽内置名称（shadowing）——常见陷阱
# ============================================================
print("=" * 60)
print("案例 7: 遮蔽内置名称（shadowing）——常见陷阱")
print("=" * 60)

def shadowing_demo():
    list = [1, 2, 3]       # ⚠️ 遮蔽了内置 list
    print(f"  局部 list: {list}")
    try:
        new_list = list("hello")   # ❌ 此时 list 是局部变量，不是内置类型
    except TypeError as e:
        print(f"  ❌ 报错: {e}")

shadowing_demo()

# 全局遮蔽
len = lambda x: "我遮蔽了 len"   # ⚠️ 危险！
print(f"  被遮蔽的 len: {len([1, 2, 3])}")
del len                           # 删除全局遮蔽，恢复内置 len
print(f"  恢复后的 len: {len([1, 2, 3])}")

print("""
说明：
  由于 LEGB 顺序，局部/全局的同名变量会遮蔽内置名称。
  永远不要用 list、dict、str、len、id 等内置名称命名变量。
""")


# ============================================================
# 案例 8: 完整的 LEGB 四层同时存在
# ============================================================
print("=" * 60)
print("案例 8: 完整的 LEGB 四层同时存在")
print("=" * 60)

scope_name = "G - 全局"           # Global 层

def enclosing_fn():
    scope_name = "E - 闭包外层"   # Enclosing 层

    def inner_fn():
        scope_name = "L - 局部"   # Local 层
        print(f"  inner_fn 看到: {scope_name}")   # L 优先

    def inner_fn_no_local():
        # 没有局部 scope_name，向上找到 Enclosing
        print(f"  inner_fn_no_local 看到: {scope_name}")   # E

    inner_fn()
    inner_fn_no_local()

enclosing_fn()

def only_global():
    # 没有局部，没有闭包，向上找到 Global
    print(f"  only_global 看到: {scope_name}")   # G

only_global()

print("""
说明：
  Python 始终从最内层开始查找，谁最近用谁。
  L → E → G → B，找到即停止，找不到才继续往外。
""")


# ============================================================
# 案例 9: 工厂函数 —— Enclosing 作用域的典型应用
# ============================================================
print("=" * 60)
print("案例 9: 工厂函数（Enclosing 作用域的典型应用）")
print("=" * 60)

def make_multiplier(factor):
    """返回一个乘法函数，factor 保存在 Enclosing 作用域"""
    def multiply(x):
        return x * factor   # factor 来自 Enclosing
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)

print(f"  double(5) = {double(5)}")
print(f"  triple(5) = {triple(5)}")
print(f"  double(10) = {double(10)}")

print("""
说明：
  make_multiplier 返回后，其局部变量 factor 并没有被销毁，
  而是被内层函数 multiply 捕获，保存在闭包的 Enclosing 作用域中。
  这就是"闭包"（Closure）的本质。
""")


# ============================================================
# 总结
# ============================================================
print("=" * 60)
print("LEGB 规则总结")
print("=" * 60)
print("""
查找顺序：L → E → G → B（找到即停止）

  L  Local      函数内部定义的变量
  E  Enclosing  嵌套函数的外层函数（闭包）
  G  Global     模块顶层定义的变量
  B  Built-in   Python 内置名称（len、print、range...）

修改规则：
  • 读取变量：无需声明，自动按 LEGB 查找
  • 修改 Global 变量：函数内必须用 global 声明
  • 修改 Enclosing 变量：内层函数必须用 nonlocal 声明

常见陷阱：
  • 函数内出现赋值语句，该变量在整个函数内都是局部变量（包括赋值前的行）
  • 用内置名称（list、len 等）命名变量会遮蔽内置函数
""")
