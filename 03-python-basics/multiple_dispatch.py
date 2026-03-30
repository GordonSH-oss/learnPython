"""
Python multipledispatch 多分派函数详解

注意:
- `multipledispatch` 是第三方库，不是标准库
- 安装: pip install multipledispatch
- 这里用 `multiple_dispatch.py` 作为文件名，避免和第三方包同名导致导入冲突
"""

try:
    from multipledispatch import dispatch
except ModuleNotFoundError:
    print("本示例依赖第三方包 `multipledispatch`。")
    print("请先安装: pip install multipledispatch")
    raise SystemExit(0)

from numbers import Number


# ============================================================
# 案例 1: 最基础的多分派
# ============================================================
print("=" * 60)
print("案例 1: 根据多个参数类型分派")
print("=" * 60)


@dispatch(int, int)
def combine(left, right):
    return f"两个整数相加: {left + right}"


@dispatch(str, str)
def combine(left, right):
    return f"两个字符串拼接: {left + right}"


@dispatch(list, list)
def combine(left, right):
    return f"两个列表合并: {left + right}"


print(combine(3, 5))
print(combine("Py", "thon"))
print(combine([1, 2], [3, 4]))

print("\n关键点:")
print("  1. `@dispatch(int, int)` 表示按完整参数签名分派")
print("  2. `combine(int, str)` 和 `combine(str, int)` 可以是不同实现")
print("  3. 这和 `singledispatch` 只看第一个参数不同")


# ============================================================
# 案例 2: 参数顺序不同，命中的实现也不同
# ============================================================
print("\n" + "=" * 60)
print("案例 2: 参数顺序本身也是签名的一部分")
print("=" * 60)


@dispatch(str, int)
def format_pair(left, right):
    return f"字符串重复: {left * right}"


@dispatch(int, str)
def format_pair(left, right):
    return f"数字 + 单位: {left}{right}"


print(format_pair("ha", 3))
print(format_pair(3, "kg"))


# ============================================================
# 案例 3: 可以使用抽象类型
# ============================================================
print("\n" + "=" * 60)
print("案例 3: 为抽象类型 Number 注册")
print("=" * 60)


@dispatch(Number, Number)
def multiply(left, right):
    return f"数值相乘: {left * right}"


@dispatch((list, tuple), Number)
def multiply(left, right):
    return f"序列逐项放大: {[item * right for item in left]}"


print(multiply(2, 3.5))
print(multiply((1, 2, 3), 10))

print("\n说明:")
print("  - `Number` 可以匹配 int、float 等数值类型")
print("  - `(list, tuple)` 表示联合签名，两个类型都能命中")


# ============================================================
# 案例 4: 更具体的签名会优先命中
# ============================================================
print("\n" + "=" * 60)
print("案例 4: 更具体的签名优先")
print("=" * 60)


@dispatch(object, object)
def evaluate(left, right):
    return f"默认实现: ({left!r}, {right!r})"


@dispatch(object, float)
def evaluate(left, right):
    return f"右边是 float: {left} + {right ** 2}"


@dispatch(float, float)
def evaluate(left, right):
    return f"两个参数都是 float: {left ** 2 + right ** 2}"


print(evaluate("x", 2.0))
print(evaluate(2.0, 3.0))
print(evaluate("x", "y"))

print("\n说明:")
print("  - `(float, float)` 比 `(object, float)` 更具体")
print("  - 因此 `evaluate(2.0, 3.0)` 会优先走更具体的版本")


print("\n" + "=" * 60)
print("总结")
print("=" * 60)
print("""
什么时候适合用 multipledispatch？
1. 分派规则依赖多个参数的类型组合
2. 同一个操作对不同类型组合有明显不同语义
3. 你想避免大量 `if isinstance(...) and isinstance(...)`

什么时候要谨慎？
1. 它是第三方库，需要额外安装
2. 签名很多时，容易出现歧义
3. 如果只看第一个参数，用 `singledispatch` 往往更简单
""")
