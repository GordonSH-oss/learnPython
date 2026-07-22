# 10 模板、泛型与 concepts

## 学习目标

- 编写函数和类模板
- 理解模板实例化与头文件定义
- 使用 concepts 表达约束
- 控制模板错误信息和代码膨胀

## 函数模板

```cpp
template <typename T>
T maximum(const T& left, const T& right) {
    return left < right ? right : left;
}
```

模板在使用具体类型时实例化。编译器需要看到定义，因此模板实现常在头文件。

## Concepts

```cpp
template <std::totally_ordered T>
const T& maximum(const T& left, const T& right);
```

concept 描述操作要求并改善接口和诊断。它不是运行时检查。

自定义 concept：

```cpp
template <typename T>
concept Sized = requires(const T& value) {
    { value.size() } -> std::convertible_to<std::size_t>;
};
```

约束应表达算法真正需要的最小能力，避免无意义地要求具体容器类型。

## 类模板

`std::vector<T>` 本身就是类模板。自定义模板同样需要考虑所有权、异常和实例化成本。

## 编译成本

模板可能增加编译时间和二进制大小。大型项目可通过减少无意义实例化、显式实例化或隐藏非模板实现控制成本。

## 常见错误

- 模板只在 `.cpp` 定义导致链接错误
- 未约束模板产生巨大诊断
- concept 约束过强
- 把运行时多态问题强行模板化
- 在公共模板中暴露不稳定实现细节

## 动手练习

1. 编写适用于 span 的泛型 sum。
2. 用 concept 限制可排序类型。
3. 把模板定义移到 `.cpp` 观察链接错误，再解释显式实例化。

