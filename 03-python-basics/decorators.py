"""
Python 装饰器（Decorator）详解

装饰器是 Python 中非常强大的特性，用于在不修改原函数的情况下增强其功能
"""

# ============================================================
# 案例 1: 装饰器基础 - *args 和 **kwargs 的作用
# ============================================================
print("=" * 60)
print("案例 1: 装饰器可以接受任何类型、任何数量的参数")
print("=" * 60)

from typing import Any

def timer(func) -> Any:
    """计时装饰器 - 使用 *args 和 **kwargs 转发所有参数"""
    def wrapper(*args, **kwargs) -> Any:
        print("⏱️  Timer start")
        result = func(*args, **kwargs)
        print("⏱️  Timer end")
        return result
    return wrapper

@timer
def printer1(toPrint: int) -> Any:
    """接受 1 个参数"""
    print(f"  打印: {toPrint}")

@timer
def printer2(toPrint: int, toPrint1: str) -> Any:
    """接受 2 个参数"""
    print(f"  打印: {toPrint}, {toPrint1}")

@timer
def printer3(a: int, b: str, c: list, d: dict) -> Any:
    """接受 4 个不同类型的参数"""
    print(f"  打印: a={a}, b={b}, c={c}, d={d}")

@timer
def printer4(*args, **kwargs) -> Any:
    """接受任意数量的参数"""
    print(f"  位置参数: {args}")
    print(f"  关键字参数: {kwargs}")

print("✅ 同一个装饰器，可以装饰不同参数的函数：")
print("\n1个参数:")
printer1(5)

print("\n2个参数:")
printer2(5, "Hello")

print("\n4个不同类型的参数:")
printer3(10, "world", [1, 2, 3], {"key": "value"})

print("\n任意数量的参数:")
printer4(1, 2, 3, 4, 5, a="x", b="y", c="z")


# ============================================================
# 案例 2: 为什么装饰器能接受任何参数？
# ============================================================
print("\n" + "=" * 60)
print("案例 2: 原理解释")
print("=" * 60)

print("""
关键点：wrapper(*args, **kwargs)

• *args  - 捕获所有位置参数（tuple）
• **kwargs - 捕获所有关键字参数（dict）
• func(*args, **kwargs) - 原样转发给原函数

过程：
1. 调用 printer2(5, "Hello")
2. 实际调用 wrapper(5, "Hello")
3. wrapper 收到: args=(5, "Hello"), kwargs={}
4. 转发给原函数: func(5, "Hello")
5. 原函数执行并返回结果

因此，装饰器不需要知道原函数的签名！
""")


# ============================================================
# 案例 3: 演示参数转发过程
# ============================================================
print("=" * 60)
print("案例 3: 参数转发过程可视化")
print("=" * 60)

def debug_decorator(func):
    """调试装饰器 - 显示参数传递过程"""
    def wrapper(*args, **kwargs):
        print(f"\n  [装饰器] 接收到:")
        print(f"    位置参数: {args}")
        print(f"    关键字参数: {kwargs}")
        
        print(f"\n  [装饰器] 转发给原函数: {func.__name__}")
        result = func(*args, **kwargs)
        
        print(f"\n  [装饰器] 原函数返回: {result}")
        return result
    return wrapper

@debug_decorator
def add(a: int, b: int) -> int:
    """加法函数"""
    print(f"    [原函数] 执行: {a} + {b}")
    return a + b

@debug_decorator
def greet(name: str, greeting: str = "Hello") -> str:
    """问候函数"""
    print(f"    [原函数] 执行问候")
    return f"{greeting}, {name}!"

print("调用 add(3, 5):")
result1 = add(3, 5)

print("\n调用 greet('Alice'):")
result2 = greet("Alice")

print("\n调用 greet('Bob', greeting='Hi'):")
result3 = greet("Bob", greeting="Hi")


# ============================================================
# 案例 4: 多种参数类型的装饰器
# ============================================================
print("\n" + "=" * 60)
print("案例 4: 装饰器处理各种参数类型")
print("=" * 60)

def log_args(func):
    """日志装饰器 - 记录参数类型"""
    def wrapper(*args, **kwargs):
        print(f"\n📝 调用 {func.__name__}")
        
        if args:
            print("  位置参数:")
            for i, arg in enumerate(args):
                print(f"    [{i}] {arg} (type: {type(arg).__name__})")
        
        if kwargs:
            print("  关键字参数:")
            for key, value in kwargs.items():
                print(f"    {key}={value} (type: {type(value).__name__})")
        
        result = func(*args, **kwargs)
        print(f"  返回值: {result} (type: {type(result).__name__})")
        return result
    return wrapper

@log_args
def process_data(num: int, text: str, items: list, flag: bool = True):
    """处理数据"""
    return f"处理了 {len(items)} 个项目"

print("测试不同类型的参数:")
process_data(42, "test", [1, 2, 3], flag=False)


# ============================================================
# 案例 5: 装饰器不关心函数签名
# ============================================================
print("\n" + "=" * 60)
print("案例 5: 同一个装饰器装饰不同签名的函数")
print("=" * 60)

def simple_log(func):
    """简单日志装饰器"""
    def wrapper(*args, **kwargs):
        print(f"→ 调用 {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@simple_log
def func1():
    """无参数"""
    print("  无参数函数")

@simple_log
def func2(x):
    """1个参数"""
    print(f"  1个参数: {x}")

@simple_log
def func3(x, y, z):
    """3个参数"""
    print(f"  3个参数: {x}, {y}, {z}")

@simple_log
def func4(*args):
    """可变参数"""
    print(f"  可变参数: {args}")

@simple_log
def func5(**kwargs):
    """关键字参数"""
    print(f"  关键字参数: {kwargs}")

@simple_log
def func6(a, b, *args, c, d=10, **kwargs):
    """混合参数"""
    print(f"  所有参数: a={a}, b={b}, args={args}, c={c}, d={d}, kwargs={kwargs}")

print("测试各种函数签名:")
func1()
func2(1)
func3(1, 2, 3)
func4(1, 2, 3, 4, 5)
func5(name="Alice", age=30)
func6(1, 2, 3, 4, c=5, d=20, x=100, y=200)


# ============================================================
# 案例 6: 装饰器的限制和解决方案
# ============================================================
print("\n" + "=" * 60)
print("案例 6: 保留原函数的元信息")
print("=" * 60)

from functools import wraps

def bad_decorator(func):
    """不保留元信息的装饰器"""
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def good_decorator(func):
    """保留元信息的装饰器"""
    @wraps(func)  # 关键：使用 @wraps
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@bad_decorator
def original_function1():
    """这是原函数的文档字符串"""
    pass

@good_decorator
def original_function2():
    """这是原函数的文档字符串"""
    pass

print("❌ 不使用 @wraps:")
print(f"  函数名: {original_function1.__name__}")  # wrapper
print(f"  文档: {original_function1.__doc__}")      # None

print("\n✅ 使用 @wraps:")
print(f"  函数名: {original_function2.__name__}")  # original_function2
print(f"  文档: {original_function2.__doc__}")      # 这是原函数的文档字符串


# ============================================================
# 案例 7: 带参数的装饰器
# ============================================================
print("\n" + "=" * 60)
print("案例 7: 装饰器本身也可以带参数")
print("=" * 60)

def repeat(times: int):
    """重复执行装饰器 - 装饰器带参数"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"\n🔄 重复执行 {times} 次:")
            result = None
            for i in range(times):
                print(f"  第 {i+1} 次:", end=" ")
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def say_hello(name: str):
    print(f"Hello, {name}!")

say_hello("Alice")

print("\n装饰器工厂结构:")
print("""
repeat(3) 的本质是三层函数：
1. 外层 repeat(times)        -> 接收装饰器自己的参数
2. 中层 decorator(func)     -> 接收被装饰函数
3. 内层 wrapper(*args, **kwargs) -> 真正执行增强逻辑
""")

print("再看一个更接近真实项目的例子：自定义格式的计时装饰器")

def clock(format_str="耗时: {duration:.4f}s"):
    """计时装饰器工厂 - 支持自定义输出格式"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time

            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            print(format_str.format(func_name=func.__name__, duration=duration))
            return result
        return wrapper
    return decorator

@clock(format_str="  函数 {func_name} 运行时间: {duration:.2f} 秒")
def slow_add(a, b):
    import time

    time.sleep(0.2)
    return a + b

@clock()
def slow_mul(a, b):
    import time

    time.sleep(0.1)
    return a * b

print(f"slow_add(1, 2) -> {slow_add(1, 2)}")
print(f"slow_mul(3, 4) -> {slow_mul(3, 4)}")

print("""
这个例子说明：
• `format_str` 被外层函数捕获，形成闭包
• 每次调用 slow_add / slow_mul 时，wrapper 都能访问这个参数
• `@clock(...)` 一定要加括号，因为你在调用装饰器工厂
• 如果格式串里用了 `{func_name}`、`{duration}`，format() 就必须传入同名参数
""")


# ============================================================
# 案例 8: 实用的装饰器示例
# ============================================================
print("\n" + "=" * 60)
print("案例 8: 实用装饰器 - 缓存、验证、日志")
print("=" * 60)

# 1. 缓存装饰器
def cache(func):
    """简单的缓存装饰器"""
    cached_results = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 创建缓存键（简化版，实际应该处理 kwargs）
        key = args
        if key in cached_results:
            print(f"  💾 从缓存返回: {key}")
            return cached_results[key]
        
        print(f"  🔄 计算结果: {key}")
        result = func(*args, **kwargs)
        cached_results[key] = result
        return result
    return wrapper

@cache
def expensive_computation(n: int) -> int:
    """耗时计算"""
    return n ** 2

print("缓存装饰器:")
print(f"第1次调用 expensive_computation(5): {expensive_computation(5)}")
print(f"第2次调用 expensive_computation(5): {expensive_computation(5)}")  # 从缓存
print(f"第1次调用 expensive_computation(3): {expensive_computation(3)}")

# 2. 验证装饰器
def validate_positive(func):
    """验证参数为正数"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        for arg in args:
            if isinstance(arg, (int, float)) and arg < 0:
                raise ValueError(f"参数必须为正数，得到: {arg}")
        return func(*args, **kwargs)
    return wrapper

@validate_positive
def calculate_square_root(n: float) -> float:
    """计算平方根"""
    return n ** 0.5

print("\n\n验证装饰器:")
try:
    print(f"calculate_square_root(16): {calculate_square_root(16)}")
    print(f"calculate_square_root(-4): {calculate_square_root(-4)}")
except ValueError as e:
    print(f"  ❌ 错误: {e}")


# ============================================================
# 案例 9: 类作为装饰器
# ============================================================
print("\n" + "=" * 60)
print("案例 9: 使用类实现装饰器")
print("=" * 60)

class CallCounter:
    """计数装饰器 - 使用类实现"""
    def __init__(self, func):
        self.func = func
        self.count = 0
        wraps(func)(self)  # 保留原函数信息
    
    def __call__(self, *args, **kwargs):
        """使类可调用"""
        self.count += 1
        print(f"  📊 函数 {self.func.__name__} 已被调用 {self.count} 次")
        return self.func(*args, **kwargs)

@CallCounter
def greet(name: str):
    print(f"    Hello, {name}!")

print("类装饰器:")
greet("Alice")
greet("Bob")
greet("Charlie")


# ============================================================
# 案例 10: 装饰器链
# ============================================================
print("\n" + "=" * 60)
print("案例 10: 多个装饰器堆叠")
print("=" * 60)

def uppercase(func):
    """转大写装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper() if isinstance(result, str) else result
    return wrapper

def add_prefix(func):
    """添加前缀装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return f"[PREFIX] {result}" if isinstance(result, str) else result
    return wrapper

def add_suffix(func):
    """添加后缀装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return f"{result} [SUFFIX]" if isinstance(result, str) else result
    return wrapper

@add_suffix
@add_prefix
@uppercase
def get_message(name: str) -> str:
    """获取消息"""
    return f"hello, {name}"

print("装饰器链（从下到上执行）:")
print(f"  原始: hello, alice")
print(f"  结果: {get_message('alice')}")


# ============================================================
# 总结
# ============================================================
print("\n" + "=" * 60)
print("装饰器总结")
print("=" * 60)
print("""
✅ 装饰器可以接受任何类型、任何数量的参数：

关键技术：
• 使用 *args 捕获所有位置参数
• 使用 **kwargs 捕获所有关键字参数
• 原样转发给原函数：func(*args, **kwargs)

基本结构：
def decorator(func):
    @wraps(func)  # 保留原函数信息
    def wrapper(*args, **kwargs):
        # 前置处理
        result = func(*args, **kwargs)
        # 后置处理
        return result
    return wrapper

优点：
1. 通用性强 - 同一个装饰器可以装饰任何函数
2. 不需要修改原函数代码
3. 可以组合使用（装饰器链）
4. 代码复用性高

常见应用：
• 日志记录
• 性能计时
• 权限验证
• 缓存
• 参数验证
• 重试机制
• 事务管理

最佳实践：
1. 使用 @wraps(func) 保留原函数元信息
2. 确保 wrapper 接受 *args 和 **kwargs
3. 返回原函数的返回值
4. 添加文档字符串说明装饰器的作用
5. 考虑是否需要带参数的装饰器

带参数装饰器的本质：
1. 外层工厂函数接收配置参数
2. 中层 decorator 接收原函数
3. 内层 wrapper 执行增强逻辑
4. 工厂参数通常通过闭包被 wrapper 访问

记住：
装饰器 + *args + **kwargs = 通用且强大的函数增强工具！
""")
