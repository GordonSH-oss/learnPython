# 02 类型、引用、`const` 与值类别

## 学习目标

- 使用引用表达非空别名
- 根据所有权和成本选择值、引用或指针参数
- 理解 `const`、`auto`、`nullptr` 和范围 for
- 建立左值、右值和移动语义的前置模型

## 引用

```cpp
void increment(int& value) {
    ++value;
}
```

`int&` 是左值引用，必须绑定到有效对象，不能重新绑定。它通常表达“借用并允许修改”。只读借用使用：

```cpp
void print(const std::string& text);
```

引用不是拥有关系，也不会延长普通对象的生命周期。

## 参数选择

| 需求 | 常见形式 |
| --- | --- |
| 小型可复制值 | `int value` |
| 只读大型对象 | `const T& value` |
| 修改调用者对象 | `T& value` |
| 参数可空 | `T* value` |
| 接管值并保存 | `T value` 后移动进成员 |

不要因为“引用更快”而把所有参数改成引用。`int`、迭代器和小型 view 按值传递通常更清楚。

## `const`

```cpp
const std::string name = "Ada";
const std::string& view = name;
```

成员函数末尾的 `const` 表示不修改对象的逻辑状态：

```cpp
std::size_t size() const;
```

## `auto`

`auto` 从初始化表达式推导类型：

```cpp
auto count = values.size();
auto iterator = values.begin();
```

它减少重复复杂类型，但不应隐藏重要单位、所有权或窄化。`auto` 默认按值推导，会丢掉顶层引用；需要引用时写 `auto&` 或 `const auto&`。

## `nullptr`

C++ 使用 `nullptr` 表达空指针。它具有专门类型，不会像整数 `0` 那样干扰重载解析。

## 值类别

左值通常表示具有身份、可以取地址的对象；右值通常表示临时值或即将被消费的值。右值引用 `T&&` 是移动语义和完美转发的基础。

此时只需记住：`std::move` 不移动任何东西，它把表达式转换成可被移动构造/赋值接收的右值。真正转移资源的是目标类型的移动操作。

## 常见错误

- 返回局部变量引用
- 保存比来源对象活得更久的引用
- 用非 const 引用表达可空参数
- 误以为 `auto` 总会保留引用
- 对仍需保持原值的对象调用 `std::move`

## 动手练习

1. 分别编写按值、`const&` 和 `&` 参数函数。
2. 用 `auto`、`auto&`、`const auto&` 遍历 vector，观察修改效果。
3. 尝试把 `nullptr` 和 `0` 传给重载函数，比较解析结果。

