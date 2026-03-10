"""
元组相等性比较的详细解释
"""

# 原始代码
a = (10, 'alpha', [1, 2])
b = (10, 'alpha', [1, 2])

print("=" * 60)
print("1. 元组相等性比较 (==)")
print("=" * 60)
print(f"a == b: {a == b}")

print("\n" + "=" * 60)
print("2. 元组身份比较 (is) - 比较是否是同一个对象")
print("=" * 60)
print(f"a is b: {a is b}")  # False，因为它们是不同的元组对象

print("\n" + "=" * 60)
print("3. 元组中元素的地址情况")
print("=" * 60)

# 检查元组中每个元素的 id（地址）
print(f"id(a): {id(a)}")
print(f"id(b): {id(b)}")
print(f"a 和 b 是不同的对象: {a is not b}")

print("\n元组 a 中元素的 id:")
for i, item in enumerate(a):
    print(f"  a[{i}] = {item}, id = {id(item)}")

print("\n元组 b 中元素的 id:")
for i, item in enumerate(b):
    print(f"  b[{i}] = {item}, id = {id(item)}")

print("\n" + "=" * 60)
print("4. 关键发现：元素的地址比较")
print("=" * 60)
print(f"a[0] is b[0] (整数 10): {a[0] is b[0]}")
print(f"a[1] is b[1] (字符串 'alpha'): {a[1] is b[1]}")
print(f"a[2] is b[2] (列表 [1, 2]): {a[2] is b[2]}")

print("\n" + "=" * 60)
print("5. 为什么 a == b 返回 True？")
print("=" * 60)
print("""
Python 的 == 操作符对于元组来说：
1. 首先比较元组的长度
2. 然后递归地比较每个对应位置的元素

对于每个元素：
- 整数和字符串：== 比较的是值，不是地址
- 列表：== 比较的是列表的内容，不是地址
  （即使两个列表是不同的对象，只要内容相同，== 就返回 True）

所以：
- a[0] == b[0]  # 10 == 10 → True
- a[1] == b[1]  # 'alpha' == 'alpha' → True  
- a[2] == b[2]  # [1, 2] == [1, 2] → True（比较内容）

因此 a == b 返回 True
""")

print("\n" + "=" * 60)
print("6. 验证：修改列表后元组相等性的变化")
print("=" * 60)
print(f"修改前: a == b = {a == b}")
print(f"修改前: a[2] is b[2] = {a[2] is b[2]}")

# 修改 a 中的列表
a[2].append(3)
print(f"\n执行 a[2].append(3) 后:")
print(f"a = {a}")
print(f"b = {b}")
print(f"a == b = {a == b}")  # 现在应该返回 False
print(f"a[2] = {a[2]}")
print(f"b[2] = {b[2]}")

print("\n" + "=" * 60)
print("7. 总结")
print("=" * 60)
print("""
关键点：
1. 元组存储的是对象的引用（地址）
2. == 比较的是值，不是地址
3. 对于列表这样的可变对象，== 会比较内容，不是身份
4. 即使两个列表是不同的对象（不同地址），只要内容相同，== 就返回 True
5. 使用 is 或 id() 才能比较对象的身份（地址）
""")


