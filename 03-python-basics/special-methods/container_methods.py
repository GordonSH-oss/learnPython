"""
容器类型魔法方法详解

__len__, __getitem__, __setitem__, __delitem__, __contains__, __iter__
"""

# ============================================================
# 案例 1: 基础容器 - __len__ 和 __getitem__
# ============================================================
print("=" * 60)
print("案例 1: 基础容器实现")
print("=" * 60)

class SimpleList:
    """简单列表 - 实现基础容器协议"""
    
    def __init__(self, items=None):
        self._items = list(items) if items else []
    
    def __len__(self) -> int:
        """len(list)"""
        return len(self._items)
    
    def __getitem__(self, index):
        """list[index] 或 list[start:end]"""
        return self._items[index]
    
    def __setitem__(self, index, value):
        """list[index] = value"""
        self._items[index] = value
    
    def __delitem__(self, index):
        """del list[index]"""
        del self._items[index]
    
    def __contains__(self, item) -> bool:
        """item in list"""
        return item in self._items
    
    def append(self, item):
        """添加元素"""
        self._items.append(item)
    
    def __repr__(self) -> str:
        return f"SimpleList({self._items})"

# 使用示例
lst = SimpleList([1, 2, 3, 4, 5])
print(f"列表: {lst}")
print(f"长度: len(lst) = {len(lst)}")
print(f"访问: lst[0] = {lst[0]}")
print(f"切片: lst[1:3] = {lst[1:3]}")
print(f"包含: 3 in lst = {3 in lst}")

lst[0] = 10
print(f"\n修改后: {lst}")

del lst[1]
print(f"删除后: {lst}")


# ============================================================
# 案例 2: 实现迭代器协议
# ============================================================
print("\n" + "=" * 60)
print("案例 2: 迭代器协议")
print("=" * 60)

class Range:
    """自定义 range 类 - 实现迭代器"""
    
    def __init__(self, start, stop=None, step=1):
        if stop is None:
            self.start = 0
            self.stop = start
        else:
            self.start = start
            self.stop = stop
        self.step = step
    
    def __iter__(self):
        """返回迭代器（这里返回 self）"""
        self.current = self.start
        return self
    
    def __next__(self):
        """获取下一个元素"""
        if (self.step > 0 and self.current >= self.stop) or \
           (self.step < 0 and self.current <= self.stop):
            raise StopIteration
        value = self.current
        self.current += self.step
        return value
    
    def __repr__(self) -> str:
        return f"Range({self.start}, {self.stop}, {self.step})"

# 使用示例
print("遍历 Range(5):")
for i in Range(5):
    print(f"  {i}", end="")
print()

print("\n遍历 Range(2, 8, 2):")
for i in Range(2, 8, 2):
    print(f"  {i}", end="")
print()


# ============================================================
# 案例 3: 字典类型容器
# ============================================================
print("\n" + "=" * 60)
print("案例 3: 字典类型容器")
print("=" * 60)

class CaseInsensitiveDict:
    """不区分大小写的字典"""
    
    def __init__(self):
        self._data = {}
    
    def __getitem__(self, key):
        """d[key]"""
        return self._data[key.lower()]
    
    def __setitem__(self, key, value):
        """d[key] = value"""
        self._data[key.lower()] = value
    
    def __delitem__(self, key):
        """del d[key]"""
        del self._data[key.lower()]
    
    def __contains__(self, key) -> bool:
        """key in d"""
        return key.lower() in self._data
    
    def __len__(self) -> int:
        """len(d)"""
        return len(self._data)
    
    def __iter__(self):
        """遍历键"""
        return iter(self._data)
    
    def keys(self):
        """获取所有键"""
        return self._data.keys()
    
    def values(self):
        """获取所有值"""
        return self._data.values()
    
    def items(self):
        """获取所有键值对"""
        return self._data.items()
    
    def __repr__(self) -> str:
        return f"CaseInsensitiveDict({dict(self._data)})"

# 使用示例
d = CaseInsensitiveDict()
d["Name"] = "张三"
d["AGE"] = 25
d["Email"] = "zhangsan@example.com"

print(f"字典: {d}")
print(f"\nd['name'] = {d['name']}")    # 小写访问
print(f"d['NAME'] = {d['NAME']}")      # 大写访问
print(f"d['NaMe'] = {d['NaMe']}")      # 混合大小写
print(f"\n'email' in d: {'email' in d}")
print(f"'EMAIL' in d: {'EMAIL' in d}")

print("\n遍历:")
for key in d:
    print(f"  {key}: {d[key]}")


# ============================================================
# 案例 4: 惰性加载容器
# ============================================================
print("\n" + "=" * 60)
print("案例 4: 惰性加载容器")
print("=" * 60)

class LazyList:
    """惰性列表 - 只在访问时才生成元素"""
    
    def __init__(self, generator_func, length):
        self._generator = generator_func
        self._length = length
        self._cache = {}  # 缓存已生成的元素
    
    def __len__(self) -> int:
        return self._length
    
    def __getitem__(self, index):
        """访问时才生成元素"""
        if isinstance(index, slice):
            # 处理切片
            start, stop, step = index.indices(self._length)
            return [self[i] for i in range(start, stop, step)]
        
        # 处理单个索引
        if index < 0:
            index += self._length
        if index < 0 or index >= self._length:
            raise IndexError("索引超出范围")
        
        # 检查缓存
        if index not in self._cache:
            print(f"  → 生成元素 [{index}]")
            self._cache[index] = self._generator(index)
        else:
            print(f"  → 使用缓存 [{index}]")
        
        return self._cache[index]
    
    def __repr__(self) -> str:
        return f"LazyList(length={self._length}, cached={len(self._cache)})"

# 使用示例
def square_generator(n):
    """生成平方数"""
    return n ** 2

lazy_list = LazyList(square_generator, 10)
print(f"创建: {lazy_list}")

print("\n第一次访问 lazy_list[5]:")
print(f"  值 = {lazy_list[5]}")

print("\n第二次访问 lazy_list[5]:")
print(f"  值 = {lazy_list[5]}")

print("\n访问切片 lazy_list[2:5]:")
result = lazy_list[2:5]
print(f"  值 = {result}")


# ============================================================
# 案例 5: 多维数组
# ============================================================
print("\n" + "=" * 60)
print("案例 5: 多维数组")
print("=" * 60)

class Matrix:
    """简单的二维矩阵"""
    
    def __init__(self, rows, cols, init_value=0):
        self.rows = rows
        self.cols = cols
        self._data = [[init_value for _ in range(cols)] for _ in range(rows)]
    
    def __getitem__(self, index):
        """支持 matrix[row, col] 或 matrix[row]"""
        if isinstance(index, tuple):
            row, col = index
            return self._data[row][col]
        else:
            # 返回整行
            return self._data[index]
    
    def __setitem__(self, index, value):
        """支持 matrix[row, col] = value"""
        if isinstance(index, tuple):
            row, col = index
            self._data[row][col] = value
        else:
            # 设置整行
            self._data[index] = value
    
    def __repr__(self) -> str:
        lines = []
        for row in self._data:
            lines.append("  " + " ".join(f"{val:3}" for val in row))
        return "Matrix([\n" + "\n".join(lines) + "\n])"

# 使用示例
matrix = Matrix(3, 4)
print("初始矩阵:")
print(matrix)

# 设置单个元素
matrix[0, 0] = 1
matrix[1, 1] = 2
matrix[2, 2] = 3

print("\n修改后:")
print(matrix)

# 访问单个元素
print(f"\nmatrix[1, 1] = {matrix[1, 1]}")

# 访问整行
print(f"matrix[0] = {matrix[0]}")


# ============================================================
# 案例 6: 自定义集合
# ============================================================
print("\n" + "=" * 60)
print("案例 6: 自定义集合")
print("=" * 60)

class UniqueList:
    """不允许重复元素的列表"""
    
    def __init__(self, items=None):
        self._items = []
        if items:
            for item in items:
                if item not in self._items:
                    self._items.append(item)
    
    def __len__(self) -> int:
        return len(self._items)
    
    def __getitem__(self, index):
        return self._items[index]
    
    def __contains__(self, item) -> bool:
        return item in self._items
    
    def __iter__(self):
        return iter(self._items)
    
    def append(self, item):
        """只添加不存在的元素"""
        if item not in self._items:
            self._items.append(item)
            print(f"  ✅ 添加 {item}")
        else:
            print(f"  ❌ {item} 已存在，跳过")
    
    def __repr__(self) -> str:
        return f"UniqueList({self._items})"

# 使用示例
unique = UniqueList([1, 2, 3])
print(f"初始: {unique}")

print("\n尝试添加元素:")
unique.append(4)
unique.append(2)  # 重复
unique.append(5)
unique.append(3)  # 重复

print(f"\n最终: {unique}")


# ============================================================
# 案例 7: 反向索引
# ============================================================
print("\n" + "=" * 60)
print("案例 7: 支持反向索引")
print("=" * 60)

class CircularList:
    """循环列表 - 索引自动循环"""
    
    def __init__(self, items):
        self._items = list(items)
    
    def __len__(self) -> int:
        return len(self._items)
    
    def __getitem__(self, index):
        """索引自动对长度取模"""
        if not self._items:
            raise IndexError("列表为空")
        # 自动循环
        index = index % len(self._items)
        return self._items[index]
    
    def __repr__(self) -> str:
        return f"CircularList({self._items})"

# 使用示例
circular = CircularList(['A', 'B', 'C', 'D'])
print(f"列表: {circular}")
print(f"长度: {len(circular)}")

print("\n正常索引:")
print(f"circular[0] = {circular[0]}")
print(f"circular[2] = {circular[2]}")

print("\n超出范围的索引（自动循环）:")
print(f"circular[4] = {circular[4]}")   # 相当于 [0]
print(f"circular[5] = {circular[5]}")   # 相当于 [1]
print(f"circular[10] = {circular[10]}") # 相当于 [2]


# ============================================================
# 总结
# ============================================================
print("\n" + "=" * 60)
print("容器类型魔法方法总结")
print("=" * 60)
print("""
📌 容器协议方法:
┌────────────────┬──────────────────┬───────────────────────┐
│ 方法           │ 语法             │ 说明                  │
├────────────────┼──────────────────┼───────────────────────┤
│ __len__        │ len(obj)         │ 返回容器长度          │
│ __getitem__    │ obj[key]         │ 获取元素              │
│ __setitem__    │ obj[key] = value │ 设置元素              │
│ __delitem__    │ del obj[key]     │ 删除元素              │
│ __contains__   │ item in obj      │ 成员测试              │
│ __iter__       │ for i in obj     │ 返回迭代器            │
│ __reversed__   │ reversed(obj)    │ 反向迭代              │
└────────────────┴──────────────────┴───────────────────────┘

📌 迭代器协议:
┌────────────────┬─────────────────────────────────────┐
│ __iter__       │ 返回迭代器对象（通常是 self）      │
│ __next__       │ 返回下一个元素，无元素时抛出        │
│                │ StopIteration                       │
└────────────────┴─────────────────────────────────────┘

✅ 最佳实践:
1. 实现 __len__ 和 __getitem__ 就可以支持很多操作
2. __getitem__ 应该支持切片操作
3. __contains__ 默认会遍历容器，可以优化
4. 迭代器应该在 __iter__ 中初始化状态
5. __next__ 没有元素时必须抛出 StopIteration

💡 使用场景:
- 自定义列表、字典、集合
- 数据库查询结果
- 文件读取器
- 惰性加载序列
- 多维数组
- 环形缓冲区

⚠️  注意事项:
1. __getitem__ 支持切片时，参数类型是 slice 对象
2. 不要在迭代过程中修改容器
3. 迭代器用完后不能重用，需要重新调用 __iter__
4. 索引越界应该抛出 IndexError
5. 键不存在应该抛出 KeyError
""")