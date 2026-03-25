def outer(func):
    def wrapper():
        print("1 外层装饰器：开始")
        func()  # 👈 这里调用的不是原函数！是被包装后的 middle！
        print("4 外层装饰器：结束")
    return wrapper

def middle(func):
    def wrapper():
        print("2 中层装饰器：开始")
        func()  # 👈 这里调用的也不是原函数！是 inner！
        print("3 中层装饰器：结束")
    return wrapper

def inner(func):
    def wrapper():
        print("2.5 内层装饰器：开始")
        func()  # 👈 只有这里，才真正调用原函数！
        print("2.7 内层装饰器：结束")
    return wrapper

# 叠加顺序：从下往上套
@outer
@middle
@inner
def hello():
    print("=== 原函数 hello ===")

hello()