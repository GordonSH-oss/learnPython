# 15 性能、ABI 与 C 互操作

## 学习目标

- 在优化前建立可重复 benchmark
- 理解值语义、分配和缓存对性能的影响
- 使用 `extern "C"` 建立 C ABI
- 防止异常和 C++ 类型跨越不兼容边界

## 先测量

C++ 抽象可以零开销，也可能隐藏分配、引用计数和虚调用。使用 profiler 和 benchmark 观察真实路径，不要凭语法判断成本。

关注：

- 容器分配次数和 `reserve`
- 数据连续性和缓存
- 不必要复制与移动
- shared_ptr 原子计数
- virtual/type erasure 间接调用
- 异常是否只存在于冷失败路径

## C ABI

```cpp
extern "C" int cpp_sum(const int* values, std::size_t length,
                         long long* result) noexcept;
```

`extern "C"` 关闭 C++ 名称修饰并使用 C linkage。接口仍应只使用 C ABI 可表达的类型。

不要跨 C ABI 暴露：

- `std::string`、`std::vector`
- C++ 引用
- 模板类型
- 异常
- 编译器特定类布局

使用指针、长度、固定宽度整数、不透明 handle 和状态码。

## 异常边界

所有 C 导出函数使用 `noexcept` 并捕获内部异常：

```cpp
extern "C" int api(...) noexcept {
    try { return implementation(...); }
    catch (const std::bad_alloc&) { return out_of_memory; }
    catch (...) { return unknown_error; }
}
```

## 不透明句柄

```c
typedef struct engine engine;
engine *engine_create(void);
void engine_destroy(engine *);
```

C++ 实现可以在 `.cpp` 中定义 `struct engine`，对 C 调用者隐藏类和依赖。创建/销毁必须来自同一库。

## Benchmark 公平性

比较相同算法、输入和输出。把数据转换、分配和边界调用纳入真实计时。优化后重新测端到端收益。

## 动手练习

1. 给 vector 处理基准增加 reserve 对照。
2. 导出一个只使用 C 类型的 C++ 函数并从 C 调用。
3. 使用不透明 handle 包装 C++ 类。

