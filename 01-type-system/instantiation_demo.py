"""
演示：类方法中如何创建实例
"""

from __future__ import annotations

class Node:
    def __init__(self, value: int):
        print(f"  🔵 __init__ 被调用：创建实例，value={value}, id={id(self)}")
        self.value = value
    
    @classmethod
    def from_list(cls, values: list[int], circular: bool = False) -> 'Node' | None:
        print(f"🟢 from_list 被调用：cls={cls}")
        
        if not values:
            return None
        
        # 关键：这里手动创建实例
        nodes = []
        for value in values:
            print(f"  🟡 准备调用 cls({value}) 创建实例...")
            node = cls(value)  # ← 这里会调用 __init__ 创建实例！
            print(f"  ✅ 实例创建完成：node={node}, value={node.value}")
            nodes.append(node)
        
        # 连接节点
        for i in range(len(nodes) - 1):
            nodes[i].next = nodes[i + 1]
        
        if circular and len(nodes) > 1:
            nodes[-1].next = nodes[0]
        
        print(f"🔴 返回第一个实例：{nodes[0]}")
        return nodes[0]
    
    def __repr__(self):
        return f"Node(value={self.value})"

# ============================================================
# 演示 1：类方法创建实例的过程
# ============================================================

print("=" * 60)
print("演示 1：类方法创建实例的过程")
print("=" * 60)

print("\n调用：Node.from_list([1, 2, 3])")
print("-" * 60)
head = Node.from_list([1, 2, 3])

print(f"\n结果：head = {head}")
print(f"head.value = {head.value}")
print(f"head.next = {head.next}")
print()

# ============================================================
# 演示 2：对比直接实例化和类方法
# ============================================================

print("=" * 60)
print("演示 2：对比直接实例化和类方法")
print("=" * 60)

print("\n方式 A：直接实例化")
print("-" * 60)
node1 = Node(10)
print(f"node1 = {node1}")

print("\n方式 B：通过类方法")
print("-" * 60)
node2 = Node.from_list([20])
print(f"node2 = {node2}")

print("\n对比：")
print(f"  node1 类型：{type(node1)}")
print(f"  node2 类型：{type(node2)}")
print(f"  都是实例：{isinstance(node1, Node) and isinstance(node2, Node)}")
print()

# ============================================================
# 演示 3：cls(...) 等价于 Node(...)
# ============================================================

print("=" * 60)
print("演示 3：cls(...) 等价于 Node(...)")
print("=" * 60)

class TestNode:
    def __init__(self, value: int):
        self.value = value
    
    @classmethod
    def create_with_cls(cls, value: int):
        print(f"使用 cls({value}) 创建实例")
        return cls(value)  # 使用 cls
    
    @classmethod
    def create_with_classname(cls, value: int):
        print(f"使用 TestNode({value}) 创建实例")
        return TestNode(value)  # 使用类名
    
    def __repr__(self):
        return f"TestNode(value={self.value})"

node_a = TestNode.create_with_cls(100)
node_b = TestNode.create_with_classname(200)

print(f"\nnode_a = {node_a}")
print(f"node_b = {node_b}")
print(f"两者类型相同：{type(node_a) == type(node_b)}")
print()

# ============================================================
# 演示 4：实例化的完整过程
# ============================================================

print("=" * 60)
print("演示 4：实例化的完整过程")
print("=" * 60)

print("""
当你调用 Node.from_list([1, 2, 3]) 时：

1. Python 调用 from_list 方法
   - cls = Node（类方法自动传入）

2. 在方法内部执行：nodes = [cls(value) for value in values]
   对于 value=1：
   - cls(1) → Node(1)
   - Python 调用 Node.__new__(Node, 1) 创建实例对象
   - Python 调用 Node.__init__(新实例, 1) 初始化实例
   - 返回实例
   
   对于 value=2：
   - cls(2) → Node(2)
   - 重复上述过程
   
   对于 value=3：
   - cls(3) → Node(3)
   - 重复上述过程

3. 返回 nodes[0]（第一个实例）

关键：不是 Python 自动实例化，而是在代码中手动调用 cls(...) 创建的！
""")

# ============================================================
# 总结
# ============================================================

print("=" * 60)
print("总结")
print("=" * 60)

print("""
✅ 关键理解：

1. 类方法不会自动创建实例
   - 需要在方法内部手动调用 cls(...)

2. cls(...) 等价于 Node(...)
   - 都会调用 __init__ 创建实例

3. 实例化过程：
   cls(value) → __new__ → __init__ → 返回实例

4. 类方法的作用：
   - 提供另一种创建实例的方式
   - 封装复杂的创建逻辑
   - 解决前向引用等问题

记住：不是"自动"，是"手动"在代码中调用 cls(...) 创建的！
""")



