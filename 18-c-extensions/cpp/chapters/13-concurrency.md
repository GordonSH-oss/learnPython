# 13 线程、锁、原子与任务

## 学习目标

- 使用 `std::jthread` 管理线程生命周期
- 用 mutex 和 RAII lock 保护不变量
- 区分 atomic 与复合状态同步
- 使用 future/promise 表达任务结果

## 线程生命周期

`std::thread` 析构时若仍 joinable 会终止程序。C++20 `std::jthread` 析构时请求停止并 join，通常更安全：

```cpp
std::jthread worker([] { /* work */ });
```

线程函数捕获的引用必须在线程结束前保持有效。

## Mutex 与 RAII

```cpp
std::mutex mutex;
{
    std::lock_guard lock{mutex};
    // 修改共享不变量
}
```

异常或 return 都会释放锁。多把 mutex 使用 `std::scoped_lock` 避免不一致锁顺序。

## 原子

`std::atomic<int>` 适合单个计数器或标志。队列 head、tail、size 等复合不变量不能只把每个字段改成 atomic 就自动正确。

默认 sequential consistency 最容易推理。只有性能测量和完整 happens-before 证明后才使用更弱 memory order。

## 条件变量

条件变量等待谓词：

```cpp
condition.wait(lock, [&] { return !queue.empty() || stopped; });
```

谓词防止虚假唤醒和状态被其他线程抢先消费。

## Future 和 async

future 表达一次性结果或异常传播。`std::async` 的启动策略可能是异步线程或延迟执行，应显式指定策略或使用自己的 executor/线程池。

## 停止令牌

`std::jthread` 可把 `std::stop_token` 传给 worker，支持协作取消。取消必须在安全点检查，不能强制终止持锁线程。

## 常见错误

- thread/jthread 捕获悬空引用
- 手工 lock 后异常导致未 unlock
- 持锁调用未知回调
- 把 atomic 当成多字段事务
- 条件变量不用谓词
- 忽略 async 启动策略

## 动手练习

1. 实现线程安全计数器。
2. 用 jthread 和 stop_token 实现可停止 worker。
3. 用条件变量实现有界队列。

