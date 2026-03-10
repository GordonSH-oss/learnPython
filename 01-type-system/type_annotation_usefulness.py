"""
演示：即使通过类方法调用，返回类型注解仍然非常有用
"""

from __future__ import annotations

class Node:
    def __init__(self, value: int, next: Node | None = None):
        self.value = value
        self.next = next
    
    @classmethod
    def from_list(cls, values: list[int], circular: bool = False) -> 'Node' | None:
        """
        类方法：通过类调用，但返回的是实例
        
        返回类型注解 'Node' | None 的作用：
        1. 告诉调用者：这个方法返回 Node 实例或 None
        2. IDE 可以根据类型注解提供代码补全
        3. 类型检查器（如 mypy）可以检查类型错误
        4. 开发者可以快速理解返回值类型
        """
        if not values:
            return None
        
        nodes = [cls(value) for value in values]
        
        for i in range(len(nodes) - 1):
            nodes[i].next = nodes[i + 1]
        
        if circular and len(nodes) > 1:
            nodes[-1].next = nodes[0]
        
        return nodes[0]  # ← 返回的是 Node 实例，不是类本身！
    
    def get_value(self) -> int:
        """实例方法"""
        return self.value

# ============================================================
# 演示：类型注解的作用
# ============================================================

print("=" * 60)
print("演示：类型注解的作用")
print("=" * 60)

# 1. 通过类调用（不需要实例化）
result = Node.from_list([1, 2, 3])

# 2. 类型注解告诉 IDE 和开发者：result 是 Node | None
print(f"result 的类型：{type(result)}")  # <class '__main__.Node'>
print(f"result 是 Node 实例：{isinstance(result, Node)}")  # True

# 3. 因为有类型注解，IDE 知道 result 有 .value 和 .get_value() 方法
if result is not None:  # 类型检查器知道需要检查 None
    print(f"result.value = {result.value}")  # ✅ IDE 会提供代码补全
    print(f"result.get_value() = {result.get_value()}")  # ✅ IDE 会提供代码补全

print()

# ============================================================
# 对比：有类型注解 vs 没有类型注解
# ============================================================

print("=" * 60)
print("对比：有类型注解 vs 没有类型注解")
print("=" * 60)

class NodeWithoutAnnotation:
    def __init__(self, value: int):
        self.value = value
    
    @classmethod
    def from_list(cls, values: list[int]):  # ❌ 没有返回类型注解
        if not values:
            return None
        return cls(values[0])

class NodeWithAnnotation:
    def __init__(self, value: int):
        self.value = value
    
    @classmethod
    def from_list(cls, values: list[int]) -> 'NodeWithAnnotation' | None:  # ✅ 有返回类型注解
        if not values:
            return None
        return cls(values[0])

# 使用没有类型注解的方法
result1 = NodeWithoutAnnotation.from_list([1, 2, 3])
# IDE 不知道 result1 是什么类型，无法提供代码补全
# 类型检查器无法检查类型错误

# 使用有类型注解的方法
result2 = NodeWithAnnotation.from_list([1, 2, 3])
# ✅ IDE 知道 result2 是 NodeWithAnnotation | None
# ✅ 类型检查器可以检查类型错误
# ✅ 开发者一眼就能看出返回值类型

if result2 is not None:
    print(f"result2.value = {result2.value}")  # IDE 知道有这个属性

print()

# ============================================================
# 类型注解的实际好处
# ============================================================

print("=" * 60)
print("类型注解的实际好处")
print("=" * 60)

def process_node(node: Node | None) -> int:
    """
    这个函数接收 Node | None
    
    因为有类型注解：
    1. 调用者知道应该传入什么类型
    2. IDE 可以提供参数提示
    3. 类型检查器可以检查类型错误
    """
    if node is None:
        return 0
    return node.value  # ✅ IDE 知道 node 有 .value 属性

# 调用
node = Node.from_list([1, 2, 3])
value = process_node(node)  # ✅ IDE 知道应该传入 Node | None
print(f"process_node 返回：{value}")

print()

# ============================================================
# 关键理解：调用方式 vs 返回类型
# ============================================================

print("=" * 60)
print("关键理解：调用方式 vs 返回类型")
print("=" * 60)

print("""
1. 调用方式（如何调用）：
   Node.from_list([1, 2, 3])  ← 通过类调用（类方法）
   
2. 返回类型（返回什么）：
   -> 'Node' | None  ← 返回 Node 实例或 None
   
3. 两者是独立的：
   - 调用方式：决定如何调用方法（类方法 vs 实例方法）
   - 返回类型：决定方法返回什么（实例、类、None 等）
   
4. 类型注解描述的是返回类型，不是调用方式：
   - 即使通过类调用，返回的仍然是实例
   - 类型注解告诉调用者：返回值是 Node 实例
   - 这样调用者就知道可以使用 .value、.next 等属性
""")

# 实际例子
node = Node.from_list([1, 2, 3])  # 通过类调用
print(f"node 是实例：{isinstance(node, Node)}")  # True
print(f"node.value = {node.value}")  # 可以使用实例属性
print(f"node.get_value() = {node.get_value()}")  # 可以调用实例方法

print()

# ============================================================
# 总结
# ============================================================

print("=" * 60)
print("总结")
print("=" * 60)

print("""
✅ 类型注解非常有用，即使通过类方法调用：

1. 描述返回值类型：
   - 告诉调用者方法返回什么类型
   - 帮助理解代码

2. IDE 支持：
   - 代码补全
   - 类型提示
   - 错误检查

3. 类型检查：
   - mypy、pylance 等工具可以检查类型错误
   - 提前发现 bug

4. 文档作用：
   - 类型注解就是最好的文档
   - 不需要看实现就知道返回什么

记住：
- 调用方式（类方法/实例方法）≠ 返回类型
- 类方法可以返回实例
- 类型注解描述返回类型，不是调用方式
""")

