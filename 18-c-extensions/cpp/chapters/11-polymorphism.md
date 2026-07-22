# 11 继承、虚函数与替代方案

## 学习目标

- 使用抽象基类表达运行时接口
- 理解虚析构函数和对象切片
- 比较 virtual、template、variant 和 type erasure
- 优先组合而非无目的继承

## 运行时多态

```cpp
class Shape {
public:
    virtual ~Shape() = default;
    virtual double area() const = 0;
};
```

通过基类指针或引用调用 virtual 函数时，实际对象决定实现。

多态基类通常需要虚析构函数，否则通过基类指针 delete 派生对象是未定义行为。

## 对象切片

按值把派生对象复制为基类会丢失派生部分：

```cpp
void render(Shape shape); // 错误：抽象类甚至不能这样传，普通基类也会切片
```

使用 `const Shape&` 或 owning smart pointer。

## 替代方案

| 需求 | 工具 |
| --- | --- |
| 编译期多态 | 模板/concepts |
| 封闭类型集合 | `std::variant` + `std::visit` |
| 开放插件式层次 | virtual interface |
| 保存任意 callable | 模板或 `std::function` |

variant 避免堆分配和虚调用，但添加类型需要修改 variant 定义及 visitor。virtual 支持开放扩展，但有间接调用和生命周期设计成本。

## 组合优先

继承表达 is-a 和可替换接口，不应只为复用实现。把策略或资源作为成员通常更容易测试和保持不变量。

## 常见错误

- 多态基类没有虚析构
- 按值存储基类导致切片
- 构造/析构期间依赖虚调用派发到派生类
- 深继承层次共享可变状态
- 使用 dynamic_cast 修补错误抽象

## 动手练习

1. 实现 Shape 层次并通过 unique_ptr 保存。
2. 用 variant 重写封闭图形集合。
3. 比较两种设计的扩展点和内存布局。

