# 08 智能指针与所有权图

## 学习目标

- 区分拥有指针和观察指针
- 使用 `unique_ptr` 表达独占所有权
- 谨慎使用 `shared_ptr` 和 `weak_ptr`
- 识别循环引用和错误 deleter

## `unique_ptr`

```cpp
auto task = std::make_unique<Task>(arguments...);
```

`unique_ptr` 不可复制、可移动。它是需要动态分配时的默认 owning pointer。很多场景甚至不需要指针，直接把对象作为成员或局部值更简单。

向函数转移所有权：

```cpp
void install(std::unique_ptr<Plugin> plugin);
```

只借用对象时使用 `Plugin&`、`const Plugin&` 或可空的 `Plugin*`，不要制造无意义 shared ownership。

## `shared_ptr`

`shared_ptr` 使用共享控制块管理引用计数。它适合多个所有者生命周期无法自然分层的情况，但带来原子计数、额外分配和所有权不清晰。

优先 `std::make_shared`，但若对象很大且 weak_ptr 长期存在，控制块和对象同一分配可能延长大内存占用。

## `weak_ptr`

weak_ptr 观察 shared ownership 而不增加强引用，用于打破循环：

```text
Parent --shared--> Child
Parent <--weak---- Child
```

使用前调用 `lock()` 获取临时 shared_ptr，并处理对象已经销毁的情况。

## 自定义 deleter

智能指针也能管理 `FILE*`、socket wrapper 或第三方句柄：

```cpp
using FilePtr = std::unique_ptr<std::FILE, FileCloser>;
```

deleter 必须与资源获取函数匹配，不能用 `delete` 释放 `malloc` 内存。

## 常见错误

- 把所有裸指针机械替换成 shared_ptr
- 从同一裸指针创建两个独立 shared_ptr
- shared_ptr 循环导致对象不释放
- 返回 `.get()` 后 owning pointer 立即销毁
- 数组、C 句柄使用错误 deleter

## 动手练习

1. 用 unique_ptr 构建树。
2. 制造 shared_ptr 循环并用 weak_ptr 修复。
3. 为 `FILE*` 编写自定义 deleter。

