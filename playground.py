import types

class User:
    # 1. 这是一个类属性（属于类）
    species = "Human"

    def __init__(self, name):
        # 2. 这是一个实例属性（属于每个独立的实例）
        self.name = name

    # 3. 这是一个在类里正常定义的方法
    def class_say_hi(self, words):
        print(f"{self.name}: {words}")

# 实例化一个对象
user_instance = User("张三")

# 4. 动态给这个【实例】添加一个属性和方法
user_instance.dynamic_attr = "New Property"

def extra_func(self):
    print("我是动态绑定的方法")
user_instance.dynamic_method = types.MethodType(extra_func, user_instance)


# ==========================================
# 核心对比：打印两个字典
# ==========================================
print("--- 1. 实例对象的 dict (user_instance.__dict__) ---")
for key, value in user_instance.__dict__.items():
    print(f"键: {key:<15} -> 值类型/内容: {value}")

print("\n--- 2. 类对象的 dict (User.__dict__) ---")
for key, value in User.__dict__.items():
    # 过滤掉系统自带的下划线属性，只看我们自己定义的
    if not key.startswith("__") or key == "__init__":
        print(f"键: {key:<15} -> 值类型/内容: {value}")
