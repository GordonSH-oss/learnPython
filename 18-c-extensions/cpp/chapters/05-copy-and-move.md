# 05 值语义、复制与移动

## 学习目标

- 理解复制构造、复制赋值、移动构造和移动赋值
- 使用 Rule of Zero、Three 和 Five
- 判断 moved-from 对象的合法状态
- 通过值语义简化所有权

## 值语义

值语义意味着对象像整数一样可以独立复制：复制后两个对象各自拥有有效状态，修改一个不影响另一个。

`std::string` 和 `std::vector` 都提供值语义。它们内部管理动态资源，但调用者不需要手写复制和析构。

## Rule of Zero

如果类的成员都能正确管理自身资源，就不应声明析构、复制或移动操作：

```cpp
struct Report {
    std::string title;
    std::vector<int> values;
};
```

编译器生成的特殊成员函数已经正确。这是现代 C++ 默认目标。

## Rule of Five

直接管理裸资源的类通常需要考虑：

1. 析构函数
2. 复制构造函数
3. 复制赋值运算符
4. 移动构造函数
5. 移动赋值运算符

很多资源不应复制，可以删除复制操作，只提供移动。

## 移动

移动操作把资源从来源转移到目标，避免深复制：

```cpp
Buffer(Buffer&& other) noexcept
    : data_(std::exchange(other.data_, nullptr)),
      size_(std::exchange(other.size_, 0)) {}
```

moved-from 对象必须仍可析构和赋值，但除非类型另有保证，其业务值通常未指定。不要在 move 后继续依赖旧内容。

移动构造通常标记 `noexcept`。标准容器扩容时只有在移动不会抛异常或无法复制等条件下才愿意采用移动，以保持异常安全。

## `std::move`

```cpp
target.push_back(std::move(source));
```

`std::move` 只是转换值类别。目标类型是否真正转移资源取决于其移动构造；若只有复制构造，仍可能复制。

## Copy-and-swap

复制赋值可先复制临时值，再交换状态，从而提供强异常保证。但 Rule of Zero 通常比手写 copy-and-swap 更简单。

## 常见错误

- 拥有裸指针却使用编译器默认浅复制
- move 后继续读取旧业务值
- 移动构造忘记清空来源所有权
- 自定义析构后无意中抑制隐式移动
- 为可以 Rule of Zero 的类手写五个操作

## 动手练习

1. 观察 vector 扩容时复制和 `noexcept` 移动的差异。
2. 实现只移动的 fd wrapper。
3. 把手写动态数组类重构为内部使用 `std::vector`，恢复 Rule of Zero。

