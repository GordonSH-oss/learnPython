# 07 标准算法、lambda 与 ranges

## 学习目标

- 使用算法表达查找、转换、排序和聚合意图
- 编写安全捕获的 lambda
- 使用 C++20 ranges 组合操作
- 理解算法与手写循环的取舍

## 算法优先表达意图

```cpp
auto found = std::find(values.begin(), values.end(), target);
std::sort(values.begin(), values.end());
auto total = std::accumulate(values.begin(), values.end(), 0LL);
```

算法名称让代码直接表达目的，并集中处理边界。不是所有循环都应强行改写；复杂状态机和多出口逻辑有时普通循环更清楚。

## lambda

```cpp
int threshold = 10;
auto large = [threshold](int value) { return value > threshold; };
```

捕获方式属于生命周期契约：

- `[value]` 按值复制
- `[&value]` 借用引用
- `[owned = std::move(object)]` 移动捕获

异步保存的 lambda 不应引用已经离开作用域的局部变量。

## ranges

```cpp
auto even = values | std::views::filter([](int value) { return value % 2 == 0; });
```

view 通常惰性计算且不拥有来源。来源必须在迭代期间存活。组合 view 可以减少中间容器，但复杂 pipeline 也可能增加类型和调试难度。

## 投影和排序

C++20 ranges 算法支持 projection：

```cpp
std::ranges::sort(records, {}, &Record::score);
```

这比重复编写比较 lambda 更直接。

## 常见错误

- lambda 引用捕获离开作用域对象
- 比较函数不满足严格弱序
- 在遍历 view 时修改来源导致失效
- `accumulate` 初始值类型太窄
- 为追求函数式风格创建难懂的 ranges 链

## 动手练习

1. 用算法实现过滤、排序和求和。
2. 比较 `0` 与 `0LL` 作为 accumulate 初始值。
3. 写一个异步保存引用捕获的错误示例并修复。

