"""
Python singledispatch 单分派泛化函数详解

`@singledispatch` 可以让一个函数根据“第一个参数的类型”自动选择实现。
它适合把不断增长的 if/elif 类型判断拆成更清晰、可扩展的结构。
"""

from collections.abc import Mapping, Sequence
from functools import singledispatch


# ============================================================
# 案例 1: 基础用法
# ============================================================
print("=" * 60)
print("案例 1: 基础用法 - 按第一个参数类型自动分派")
print("=" * 60)


@singledispatch
def describe(value):
    """默认实现：处理未注册的类型"""
    raise TypeError(f"暂不支持类型: {type(value).__name__}")


@describe.register
def describe_int(value: int):
    return f"整数: {value} -> {value * 2}"


@describe.register
def describe_str(value: str):
    return f"字符串: {value!r} -> {value.upper()}"


@describe.register(list)
def describe_list(value):
    return f"列表: 长度={len(value)}, 求和={sum(value)}"


print(describe(10))
print(describe("hello"))
print(describe([1, 2, 3]))

try:
    print(describe(3.14))
except TypeError as exc:
    print(f"捕获异常: {exc}")

print("\n关键点:")
print("  1. `@singledispatch` 先定义默认实现")
print("  2. `@函数名.register(类型)` 为指定类型注册实现")
print("  3. 分派依据只有第一个参数")


# ============================================================
# 案例 2: 类型继承链会影响分派结果
# ============================================================
print("\n" + "=" * 60)
print("案例 2: 继承层级 - bool 是 int 的子类")
print("=" * 60)


@singledispatch
def classify(value):
    return f"默认分支: {value!r}"


@classify.register
def classify_int(value: int):
    return f"int 分支: {value} (平方={value ** 2})"


print("还没注册 bool 之前:")
print(f"  classify(True) -> {classify(True)}")
print("  原因: bool 继承自 int，会沿着 MRO 找到最合适的实现")


@classify.register
def classify_bool(value: bool):
    return f"bool 分支: {value} (取反={not value})"


print("\n注册 bool 之后:")
print(f"  classify(True) -> {classify(True)}")
print(f"  classify(5) -> {classify(5)}")


# ============================================================
# 案例 3: 可以为抽象基类注册实现
# ============================================================
print("\n" + "=" * 60)
print("案例 3: 为抽象基类注册 - Mapping / Sequence")
print("=" * 60)


@singledispatch
def summarize(value):
    return f"通用摘要: {value!r}"


@summarize.register
def summarize_mapping(value: Mapping):
    return f"映射类型: {len(value)} 个键 -> {list(value.keys())}"


@summarize.register
def summarize_sequence(value: Sequence):
    return f"序列类型: 长度={len(value)}, 前两个元素={list(value[:2])}"


@summarize.register
def summarize_str(value: str):
    return f"字符串单独处理: 长度={len(value)}, 内容={value!r}"


print(summarize({"name": "Ada", "age": 20}))
print(summarize((10, 20, 30, 40)))
print(summarize("Python"))

print("\n说明:")
print("  - `dict` 会命中 `Mapping`")
print("  - `tuple` 会命中 `Sequence`")
print("  - `str` 虽然也是序列，但这里有更具体的注册，所以优先命中 `str`")


# ============================================================
# 案例 4: 查看当前分派到哪个实现
# ============================================================
print("\n" + "=" * 60)
print("案例 4: dispatch() 和 registry")
print("=" * 60)

bool_impl = classify.dispatch(bool)
int_impl = classify.dispatch(int)
float_impl = classify.dispatch(float)

print(f"classify.dispatch(bool).__name__  -> {bool_impl.__name__}")
print(f"classify.dispatch(int).__name__   -> {int_impl.__name__}")
print(f"classify.dispatch(float).__name__ -> {float_impl.__name__}")

registered_types = [cls.__name__ for cls in classify.registry]
print(f"已注册类型: {registered_types}")


# ============================================================
# 案例 5: 它不是“多参数分派”
# ============================================================
print("\n" + "=" * 60)
print("案例 5: 只看第一个参数")
print("=" * 60)


@singledispatch
def combine(left, right):
    return f"默认组合: {left!r}, {right!r}"


@combine.register
def combine_list(left: list, right):
    return f"第一个参数是 list: {left + [right]}"


print(combine([1, 2], 3))
print(combine("x", [1, 2, 3]))
print("注意: 第二个调用不会看 right 的类型，因为 singledispatch 只检查第一个参数")


print("\n" + "=" * 60)
print("总结")
print("=" * 60)
print("""
什么时候适合用 singledispatch？
1. 你要根据输入类型做不同处理
2. 类型分支会不断增加
3. 你希望新增类型时不改原函数主体

什么时候不适合？
1. 逻辑只分两个很简单的分支
2. 分派依据不是第一个参数
3. 规则主要依赖“值”而不是“类型”
""")
