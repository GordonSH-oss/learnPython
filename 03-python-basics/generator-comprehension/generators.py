"""
Python 生成器（Generators）详解

生成器是一种特殊的迭代器，使用 yield 关键字
延迟计算，节省内存，适合处理大数据集
"""

import sys

# ============================================================
# 案例 1: 生成器基础 - yield 关键字
# ============================================================
print("=" * 60)
print("案例 1: 生成器基础")
print("=" * 60)

def simple_generator():
    """最简单的生成器"""
    print("  → 生成 1")
    yield 1
    print("  → 生成 2")
    yield 2
    print("  → 生成 3")
    yield 3
    print("  → 结束")

print("创建生成器对象:")
gen = simple_generator()
print(f"类型: {type(gen)}")
print(f"生成器对象: {gen}")

print("\n逐个获取值:")
print(f"第一次 next(): {next(gen)}")
print(f"第二次 next(): {next(gen)}")
print(f"第三次 next(): {next(gen)}")

try:
    print(f"第四次 next(): {next(gen)}")
except StopIteration:
    print("❌ StopIteration: 生成器已耗尽")


# ============================================================
# 案例 2: 生成器表达式（Generator Expression）
# ============================================================
print("\n" + "=" * 60)
print("案例 2: 生成器表达式 vs 列表推导式")
print("=" * 60)

# 列表推导式（立即创建整个列表）
print("列表推导式:")
list_comp = [i ** 2 for i in range(10)]
print(f"  类型: {type(list_comp)}")
print(f"  值: {list_comp}")
print(f"  内存大小: {sys.getsizeof(list_comp)} bytes")

# 生成器表达式（延迟计算）
print("\n生成器表达式:")
gen_exp = (i ** 2 for i in range(10))  # 注意：圆括号
print(f"  类型: {type(gen_exp)}")
print(f"  对象: {gen_exp}")
print(f"  内存大小: {sys.getsizeof(gen_exp)} bytes")

print("\n遍历生成器:")
for value in gen_exp:
    print(f"  {value}", end=" ")
print()

# 对比大数据的内存占用
print("\n大数据内存对比:")
large_list = [i for i in range(1000000)]
large_gen = (i for i in range(1000000))
print(f"列表: {sys.getsizeof(large_list):,} bytes")
print(f"生成器: {sys.getsizeof(large_gen):,} bytes")
print(f"内存节省: {sys.getsizeof(large_list) / sys.getsizeof(large_gen):.0f}x")


# ============================================================
# 案例 3: 实用生成器函数
# ============================================================
print("\n" + "=" * 60)
print("案例 3: 实用生成器函数")
print("=" * 60)

def fibonacci(n):
    """斐波那契数列生成器"""
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

print("斐波那契数列（前10项）:")
for num in fibonacci(10):
    print(f"  {num}", end=" ")
print()

def countdown(n):
    """倒计时生成器"""
    print(f"倒计时从 {n} 开始...")
    while n > 0:
        yield n
        n -= 1
    print("发射！🚀")

print("\n倒计时:")
for i in countdown(5):
    print(f"  {i}...", end=" ")
print()


# ============================================================
# 案例 4: 无限生成器
# ============================================================
print("\n" + "=" * 60)
print("案例 4: 无限生成器")
print("=" * 60)

def infinite_sequence():
    """无限序列生成器"""
    num = 0
    while True:
        yield num
        num += 1

print("无限序列（前10个）:")
gen = infinite_sequence()
for _ in range(10):
    print(f"  {next(gen)}", end=" ")
print()

def repeat(value):
    """无限重复值"""
    while True:
        yield value

print("\n无限重复（前5个）:")
gen = repeat("Hello")
for _ in range(5):
    print(f"  {next(gen)}", end=" ")
print()


# ============================================================
# 案例 5: 生成器的状态保持
# ============================================================
print("\n" + "=" * 60)
print("案例 5: 生成器保持状态")
print("=" * 60)

def running_average():
    """计算运行平均值的生成器"""
    total = 0
    count = 0
    average = None
    while True:
        value = yield average  # 接收值并返回平均值
        total += value
        count += 1
        average = total / count

print("运行平均值:")
avg_gen = running_average()
next(avg_gen)  # 启动生成器

values = [10, 20, 30, 40, 50]
for value in values:
    avg = avg_gen.send(value)
    print(f"  加入 {value}, 平均值: {avg:.2f}")


# ============================================================
# 案例 6: 生成器管道（Pipeline）
# ============================================================
print("\n" + "=" * 60)
print("案例 6: 生成器管道")
print("=" * 60)

def number_generator():
    """生成数字"""
    for i in range(1, 11):
        yield i

def square_generator(numbers):
    """平方"""
    for num in numbers:
        yield num ** 2

def filter_even(numbers):
    """过滤偶数"""
    for num in numbers:
        if num % 2 == 0:
            yield num

# 构建管道
print("管道: 数字 → 平方 → 过滤偶数")
pipeline = filter_even(square_generator(number_generator()))
result = list(pipeline)
print(f"结果: {result}")


# ============================================================
# 案例 7: 处理大文件
# ============================================================
print("\n" + "=" * 60)
print("案例 7: 处理大文件（生成器的优势）")
print("=" * 60)

def read_large_file(file_path):
    """
    逐行读取大文件（不会一次性加载到内存）
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                yield line.strip()
    except FileNotFoundError:
        print(f"  文件不存在: {file_path}")

# 演示概念
print("使用生成器读取文件的优势:")
print("  ✅ 内存效率高（逐行读取）")
print("  ✅ 适合处理大文件（GB级别）")
print("  ✅ 可以提前终止")
print("\n示例代码:")
print("""
def read_large_file(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            yield line.strip()

# 使用
for line in read_large_file('huge_file.txt'):
    if 'target' in line:
        print(line)
        break  # 可以提前终止，不需要读完整个文件
""")


# ============================================================
# 案例 8: yield from（Python 3.3+）
# ============================================================
print("\n" + "=" * 60)
print("案例 8: yield from 委托生成器")
print("=" * 60)

def inner_generator():
    """内部生成器"""
    yield 1
    yield 2
    yield 3

def outer_generator_old():
    """传统方式：手动迭代"""
    for value in inner_generator():
        yield value

def outer_generator_new():
    """新方式：使用 yield from"""
    yield from inner_generator()

print("传统方式:")
print(f"  {list(outer_generator_old())}")

print("\nyield from 方式:")
print(f"  {list(outer_generator_new())}")

# 扁平化嵌套列表
def flatten(nested_list):
    """扁平化嵌套列表"""
    for item in nested_list:
        if isinstance(item, list):
            yield from flatten(item)  # 递归
        else:
            yield item

print("\n扁平化嵌套列表:")
nested = [1, [2, 3, [4, 5]], 6, [7, [8, 9]]]
print(f"原始: {nested}")
print(f"扁平化: {list(flatten(nested))}")


# ============================================================
# 案例 9: 生成器方法：send(), throw(), close()
# ============================================================
print("\n" + "=" * 60)
print("案例 9: 生成器的高级方法")
print("=" * 60)

def echo_generator():
    """回显生成器"""
    try:
        while True:
            value = yield
            if value is not None:
                print(f"  → 收到: {value}")
    except GeneratorExit:
        print("  → 生成器关闭")

print("1. send() 方法:")
gen = echo_generator()
next(gen)  # 启动生成器
gen.send("Hello")
gen.send("World")
gen.close()  # 关闭生成器

def exception_handler():
    """处理异常的生成器"""
    try:
        while True:
            value = yield
            print(f"  → 处理: {value}")
    except ValueError as e:
        print(f"  → 捕获异常: {e}")
        yield "已恢复"

print("\n2. throw() 方法:")
gen = exception_handler()
next(gen)
gen.send("正常数据")
result = gen.throw(ValueError, "测试异常")
print(f"  → 返回值: {result}")


# ============================================================
# 案例 10: 生成器 vs 列表的性能对比
# ============================================================
print("\n" + "=" * 60)
print("案例 10: 性能和内存对比")
print("=" * 60)

import time

def list_approach(n):
    """列表方式"""
    return [i ** 2 for i in range(n)]

def generator_approach(n):
    """生成器方式"""
    return (i ** 2 for i in range(n))

n = 1000000

# 创建时间
start = time.time()
lst = list_approach(n)
list_time = (time.time() - start) * 1000

start = time.time()
gen = generator_approach(n)
gen_time = (time.time() - start) * 1000

print(f"创建 {n:,} 个元素:")
print(f"  列表: {list_time:.2f}ms, 内存: {sys.getsizeof(lst):,} bytes")
print(f"  生成器: {gen_time:.4f}ms, 内存: {sys.getsizeof(gen):,} bytes")

# 只取前10个
print(f"\n只取前10个元素:")
start = time.time()
lst = list_approach(n)
result1 = lst[:10]
list_time = (time.time() - start) * 1000

start = time.time()
gen = generator_approach(n)
result2 = [next(gen) for _ in range(10)]
gen_time = (time.time() - start) * 1000

print(f"  列表方式: {list_time:.2f}ms")
print(f"  生成器方式: {gen_time:.4f}ms")
print(f"  生成器快了: {list_time / gen_time:.0f}x")


# ============================================================
# 总结
# ============================================================
print("\n" + "=" * 60)
print("生成器总结")
print("=" * 60)
print("""
📌 生成器的两种创建方式:
┌─────────────────────┬──────────────────────────────┐
│ 生成器函数          │ def func(): yield value      │
│ 生成器表达式        │ (expr for item in iterable)  │
└─────────────────────┴──────────────────────────────┘

✅ 优点:
1. 内存效率高（延迟计算，不一次性占用内存）
2. 适合处理大数据集或无限序列
3. 可以在循环中间暂停和恢复
4. 支持管道式处理
5. 创建快速（不立即计算）

⚠️  注意事项:
1. 只能遍历一次（迭代器耗尽后不能重用）
2. 不支持索引访问（不能 gen[0]）
3. 不支持 len()
4. 调试相对困难

💡 核心方法:
- next(gen)      # 获取下一个值
- gen.send(val)  # 发送值给生成器
- gen.throw(exc) # 抛出异常
- gen.close()    # 关闭生成器

🎯 使用场景:
- 处理大文件（逐行读取）
- 数据流处理（实时数据）
- 数学序列（斐波那契、素数等）
- 无限序列
- 管道式数据处理
- 节省内存的数据转换

📚 关键字:
- yield        # 产生值并暂停
- yield from   # 委托给子生成器
- return       # 终止生成器（Python 3.3+）
""")