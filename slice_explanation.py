"""
Python 切片机制详解

解释为什么自定义类可以使用 [] 切片操作
"""

# ============================================================
# 关键：__getitem__ 魔法方法
# ============================================================

class FrenchDeck:
    def __init__(self):
        self._cards = list(range(52))  # 简化示例
    
    def __getitem__(self, position):
        """
        当使用 deck[index] 或 deck[start:end] 时，
        Python 会自动调用这个方法
        """
        return self._cards[position]

deck = FrenchDeck()

# ============================================================
# 1. 普通索引访问
# ============================================================
print("1. 普通索引访问:")
print(f"   deck[0] = {deck[0]}")
print(f"   Python 实际调用: deck.__getitem__(0)")
print()

# ============================================================
# 2. 切片访问（你的问题）
# ============================================================
print("2. 切片访问:")
print(f"   deck[:3] = {deck[:3]}")
print(f"   Python 实际调用: deck.__getitem__(slice(None, 3, None))")
print()

# ============================================================
# 3. 查看 slice 对象
# ============================================================
print("3. slice 对象详解:")
print(f"   :3 会被转换为: slice(None, 3, None)")
print(f"   slice(None, 3, None) = {slice(None, 3, None)}")
print(f"   slice 对象类型: {type(slice(None, 3, None))}")
print()

# ============================================================
# 4. 手动创建 slice 对象
# ============================================================
print("4. 手动创建 slice 对象:")
my_slice = slice(None, 3, None)
print(f"   my_slice = {my_slice}")
print(f"   deck[my_slice] = {deck[my_slice]}")
print(f"   等价于: deck[:3]")
print()

# ============================================================
# 5. 验证 __getitem__ 接收的参数
# ============================================================
print("5. 验证 __getitem__ 接收的参数:")

class DebugDeck:
    def __init__(self):
        self._cards = list(range(10))
    
    def __getitem__(self, position):
        print(f"   __getitem__ 被调用，参数类型: {type(position)}")
        print(f"   参数值: {position}")
        if isinstance(position, slice):
            print(f"   这是一个 slice 对象:")
            print(f"     start = {position.start}")
            print(f"     stop = {position.stop}")
            print(f"     step = {position.step}")
        return self._cards[position]

debug_deck = DebugDeck()
print("   使用 deck[5]:")
result1 = debug_deck[5]
print()

print("   使用 deck[:3]:")
result2 = debug_deck[:3]
print()

print("   使用 deck[1:5:2]:")
result3 = debug_deck[1:5:2]
print()

# ============================================================
# 6. 为什么不需要"定义 slice 对象"？
# ============================================================
print("6. 为什么不需要'定义 slice 对象'？")
print("""
   答案：Python 自动处理！
   
   当你写 deck[:3] 时：
   1. Python 解析器识别切片语法 [:3]
   2. 自动创建 slice(None, 3, None) 对象
   3. 调用 deck.__getitem__(slice(None, 3, None))
   4. __getitem__ 方法接收这个 slice 对象
   5. 方法内部使用 self._cards[position]，列表支持切片
   6. 返回切片结果
   
   整个过程是自动的，不需要手动创建 slice 对象！
""")

# ============================================================
# 7. 如果 __getitem__ 不处理 slice 会怎样？
# ============================================================
print("7. 如果 __getitem__ 不处理 slice 会怎样？")

class BadDeck:
    def __init__(self):
        self._cards = list(range(10))
    
    def __getitem__(self, position):
        # ❌ 错误：只处理整数索引，不处理 slice
        if isinstance(position, int):
            return self._cards[position]
        else:
            raise TypeError(f"不支持的类型: {type(position)}")

bad_deck = BadDeck()
print(f"   bad_deck[5] = {bad_deck[5]}")  # ✅ 可以工作
try:
    print(f"   bad_deck[:3] = ", end="")
    print(bad_deck[:3])  # ❌ 会报错
except TypeError as e:
    print(f"❌ 错误: {e}")
print()

# ============================================================
# 8. 正确的做法（你的代码）
# ============================================================
print("8. 正确的做法（你的代码）:")
print("""
   def __getitem__(self, position):
       return self._cards[position]
   
   为什么这样就能工作？
   - position 可以是 int（索引）或 slice（切片）
   - self._cards 是列表，列表的 [] 操作符支持：
     * 整数索引: cards[0]
     * 切片: cards[:3]
   - 所以直接返回 self._cards[position] 就能同时支持两种操作
""")

# ============================================================
# 9. 完整的切片语法示例
# ============================================================
print("9. 完整的切片语法示例:")
deck = FrenchDeck()
deck._cards = list(range(10))  # 重置为 0-9

print(f"   deck[:3]     = {deck[:3]}")      # 前3个
print(f"   deck[3:]     = {deck[3:]}")      # 从第3个开始
print(f"   deck[1:5]    = {deck[1:5]}")     # 第1到第4个
print(f"   deck[::2]    = {deck[::2]}")     # 每隔一个
print(f"   deck[::-1]   = {deck[::-1]}")    # 反转
print(f"   deck[1:8:2]  = {deck[1:8:2]}")   # 从1到7，每隔一个

print("\n对应的 slice 对象:")
print(f"   :3      -> slice(None, 3, None)")
print(f"   3:      -> slice(3, None, None)")
print(f"   1:5     -> slice(1, 5, None)")
print(f"   ::2     -> slice(None, None, 2)")
print(f"   ::-1    -> slice(None, None, -1)")
print(f"   1:8:2   -> slice(1, 8, 2)")

