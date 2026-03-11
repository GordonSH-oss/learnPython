# 推导式 vs 生成器：完整对比指南

## 快速识别

```python
# 列表推导式 - 方括号 []
list_comp = [i ** 2 for i in range(10)]

# 生成器表达式 - 圆括号 ()
gen_exp = (i ** 2 for i in range(10))

# 生成器函数 - 使用 yield
def gen_func():
    for i in range(10):
        yield i ** 2
```

## 核心区别

### 1. 立即 vs 延迟计算

```python
# 推导式：立即计算所有值
numbers = [i for i in range(5)]
print(numbers)  # [0, 1, 2, 3, 4] - 已经计算完成

# 生成器：延迟计算（惰性求值）
numbers = (i for i in range(5))
print(numbers)  # <generator object> - 还没有计算
print(list(numbers))  # [0, 1, 2, 3, 4] - 现在才计算
```

**区别说明：**
- 推导式在创建时就计算所有元素
- 生成器只在被访问时才计算元素

### 2. 内存占用

```python
import sys

# 推导式：占用大量内存
large_list = [i for i in range(1000000)]
print(f"列表大小: {sys.getsizeof(large_list):,} bytes")  # ~8,000,000 bytes

# 生成器：占用很小内存
large_gen = (i for i in range(1000000))
print(f"生成器大小: {sys.getsizeof(large_gen):,} bytes")  # ~200 bytes
```

**内存对比表：**

| 元素数量 | 列表推导式 | 生成器表达式 | 内存节省 |
|---------|-----------|-------------|---------|
| 1,000 | ~9 KB | ~200 B | ~45x |
| 10,000 | ~87 KB | ~200 B | ~435x |
| 100,000 | ~824 KB | ~200 B | ~4,120x |
| 1,000,000 | ~8 MB | ~200 B | ~40,000x |

### 3. 可重用性

```python
# 推导式：可以多次遍历
numbers = [i for i in range(5)]
print(list(numbers))  # [0, 1, 2, 3, 4]
print(list(numbers))  # [0, 1, 2, 3, 4] - 可以再次遍历

# 生成器：只能遍历一次
numbers = (i for i in range(5))
print(list(numbers))  # [0, 1, 2, 3, 4]
print(list(numbers))  # [] - 生成器已耗尽
```

**区别说明：**
- 推导式创建的列表可以多次访问
- 生成器只能遍历一次，耗尽后就不能再用

### 4. 支持的操作

```python
# 推导式：支持所有序列操作
numbers = [i for i in range(10)]
print(numbers[5])      # ✅ 索引访问
print(len(numbers))    # ✅ 长度
print(numbers[:3])     # ✅ 切片
print(5 in numbers)    # ✅ 成员测试

# 生成器：只支持迭代
numbers = (i for i in range(10))
# print(numbers[5])    # ❌ TypeError: 不支持索引
# print(len(numbers))  # ❌ TypeError: 不支持 len()
# print(numbers[:3])   # ❌ TypeError: 不支持切片
print(next(numbers))   # ✅ 获取下一个值
```

**操作对比表：**

| 操作 | 列表推导式 | 生成器 |
|-----|----------|-------|
| 索引访问 `[i]` | ✅ | ❌ |
| 切片 `[:]` | ✅ | ❌ |
| `len()` | ✅ | ❌ |
| `in` 成员测试 | ✅ | ✅ |
| 遍历 `for` | ✅ | ✅ |
| `next()` | ❌ | ✅ |
| 多次遍历 | ✅ | ❌ |

### 5. 性能对比

#### 场景1：全量处理

```python
import time

# 生成所有元素并使用
n = 1000000

# 推导式
start = time.time()
result = sum([i ** 2 for i in range(n)])
list_time = time.time() - start

# 生成器
start = time.time()
result = sum((i ** 2 for i in range(n)))
gen_time = time.time() - start

# 结果：差不多（都需要计算所有元素）
```

#### 场景2：提前终止

```python
import time

# 只需要前100个元素
n = 1000000

# 推导式（仍然创建所有元素）
start = time.time()
numbers = [i ** 2 for i in range(n)]
result = numbers[:100]
list_time = time.time() - start

# 生成器（只计算需要的元素）
start = time.time()
gen = (i ** 2 for i in range(n))
result = [next(gen) for _ in range(100)]
gen_time = time.time() - start

# 结果：生成器快很多（只计算100个）
```

**性能总结：**
- **全量处理**：性能相近，但生成器更省内存
- **部分处理**：生成器明显更快（只计算需要的部分）
- **创建时间**：生成器几乎瞬间创建

## 详细对比表

| 特性 | 列表推导式 | 生成器表达式 | 生成器函数 |
|-----|----------|------------|-----------|
| **语法** | `[expr for ...]` | `(expr for ...)` | `def f(): yield` |
| **返回类型** | list/dict/set | generator | generator |
| **计算时机** | 立即 | 延迟 | 延迟 |
| **内存占用** | 大（所有元素） | 小（固定大小） | 小（固定大小） |
| **可重用性** | ✅ 多次 | ❌ 一次 | ❌ 一次 |
| **索引访问** | ✅ | ❌ | ❌ |
| **len()** | ✅ | ❌ | ❌ |
| **切片** | ✅ | ❌ | ❌ |
| **提前终止** | ❌ 浪费 | ✅ 高效 | ✅ 高效 |
| **状态保持** | ❌ | ✅ | ✅ |
| **复杂逻辑** | ❌ 有限 | ❌ 有限 | ✅ 强大 |
| **可读性** | 高（简单） | 中 | 高（复杂） |

## 何时使用推导式？

### ✅ 推荐使用推导式的场景

1. **数据量小** - 少于10,000个元素
```python
# 好
squares = [i ** 2 for i in range(100)]
```

2. **需要多次访问** - 要重复遍历或随机访问
```python
# 好
numbers = [i for i in range(10)]
print(numbers[5])  # 需要索引访问
for _ in range(3):
    print(sum(numbers))  # 需要多次遍历
```

3. **需要序列操作** - 切片、len()、索引等
```python
# 好
data = [process(x) for x in items]
first_10 = data[:10]  # 需要切片
total = len(data)     # 需要长度
```

4. **简单转换** - 一行代码能表达清楚
```python
# 好
lowercase = [s.lower() for s in strings]
doubled = [x * 2 for x in numbers]
```

### ❌ 不推荐使用推导式的场景

1. **大数据集** - 超过100,000个元素
```python
# 不好
huge_list = [process(i) for i in range(10000000)]  # 占用大量内存

# 好
huge_gen = (process(i) for i in range(10000000))
```

2. **可能提前终止** - 只需要部分结果
```python
# 不好
all_data = [expensive_func(x) for x in range(1000000)]
result = all_data[0]  # 只用第一个，浪费计算

# 好
data_gen = (expensive_func(x) for x in range(1000000))
result = next(data_gen)  # 只计算一个
```

3. **无限序列** - 不知道何时结束
```python
# 不好（会卡死）
# infinite = [i for i in itertools.count()]

# 好
infinite = (i for i in itertools.count())
```

## 何时使用生成器？

### ✅ 推荐使用生成器的场景

1. **大数据处理** - 内存受限
```python
# 好
def read_large_file(path):
    with open(path) as f:
        for line in f:
            yield line.strip()

# 逐行处理，不占用大量内存
for line in read_large_file('huge_file.txt'):
    process(line)
```

2. **数据流处理** - 实时数据
```python
# 好
def live_data_stream():
    while True:
        data = fetch_from_sensor()
        yield data

for data_point in live_data_stream():
    analyze(data_point)
```

3. **管道式处理** - 多步骤转换
```python
# 好
def numbers():
    for i in range(1000000):
        yield i

def squares(nums):
    for n in nums:
        yield n ** 2

def filter_even(nums):
    for n in nums:
        if n % 2 == 0:
            yield n

# 管道式处理，内存高效
pipeline = filter_even(squares(numbers()))
```

4. **复杂状态** - 需要保持状态
```python
# 好
def stateful_generator():
    count = 0
    total = 0
    while True:
        value = yield
        count += 1
        total += value
        print(f"平均值: {total / count}")
```

5. **只需要一次遍历**
```python
# 好
data = (expensive_transform(x) for x in huge_dataset)
result = process_once(data)  # 只遍历一次
```

### ❌ 不推荐使用生成器的场景

1. **需要多次访问**
```python
# 不好
gen = (i for i in range(10))
print(list(gen))  # [0, 1, 2, ..., 9]
print(list(gen))  # [] - 已耗尽

# 好
lst = [i for i in range(10)]
print(list(lst))  # [0, 1, 2, ..., 9]
print(list(lst))  # [0, 1, 2, ..., 9] - 可重用
```

2. **需要随机访问**
```python
# 不好
gen = (i for i in range(10))
# print(gen[5])  # ❌ 不支持索引

# 好
lst = [i for i in range(10)]
print(lst[5])  # ✅ 支持索引
```

3. **需要知道长度**
```python
# 不好
gen = (i for i in range(10))
# print(len(gen))  # ❌ 不支持 len()

# 好
lst = [i for i in range(10)]
print(len(lst))  # ✅ 支持 len()
```

## 转换指南

### 推导式 → 生成器

```python
# 推导式
squares = [i ** 2 for i in range(1000000)]

# 生成器表达式（简单情况）
squares = (i ** 2 for i in range(1000000))

# 生成器函数（复杂逻辑）
def squares_gen():
    for i in range(1000000):
        result = i ** 2
        # 可以添加更复杂的逻辑
        if result > 100:
            yield result
```

### 生成器 → 推导式

```python
# 生成器
gen = (i ** 2 for i in range(10))

# 转换为列表
lst = list(gen)

# 或者直接使用推导式
lst = [i ** 2 for i in range(10)]
```

## 实战决策树

```
开始
 │
 ├─ 数据量 > 100,000？
 │   ├─ 是 → 使用生成器
 │   └─ 否 → 继续
 │
 ├─ 需要多次遍历？
 │   ├─ 是 → 使用推导式
 │   └─ 否 → 继续
 │
 ├─ 需要索引/切片/len()？
 │   ├─ 是 → 使用推导式
 │   └─ 否 → 继续
 │
 ├─ 可能提前终止？
 │   ├─ 是 → 使用生成器
 │   └─ 否 → 继续
 │
 ├─ 无限序列？
 │   ├─ 是 → 使用生成器
 │   └─ 否 → 继续
 │
 ├─ 逻辑复杂（多步骤/异常处理）？
 │   ├─ 是 → 使用生成器函数
 │   └─ 否 → 使用推导式
 │
 └─ 默认：小数据用推导式，大数据用生成器
```

## 性能测试实例

```python
import time
import sys

def test_memory():
    """内存测试"""
    n = 1000000
    
    # 推导式
    lst = [i for i in range(n)]
    list_size = sys.getsizeof(lst)
    
    # 生成器
    gen = (i for i in range(n))
    gen_size = sys.getsizeof(gen)
    
    print(f"列表: {list_size:,} bytes")
    print(f"生成器: {gen_size:,} bytes")
    print(f"节省: {list_size / gen_size:.0f}x")

def test_creation_speed():
    """创建速度测试"""
    n = 1000000
    
    # 推导式
    start = time.time()
    lst = [i ** 2 for i in range(n)]
    list_time = time.time() - start
    
    # 生成器
    start = time.time()
    gen = (i ** 2 for i in range(n))
    gen_time = time.time() - start
    
    print(f"列表创建: {list_time:.4f}s")
    print(f"生成器创建: {gen_time:.6f}s")
    print(f"生成器快: {list_time / gen_time:.0f}x")

def test_partial_use():
    """部分使用测试"""
    n = 1000000
    take = 100
    
    # 推导式
    start = time.time()
    lst = [i ** 2 for i in range(n)]
    result = lst[:take]
    list_time = time.time() - start
    
    # 生成器
    start = time.time()
    gen = (i ** 2 for i in range(n))
    result = [next(gen) for _ in range(take)]
    gen_time = time.time() - start
    
    print(f"列表方式: {list_time:.4f}s")
    print(f"生成器方式: {gen_time:.6f}s")
    print(f"生成器快: {list_time / gen_time:.0f}x")
```

## 总结

### 推导式的优势
- ✅ 简洁、易读
- ✅ 支持索引、切片、len()
- ✅ 可以多次遍历
- ✅ 适合小数据集

### 生成器的优势
- ✅ 内存高效（延迟计算）
- ✅ 适合大数据集
- ✅ 支持无限序列
- ✅ 可以提前终止
- ✅ 保持状态

### 黄金法则
1. **小数据（< 10,000）** → 推导式
2. **大数据（> 100,000）** → 生成器
3. **需要多次访问** → 推导式
4. **只用一次** → 生成器
5. **需要索引/切片** → 推导式
6. **可能提前终止** → 生成器
7. **逻辑简单** → 推导式
8. **逻辑复杂** → 生成器函数

记住：**没有绝对的对错，根据具体场景选择！**
