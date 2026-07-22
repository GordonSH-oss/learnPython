# 03 类、构造函数与不变量

## 学习目标

- 用类封装状态和行为
- 通过构造函数建立不变量
- 区分 `class` 与 `struct` 的默认访问权限
- 使用成员初始化列表和封装接口

## 从结构体到类

C 结构体通常依靠外部函数维护状态。C++ 类可以把数据和操作放在同一契约中：

```cpp
class BankAccount {
public:
    explicit BankAccount(long initial_balance)
        : balance_(initial_balance) {
        if (initial_balance < 0) {
            throw std::invalid_argument("negative balance");
        }
    }

    void deposit(long amount);
    bool withdraw(long amount);
    long balance() const { return balance_; }

private:
    long balance_;
};
```

不变量是所有公开操作前后都必须成立的条件，例如 `balance_ >= 0`。

## 构造函数

成员在进入构造函数体前已经初始化。初始化列表不是赋值语法：

```cpp
Widget(std::string name) : name_(std::move(name)) {}
```

成员按类中声明顺序初始化，而不是初始化列表书写顺序。让两者顺序一致可避免误解和警告。

单参数构造函数通常加 `explicit`，防止意外隐式转换。

## `class` 与 `struct`

两者能力几乎相同：

- `class` 默认成员和继承为 private。
- `struct` 默认成员和继承为 public。

惯例上，`struct` 适合无复杂不变量的简单值聚合；`class` 适合封装状态和行为。

## 成员函数

`const` 成员函数可以在 const 对象上调用。getter 返回值、引用还是 view 取决于生命周期和封装：返回私有字符串的 `const&` 会暴露对象内部生命周期，返回值更独立但可能复制。

## 枚举类

```cpp
enum class Status { pending, running, done };
```

`enum class` 不会把枚举项注入外层作用域，也不会隐式转换为整数，通常比传统 enum 更安全。

## 常见错误

- 构造完成后对象仍可能处于无效状态
- 在构造函数体中“初始化”本应在列表初始化的成员
- 返回私有成员的悬空引用或可修改引用
- 忘记为只读成员函数添加 `const`
- 用继承只为复用几行实现

## 动手练习

1. 为温度类型建立“不低于绝对零度”的不变量。
2. 使用 `enum class` 表示任务状态。
3. 编写测试验证每个公开操作都保持不变量。

