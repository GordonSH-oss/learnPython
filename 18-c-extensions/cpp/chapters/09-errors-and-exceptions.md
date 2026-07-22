# 09 异常、状态与错误边界

## 学习目标

- 根据失败类型选择异常、可选值或错误码
- 理解异常安全保证
- 使用 RAII 保证栈展开安全
- 避免异常跨越 C ABI

## 失败分类

- 调用者违反前置条件：可抛 `std::invalid_argument` 或用类型避免非法状态。
- 环境/资源失败：可抛 `std::system_error`，或在系统边界返回 error_code。
- 查询没有结果：`std::optional<T>` 常比异常更合适。
- 性能敏感底层循环：状态码可能更清楚，但要完整传播。

异常适合构造函数，因为构造函数不能返回错误码；失败构造不会产生半有效对象。

## 异常安全保证

| 保证 | 含义 |
| --- | --- |
| no-throw | 操作不会抛异常 |
| strong | 失败时状态保持原样 |
| basic | 失败后对象仍有效，无泄漏，但值可能变化 |
| none | 无可用保证 |

通过“先构造临时结果，再提交交换”常可实现 strong guarantee。

## 捕获策略

只在能够恢复、添加上下文或转换边界时捕获。不要 `catch (...)` 后静默忽略。

```cpp
try {
    run();
} catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
}
```

按 `const&` 捕获避免切片。

## C ABI 边界

C++ 异常不能穿过不知道 C++ 异常 ABI 的 C 调用栈。`extern "C"` 导出函数应捕获所有异常并转换成状态码：

```cpp
extern "C" int api_call(...) noexcept {
    try { ... }
    catch (...) { return error_code; }
}
```

## 常见错误

- 析构函数抛异常
- 捕获异常后继续使用半更新状态
- 用异常表示高频正常分支
- 按值捕获基类异常造成切片
- 异常跨 C 或 Python ABI 边界逃逸

## 动手练习

1. 为配置查找选择 optional 或异常并说明原因。
2. 给容器更新实现 strong guarantee。
3. 把 C++ 异常转换为 C 状态码。

