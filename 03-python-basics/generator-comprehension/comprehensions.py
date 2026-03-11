"""
Python 推导式（Comprehensions）详解

推导式是 Python 中用于快速创建序列的简洁语法
包括：列表推导式、字典推导式、集合推导式
"""

# ============================================================
# 案例 1: 列表推导式基础
# ============================================================
print("=" * 60)
print("案例 1: 列表推导式基础")
print("=" * 60)

# 传统方式创建列表
print("传统方式（for 循环）:")
squares_old = []
for i in range(10):
    squares_old.append(i ** 2)
print(f"平方数: {squares_old}")

# 列表推导式
print("\n列表推导式:")
squares = [i ** 2 for i in range(10)]
print(f"平方数: {squares}")

# 带条件的列表推导式
print("\n带条件的推导式（只要偶数的平方）:")
even_squares = [i ** 2 for i in range(10) if i % 2 == 0]
print(f"偶数的平方: {even_squares}")

# if-else 在推导式中
print("\n使用 if-else:")
odd_even = ["偶数" if i % 2 == 0 else "奇数" for i in range(10)]
print(f"奇偶性: {odd_even}")


# ============================================================
# 案例 2: 嵌套列表推导式
# ============================================================
print("\n" + "=" * 60)
print("案例 2: 嵌套列表推导式")
print("=" * 60)

# 二维矩阵
print("创建 3x4 矩阵:")
matrix = [[i * 4 + j for j in range(4)] for i in range(3)]
for row in matrix:
    print(f"  {row}")

# 矩阵转置
print("\n矩阵转置:")
transposed = [[row[i] for row in matrix] for i in range(4)]
for row in transposed:
    print(f"  {row}")

# 扁平化嵌套列表
print("\n扁平化嵌套列表:")
nested = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print(f"原始: {nested}")
flat = [num for sublist in nested for num in sublist]
print(f"扁平化: {flat}")


# ============================================================
# 案例 3: 字典推导式
# ============================================================
print("\n" + "=" * 60)
print("案例 3: 字典推导式")
print("=" * 60)

# 基础字典推导式
print("创建平方数字典:")
squares_dict = {i: i ** 2 for i in range(6)}
print(f"  {squares_dict}")

# 从两个列表创建字典
print("\n从两个列表创建字典:")
keys = ['a', 'b', 'c', 'd']
values = [1, 2, 3, 4]
dict_from_lists = {k: v for k, v in zip(keys, values)}
print(f"  {dict_from_lists}")

# 带条件的字典推导式
print("\n筛选字典:")
prices = {'apple': 3.5, 'banana': 2.0, 'orange': 4.5, 'pear': 3.0}
print(f"原始价格: {prices}")
expensive = {k: v for k, v in prices.items() if v > 3.0}
print(f"贵的水果: {expensive}")

# 字典键值互换
print("\n键值互换:")
reversed_dict = {v: k for k, v in dict_from_lists.items()}
print(f"原始: {dict_from_lists}")
print(f"互换: {reversed_dict}")


# ============================================================
# 案例 4: 集合推导式
# ============================================================
print("\n" + "=" * 60)
print("案例 4: 集合推导式")
print("=" * 60)

# 基础集合推导式
print("创建平方数集合:")
squares_set = {i ** 2 for i in range(10)}
print(f"  {squares_set}")

# 去重
print("\n去重文本中的字符:")
text = "hello world"
unique_chars = {char for char in text if char != ' '}
print(f"原始: '{text}'")
print(f"唯一字符: {unique_chars}")

# 集合推导式的去重特性
print("\n自动去重:")
duplicates = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
print(f"原始列表: {duplicates}")
unique_set = {x for x in duplicates}
print(f"去重后: {unique_set}")


# ============================================================
# 案例 5: 多条件推导式
# ============================================================
print("\n" + "=" * 60)
print("案例 5: 多条件推导式")
print("=" * 60)

# 多个 if 条件（AND）
print("找出能被2和3整除的数:")
divisible = [i for i in range(50) if i % 2 == 0 if i % 3 == 0]
print(f"  {divisible}")

# 多个 for 循环（笛卡尔积）
print("\n笛卡尔积:")
colors = ['red', 'blue']
sizes = ['S', 'M', 'L']
combinations = [(color, size) for color in colors for size in sizes]
print(f"  {combinations}")

# 复杂条件
print("\n复杂条件（FizzBuzz）:")
fizzbuzz = [
    "FizzBuzz" if i % 15 == 0 else
    "Fizz" if i % 3 == 0 else
    "Buzz" if i % 5 == 0 else
    i
    for i in range(1, 21)
]
print(f"  {fizzbuzz}")


# ============================================================
# 案例 6: 推导式 vs 传统循环（性能对比）
# ============================================================
print("\n" + "=" * 60)
print("案例 6: 性能对比")
print("=" * 60)

import time

# 方法1: 传统循环
start = time.time()
result1 = []
for i in range(100000):
    if i % 2 == 0:
        result1.append(i ** 2)
time1 = (time.time() - start) * 1000

# 方法2: 列表推导式
start = time.time()
result2 = [i ** 2 for i in range(100000) if i % 2 == 0]
time2 = (time.time() - start) * 1000

print(f"传统循环: {time1:.2f}ms")
print(f"列表推导式: {time2:.2f}ms")
print(f"推导式快了: {time1 / time2:.2f}x")


# ============================================================
# 案例 7: 实用示例
# ============================================================
print("\n" + "=" * 60)
print("案例 7: 实用示例")
print("=" * 60)

# 处理字符串
print("1. 字符串处理:")
sentence = "Hello World Python"
words = sentence.split()
print(f"原始: {words}")
lowercase = [word.lower() for word in words]
print(f"小写: {lowercase}")
lengths = {word: len(word) for word in words}
print(f"长度: {lengths}")

# 过滤数据
print("\n2. 过滤数据:")
data = [
    {"name": "Alice", "age": 25, "city": "Beijing"},
    {"name": "Bob", "age": 17, "city": "Shanghai"},
    {"name": "Charlie", "age": 30, "city": "Beijing"},
    {"name": "David", "age": 22, "city": "Shenzhen"}
]
adults = [person["name"] for person in data if person["age"] >= 18]
print(f"成年人: {adults}")
beijing_people = [person["name"] for person in data if person["city"] == "Beijing"]
print(f"北京人: {beijing_people}")

# 数学运算
print("\n3. 数学运算:")
numbers = [1, 2, 3, 4, 5]
print(f"原始: {numbers}")
doubled = [n * 2 for n in numbers]
print(f"翻倍: {doubled}")
sum_result = sum([n ** 2 for n in numbers])
print(f"平方和: {sum_result}")


# ============================================================
# 案例 8: 推导式的陷阱
# ============================================================
print("\n" + "=" * 60)
print("案例 8: 推导式的陷阱和注意事项")
print("=" * 60)

# 陷阱1: 过度嵌套（可读性差）
print("❌ 不推荐：过度嵌套")
print("[[i*j for j in range(3)] for i in range(3) if i > 0]")

print("\n✅ 推荐：使用普通循环或拆分")
result = []
for i in range(3):
    if i > 0:
        row = [i * j for j in range(3)]
        result.append(row)
print(f"结果: {result}")

# 陷阱2: 副作用
print("\n❌ 不要在推导式中产生副作用:")
print("# 不要这样做：[print(i) for i in range(5)]")
print("# 应该使用: for i in range(5): print(i)")

# 陷阱3: 内存占用
print("\n⚠️  大数据时注意内存:")
print("# 推导式会立即创建整个列表")
print("# 对于大数据，考虑使用生成器（下一个文件）")


# ============================================================
# 总结
# ============================================================
print("\n" + "=" * 60)
print("推导式总结")
print("=" * 60)
print("""
📌 三种推导式:
┌──────────────────┬────────────────────────────────┐
│ 列表推导式       │ [expr for item in iterable]    │
│ 字典推导式       │ {k: v for item in iterable}    │
│ 集合推导式       │ {expr for item in iterable}    │
└──────────────────┴────────────────────────────────┘

✅ 优点:
1. 简洁、可读性强
2. 性能通常比等效的 for 循环好
3. 功能强大，支持条件和嵌套
4. Pythonic 风格

⚠️  何时不使用:
1. 逻辑太复杂（超过2层嵌套）
2. 需要处理异常
3. 有副作用（print、文件操作等）
4. 大数据集（考虑生成器）

💡 基本语法:
# 基础
[expr for item in iterable]

# 带条件
[expr for item in iterable if condition]

# if-else
[expr1 if condition else expr2 for item in iterable]

# 多层循环
[expr for i in iter1 for j in iter2]

# 多个条件（AND）
[expr for item in iterable if cond1 if cond2]

🎯 使用场景:
- 数据转换和映射
- 数据过滤
- 数据聚合
- 列表扁平化
- 数学计算
- 字符串处理
""")