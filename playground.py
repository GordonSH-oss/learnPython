import time
from functools import wraps

# 外层：装饰器工厂，接收自定义参数
def clock(format_str="耗时: {duration:.4f}s"):
    # 中层：装饰器，接收被装饰函数
    def decorator(func):
        # 内层：包装函数，执行增强逻辑
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)  # 执行原函数
            duration = time.perf_counter() - start
            # 使用装饰器的参数 format_str
            print(format_str.format(func_name=func.__name__, duration=duration))
            return result
        return wrapper
    return decorator

# 用法1：传自定义参数
@clock(format_str="函数 {func_name} 运行时间: {duration:.2f} 秒")
def slow_add(a, b):
    time.sleep(0.5)
    return a + b

# 用法2：使用默认参数
@clock()  # 注意：必须加括号！代表调用工厂函数
def slow_mul(a, b):
    time.sleep(0.3)
    return a * b

# 测试调用
slow_add(1, 2)  # 输出：函数 {func_name} 运行时间: 0.50 秒
slow_mul(3, 4)  # 输出：耗时: 0.3000s
