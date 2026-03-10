"""
Python self 参数使用示例
演示什么时候需要 self，什么时候不需要
"""

# ============================================================
# 1. 实例方法 - 需要 self
# ============================================================

class Person:
    def __init__(self, name: str, age: int):
        # ✅ 需要 self：设置实例属性
        self.name = name
        self.age = age
    
    def introduce(self):
        # ✅ 需要 self：访问实例属性 self.name 和 self.age
        return f"我是 {self.name}，{self.age} 岁"
    
    def have_birthday(self):
        # ✅ 需要 self：修改实例属性 self.age
        self.age += 1
        return self.age
    
    def get_info(self):
        # ✅ 需要 self：调用其他实例方法
        return self.introduce()


# ============================================================
# 2. 类方法 - 需要 cls（不是 self）
# ============================================================

class Counter:
    count = 0  # 类属性
    
    def __init__(self, name: str):
        self.name = name
        Counter.count += 1
    
    @classmethod
    def get_count(cls):
        # ✅ 需要 cls：访问类属性 cls.count
        return cls.count
    
    @classmethod
    def reset_count(cls):
        # ✅ 需要 cls：修改类属性
        cls.count = 0
    
    @classmethod
    def create(cls, name: str):
        # ✅ 需要 cls：创建新实例（工厂方法）
        return cls(name)


# ============================================================
# 3. 静态方法 - 不需要 self 或 cls
# ============================================================

class MathUtils:
    @staticmethod
    def add(a: int, b: int) -> int:
        # ❌ 不需要 self：不访问任何实例或类属性
        return a + b
    
    @staticmethod
    def is_even(n: int) -> bool:
        # ❌ 不需要 self：纯函数
        return n % 2 == 0


# ============================================================
# 4. 你的 Node 类示例
# ============================================================

class Node:
    def __init__(self, value: int, next_node: 'Node' | None = None):
        # ✅ 需要 self：设置实例属性
        self.value = value
        self.next = next_node
    
    def get_value(self):
        # ✅ 需要 self：访问实例属性
        return self.value
    
    def get_next(self):
        # ✅ 需要 self：访问实例属性
        return self.next
    
    def set_next(self, next_node: 'Node' | None):
        # ✅ 需要 self：修改实例属性
        self.next = next_node
    
    @staticmethod
    def is_valid_value(value):
        # ❌ 不需要 self：不访问实例或类属性，纯验证函数
        return isinstance(value, int)
    
    @classmethod
    def create_empty(cls):
        # ✅ 需要 cls：创建新实例（工厂方法）
        return cls(0, None)


# ============================================================
# 5. 判断流程示例
# ============================================================

class Example:
    class_var = "类变量"
    
    def __init__(self, instance_var: str):
        # ✅ 需要 self：设置实例属性
        self.instance_var = instance_var
    
    def instance_method(self):
        # ✅ 需要 self：访问实例属性
        return self.instance_var
    
    @classmethod
    def class_method(cls):
        # ✅ 需要 cls：访问类属性
        return cls.class_var
    
    @staticmethod
    def static_method():
        # ❌ 不需要 self/cls：不访问任何属性
        return "这是一个静态方法"


# ============================================================
# 测试代码
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("1. 实例方法示例")
    print("=" * 60)
    person = Person("张三", 25)
    print(person.introduce())      # 我是 张三，25 岁
    person.have_birthday()
    print(f"生日后：{person.age} 岁")  # 26 岁
    
    print("\n" + "=" * 60)
    print("2. 类方法示例")
    print("=" * 60)
    c1 = Counter("计数器1")
    c2 = Counter("计数器2")
    print(f"当前计数：{Counter.get_count()}")  # 2
    Counter.reset_count()
    print(f"重置后：{Counter.get_count()}")   # 0
    
    print("\n" + "=" * 60)
    print("3. 静态方法示例")
    print("=" * 60)
    print(f"3 + 5 = {MathUtils.add(3, 5)}")           # 8
    print(f"4 是偶数？{MathUtils.is_even(4)}")         # True
    
    print("\n" + "=" * 60)
    print("4. Node 类示例")
    print("=" * 60)
    node1 = Node(1)
    node2 = Node(2, node1)
    print(f"node2.value = {node2.get_value()}")       # 2
    print(f"node2.next.value = {node2.get_next().get_value()}")  # 1
    print(f"值 5 有效？{Node.is_valid_value(5)}")     # True
    empty_node = Node.create_empty()
    print(f"空节点值：{empty_node.get_value()}")      # 0
    
    print("\n" + "=" * 60)
    print("5. 判断流程示例")
    print("=" * 60)
    ex = Example("实例变量")
    print(f"实例方法：{ex.instance_method()}")        # 实例变量
    print(f"类方法：{Example.class_method()}")        # 类变量
    print(f"静态方法：{Example.static_method()}")     # 这是一个静态方法





