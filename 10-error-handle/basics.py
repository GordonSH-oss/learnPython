"""
基础异常处理示例 - 对应 exception-basics.md
运行：python basics.py
"""

# ── 1. try/except/else/finally 完整结构 ──────────────────────────────────────

def safe_divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError as e:
        print(f"[except] 除零错误：{e}")
        return None
    except TypeError as e:
        print(f"[except] 类型错误：{e}")
        return None
    else:
        # 无异常时执行
        print(f"[else]   计算成功：{a} / {b} = {result}")
        return result
    finally:
        # 无论如何都执行
        print(f"[finally] 调用结束")

print("=== 正常情况 ===")
safe_divide(10, 2)

print("\n=== 除零 ===")
safe_divide(10, 0)

print("\n=== 类型错误 ===")
safe_divide("10", 2)


# ── 2. 捕获多个异常 ──────────────────────────────────────────────────────────

def parse_input(value):
    try:
        return int(value)
    except (ValueError, TypeError) as e:
        print(f"解析失败：{type(e).__name__}: {e}")
        return 0

print("\n=== 多异常捕获 ===")
parse_input("abc")
parse_input(None)
parse_input("42")


# ── 3. raise 主动抛出 ────────────────────────────────────────────────────────

def validate_age(age):
    if not isinstance(age, int):
        raise TypeError(f"age 必须是整数，收到 {type(age).__name__}")
    if age < 0 or age > 150:
        raise ValueError(f"age 超出合理范围：{age}")
    return age

print("\n=== 主动抛出 ===")
try:
    validate_age("twenty")
except TypeError as e:
    print(f"TypeError: {e}")

try:
    validate_age(200)
except ValueError as e:
    print(f"ValueError: {e}")


# ── 4. 异常链 raise ... from ─────────────────────────────────────────────────

def load_config(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError as e:
        raise RuntimeError(f"配置文件不存在：{path}") from e

print("\n=== 异常链 ===")
try:
    load_config("/nonexistent/config.yaml")
except RuntimeError as e:
    print(f"RuntimeError: {e}")
    print(f"原始原因: {e.__cause__}")


# ── 5. 重新抛出（裸 raise）───────────────────────────────────────────────────

def process_with_log(data):
    try:
        return int(data)
    except ValueError:
        print("记录日志：数据格式错误")
        raise  # 原样重新抛出，不改变异常类型和堆栈

print("\n=== 重新抛出 ===")
try:
    process_with_log("bad")
except ValueError as e:
    print(f"最终捕获：{e}")
