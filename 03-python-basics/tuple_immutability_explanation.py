"""
元组不可变性和 __add__ 方法的详细解释
"""

a = (10, 'alpha', [1, 2])
b = (10, 'alpha', [1, 2])

print("=" * 60)
print("1. 问题：为什么 a.__add__(b) 后，a 没有改变？")
print("=" * 60)

print(f"原始 a: {a}")
print(f"原始 b: {b}")
print(f"a 的 id: {id(a)}")

print("\n执行 a.__add__(b)...")
result = a.__add__(b)  # 注意：这里保存了返回值

print(f"\n执行后 a: {a}")
print(f"执行后 a 的 id: {id(a)}")  # a 的地址没有改变
print(f"返回值 result: {result}")
print(f"返回值 result 的 id: {id(result)}")  # 返回的是新对象

print("\n" + "=" * 60)
print("2. 关键发现")
print("=" * 60)
print(f"a is result: {a is result}")  # False，它们是不同的对象
print(f"a == result: {a == result}")  # False，因为长度不同

print("\n" + "=" * 60)
print("3. 为什么 a 没有改变？")
print("=" * 60)
print("""
原因：
1. 元组是不可变的（immutable）对象
2. __add__ 方法不会修改原元组，而是创建一个新的元组
3. 新元组包含原元组和另一个元组的所有元素
4. 原元组 a 保持不变

类比：
- 就像字符串：s = "hello"; s + " world" 不会改变 s
- 必须赋值：s = s + " world" 才能改变 s
""")

print("\n" + "=" * 60)
print("4. 正确的使用方式")
print("=" * 60)

# 方式1：使用 + 操作符（推荐）
a1 = (10, 'alpha', [1, 2])
b1 = (10, 'alpha', [1, 2])
a1 = a1 + b1  # 或者 a1 += b1
print(f"方式1 (使用 +): a1 = {a1}")

# 方式2：使用 __add__ 并赋值
a2 = (10, 'alpha', [1, 2])
b2 = (10, 'alpha', [1, 2])
a2 = a2.__add__(b2)
print(f"方式2 (使用 __add__ 并赋值): a2 = {a2}")

# 方式3：直接使用返回值
a3 = (10, 'alpha', [1, 2])
b3 = (10, 'alpha', [1, 2])
result3 = a3.__add__(b3)
print(f"方式3 (保存返回值): result3 = {result3}")
print(f"a3 仍然是: {a3}")

print("\n" + "=" * 60)
print("5. 验证元组的不可变性")
print("=" * 60)

try:
    a_test = (1, 2, 3)
    a_test[0] = 99  # 尝试修改元组
except TypeError as e:
    print(f"尝试修改元组会报错: {e}")

print("\n但是，元组中的可变对象（如列表）可以被修改：")
a_mutable = (1, 2, [3, 4])
print(f"修改前: {a_mutable}")
a_mutable[2].append(5)  # 可以修改列表
print(f"修改后: {a_mutable}")
print("注意：元组本身没有改变（id 不变），但列表的内容改变了")

print("\n" + "=" * 60)
print("6. 总结")
print("=" * 60)
print("""
关键点：
1. 元组是不可变的，不能直接修改
2. __add__ 方法返回新元组，不修改原元组
3. 必须将返回值赋给变量才能"更新"元组
4. 使用 + 操作符更简洁：a = a + b 或 a += b
5. 元组中的可变对象（如列表）仍然可以被修改
""")


