"""
Python 前向引用示例
演示为什么类型注解中需要加引号
"""

from __future__ import annotations  # 必须在文件最顶部

# ============================================================
# 情况 1：没有 from __future__ import annotations 的情况
# 注意：由于文件顶部已经有了，这里演示的是如果去掉会怎样
# ============================================================

print("=" * 60)
print("情况 1：没有 from __future__ import annotations")
print("=" * 60)

try:
    # ❌ 这会报错：NameError: name 'Node' is not defined
    class NodeWithoutFuture:
        def __init__(self, value: int, next: 'NodeWithoutFuture' | None = None):
            # ✅ 必须加引号
            self.value = value
            self.next = next
        
        @classmethod
        def create(cls) -> 'NodeWithoutFuture':  # ✅ 必须加引号
            return cls(1)
    
    print("✅ 成功：使用引号可以工作")
    node = NodeWithoutFuture.create()
    print(f"   创建的节点：{node.value}")
    
except NameError as e:
    print(f"❌ 错误：{e}")

print()

# ============================================================
# 情况 2：有 from __future__ import annotations
# ============================================================

print("=" * 60)
print("情况 2：有 from __future__ import annotations（当前文件的情况）")
print("=" * 60)

class NodeWithFuture:
    def __init__(self, value: int, next: NodeWithFuture | None = None):
        # ⚠️ 可以不加引号（因为 from __future__ 让所有注解变成字符串）
        self.value = value
        self.next = next
    
    @classmethod
    def create(cls) -> NodeWithFuture:  # ⚠️ 可以不加引号
        return cls(1)
    
    @classmethod
    def create_with_quote(cls) -> 'NodeWithFuture':  # ✅ 加引号（推荐）
        return cls(1)

print("✅ 成功：两种写法都可以")
node1 = NodeWithFuture.create()
node2 = NodeWithFuture.create_with_quote()
print(f"   不加引号：{node1.value}")
print(f"   加引号：{node2.value}")
print()

# ============================================================
# 情况 3：相互引用的类
# ============================================================

print("=" * 60)
print("情况 3：相互引用的类")
print("=" * 60)

class Parent:
    def get_child(self) -> 'Child':  # ✅ 引用另一个类，需要引号
        return Child()
    
    def get_self(self) -> 'Parent':  # ✅ 引用自己，需要引号
        return self

class Child:
    def get_parent(self) -> 'Parent':  # ✅ 引用另一个类，需要引号
        return Parent()

parent = Parent()
child = parent.get_child()
print(f"✅ 成功：Parent -> Child -> Parent")
print(f"   parent.get_child() = {type(child).__name__}")
print()

# ============================================================
# 情况 4：递归类型（链表）
# ============================================================

print("=" * 60)
print("情况 4：递归类型（链表）")
print("=" * 60)

class LinkedList:
    def __init__(self, value: int, next: 'LinkedList' | None = None):
        # ✅ next 指向另一个 LinkedList，需要前向引用
        self.value = value
        self.next = next
    
    def get_next(self) -> 'LinkedList' | None:
        # ✅ 返回类型是 LinkedList，需要前向引用
        return self.next
    
    def copy(self) -> 'LinkedList':
        # ✅ 返回当前类的实例，需要前向引用
        return LinkedList(self.value, self.next)

node1 = LinkedList(1)
node2 = LinkedList(2, node1)
print(f"✅ 成功：创建递归链表")
print(f"   node2.value = {node2.value}")
print(f"   node2.next.value = {node2.next.value}")
print()

# ============================================================
# 总结
# ============================================================

print("=" * 60)
print("总结")
print("=" * 60)
print("""
1. 没有 from __future__ import annotations：
   ✅ 必须加引号：-> 'Node'
   ❌ 不加引号会报错：NameError

2. 有 from __future__ import annotations：
   ⚠️ 可以不加引号：-> Node（自动变成字符串）
   ✅ 建议加引号：-> 'Node'（更明确、兼容性更好）

3. 最佳实践：
   - 总是使用 from __future__ import annotations
   - 即使有了 from __future__，也建议加引号
   - 这样代码更明确，兼容性更好

4. 什么时候需要加引号：
   - 类方法返回当前类：-> 'Node'
   - 实例方法返回当前类：-> 'Node'
   - 参数类型是当前类：next: 'Node'
   - 引用其他类（相互引用）：-> 'OtherClass'
""")

