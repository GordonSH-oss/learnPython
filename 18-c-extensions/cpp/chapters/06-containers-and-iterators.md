# 06 标准容器、字符串与迭代器

## 学习目标

- 根据访问模式选择标准容器
- 使用 `std::string`、`std::string_view`、`std::span`
- 理解迭代器失效和容量变化
- 避免不必要的手工内存管理

## 首选 `std::vector`

`std::vector<T>` 是动态连续数组，通常是序列容器默认选择：

```cpp
std::vector<int> values{1, 2, 3};
values.push_back(4);
```

它提供 O(1) 随机访问、良好缓存局部性和自动生命周期。扩容可能移动元素并使指针、引用和迭代器失效。

`reserve` 调整容量而不改变 size；`resize` 改变元素数量。不要混淆。

## 容器选择

| 需求 | 常见选择 |
| --- | --- |
| 连续动态序列 | `std::vector` |
| 固定编译期长度 | `std::array` |
| 双端频繁插入 | `std::deque` |
| 有序键值 | `std::map` |
| 哈希键值 | `std::unordered_map` |
| 唯一元素 | `std::set`/`unordered_set` |

链表很少是默认选择。节点分配和缓存不友好常抵消理论 O(1) 插入优势。

## 字符串与 view

`std::string` 拥有字符存储。`std::string_view` 只是借用字符范围：

```cpp
std::string_view prefix(std::string_view text, std::size_t count);
```

view 不保证以 NUL 结尾，也不会延长来源生命周期。返回指向临时 string 的 view 会悬空。

`std::span<T>` 是连续对象序列的非拥有 view，携带指针和长度，适合替代 `(T*, size_t)`：

```cpp
int sum(std::span<const int> values);
```

## 迭代器

迭代器把容器位置抽象成统一接口。半开区间 `[begin, end)` 与 C 数组末尾后一指针模型一致。

修改容器时必须检查失效规则。vector 扩容会使所有旧地址失效；erase 通常使删除位置及其后的迭代器失效。

## 动手练习

1. 用 vector 重写 C 动态数组。
2. 比较 `reserve` 前后扩容次数。
3. 编写接收 `span<const int>` 的统计函数。
4. 制造一个悬空 string_view，再修复生命周期。

