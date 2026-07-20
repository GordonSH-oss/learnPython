from functools import wraps

def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Before calling the function")
        from datetime import datetime
        start=datetime.now()  # 模拟耗时操作
        result = func(*args, **kwargs)
        end=datetime.now()
        print(f"Function execution time: {end-start}")
        print("After calling the function")
        return result
    return wrapper

@decorator
def say_hello(name):
    print(f"Hello, {name}!")

if __name__ == "__main__":
    print(say_hello.__name__)  # 输出: wrapper
    say_hello("Tom")