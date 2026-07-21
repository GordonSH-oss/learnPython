# 16 线程与并发

## 学习目标

完成本章后，你应该能够：

- 创建、等待和清理 POSIX 线程
- 区分并发、并行、数据竞争和普通的执行顺序不确定
- 用 mutex 保护共享不变量
- 用条件变量等待状态变化，而不是等待“通知本身”
- 判断原子操作、线程局部存储和锁分别适合什么问题
- 设计具有明确启动、运行、关闭和回收阶段的线程池

## 线程共享什么

同一进程的线程共享代码、全局对象、动态内存和文件描述符。每个线程有自己的栈、寄存器上下文和线程局部对象。

线程比独立进程共享更多状态，但不能简单断言线程切换始终“远小于”进程切换；实际成本取决于调度、缓存、地址空间和工作负载。更重要的区别是共享状态带来的同步责任。

## 创建与等待线程

```c
#include <pthread.h>
#include <stdio.h>
#include <string.h>

static void *worker(void *argument) {
    const int id = *(const int *)argument;
    printf("thread %d running\n", id);
    return NULL;
}

int main(void) {
    pthread_t thread;
    int id = 1;
    int error = pthread_create(&thread, NULL, worker, &id);
    if (error != 0) {
        fprintf(stderr, "pthread_create: %s\n", strerror(error));
        return 1;
    }

    error = pthread_join(thread, NULL);
    if (error != 0) {
        fprintf(stderr, "pthread_join: %s\n", strerror(error));
        return 1;
    }
    return 0;
}
```

pthread 函数通常直接返回错误码，不一定设置 `errno`，所以应使用返回值配合 `strerror`。

传给线程的参数必须在线程读取期间仍然存活。不要把循环中不断变化的同一个局部变量地址交给多个线程后立即继续修改。

## joinable 与 detached 生命周期

线程默认是 joinable。线程函数返回后，其部分资源会保留到其他线程调用 `pthread_join`。每个 joinable 线程应恰好 join 一次。

detached 线程结束后自动释放这些资源，不能再 join。detach 适合真正不需要结果、且进程能够保证其依赖对象在结束前一直存活的后台任务。它不是逃避生命周期管理的快捷方式。

## 数据竞争是未定义行为

下面的 `counter++` 是读、计算、写组合操作：

```c
int counter = 0;

static void *unsafe_increment(void *unused) {
    (void)unused;
    counter++;
    return NULL;
}
```

若多个线程没有同步地访问同一内存位置，并且至少一个访问是写入，就形成数据竞争。C 语言把数据竞争定义为未定义行为，不只是“丢失部分递增”。程序即使偶尔得到预期结果，也不能证明它正确。

可以用 ThreadSanitizer 运行专门的错误实验：

```bash
clang -std=c17 -g -pthread -fsanitize=thread race.c -o /tmp/race
/tmp/race
```

ThreadSanitizer 的可用性和与其他 sanitizer 的组合限制取决于平台。

## mutex 保护共享不变量

mutex 不是给某一行代码加装饰，而是保护一组共享状态及其不变量：

```c
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
long counter = 0;

static void add_to_counter(long amount) {
    pthread_mutex_lock(&mutex);
    counter += amount;
    pthread_mutex_unlock(&mutex);
}
```

如果每次递增都加锁，锁操作可能远比整数加法昂贵。线程可以先在局部变量中累计，最后只加锁一次合并结果。

锁粒度存在权衡：

- 较粗的锁容易保持不变量，但可能限制并行度。
- 较细的锁可能增加并行度，也增加加锁开销、死锁路径和验证难度。

“越细越快”不是通用规律。

## 条件变量等待状态

条件变量本身不保存任务或通知。真正的状态保存在受 mutex 保护的谓词中：

```c
pthread_mutex_lock(&mutex);
while (queue_is_empty && !shutdown) {
    pthread_cond_wait(&condition, &mutex);
}
/* 返回前已经重新获得 mutex，必须再次检查状态。 */
pthread_mutex_unlock(&mutex);
```

`pthread_cond_wait` 会原子地释放 mutex 并进入等待，返回前重新获得 mutex。使用 `while` 的原因包括虚假唤醒、多个消费者竞争同一任务，以及状态在唤醒后再次变化。

修改谓词时必须持有同一把 mutex，然后 `signal` 唤醒一个等待者或 `broadcast` 唤醒所有等待者。

## FIFO 有界队列

生产者—消费者队列通常保存：

```text
items[capacity]
head: 下一个读取位置
tail: 下一个写入位置
count: 当前元素数量
```

- 生产者在 `count == capacity` 时等待 `not_full`。
- 消费者在 `count == 0` 时等待 `not_empty`。
- 写入和读取后用取模推进 `tail` 和 `head`。

使用 `buffer[--count]` 实现的是 LIFO 栈，不是 FIFO 队列。

## 原子操作

C11 `<stdatomic.h>` 提供原子类型：

```c
#include <stdatomic.h>

atomic_long counter = 0;
atomic_fetch_add(&counter, 1);
```

原子操作适合单个计数器、标志或经过严格设计的无锁算法。多个字段必须一起满足复杂不变量时，mutex 往往更清楚。原子不等于“整个业务操作自动成为原子事务”。

内存顺序是高级主题；在没有可证明需求前，默认顺序一致语义比随意使用 relaxed 更容易推理。

## 线程局部存储、线程安全与可重入

```c
_Thread_local int current_worker_id;
```

每个线程拥有独立副本，因此访问该对象不需要为对象本身加锁。但堆对象、文件描述符、缓存和任何共享可变状态仍可能竞争。

- 线程安全：函数可以被多个线程并发调用并满足契约，内部可以使用锁。
- 可重入：函数被中断后，在上一次调用尚未完成时再次调用仍然安全，通常不能依赖不可重入锁或共享临时状态。

线程安全不自动意味着可重入，带 `_r` 后缀也应以平台文档为准。

## 死锁

死锁通常涉及互斥、持有并等待、不可抢占和循环等待。常用预防策略：

- 为多把锁规定全局获取顺序
- 缩短锁持有时间，不在持锁时执行未知回调或阻塞 I/O
- 把相关状态放在同一所有权边界内
- 必要时使用 trylock 或超时，但必须设计失败恢复

trylock 不能自动解决死锁；如果失败后立即忙循环，还可能造成活锁和高 CPU 占用。

## 线程池生命周期

一个可靠线程池至少有这些状态转换：

```text
create -> accepting tasks -> shutting down -> workers joined -> destroyed
```

接口必须回答：

- 创建到一半失败时如何停止已创建线程？
- 关闭后提交任务返回什么？
- 关闭是排空队列还是丢弃未开始任务？
- 任务参数由提交者还是任务函数释放？
- 如何知道所有任务已经完成，而不是用 `sleep` 猜测？

通常让 `pool_submit` 返回状态，并让 `pool_destroy` 设置关闭标志、广播条件变量、join 所有 worker，最后销毁同步对象和内存。

## 常见错误

- 忽略 pthread 返回值或错误地读取 `errno`
- 线程参数在线程读取前已经失效或被循环修改
- joinable 线程从不 join
- 用最终结果是否正确判断有没有数据竞争
- 条件变量使用 `if` 而不是循环检查谓词
- 用 `sleep` 建立线程先后顺序
- 持锁执行回调、慢 I/O 或再次获取顺序未知的锁
- 线程池部分初始化失败后释放仍被 worker 使用的对象

## 检查点

1. 两个线程都只读同一对象是否构成数据竞争？
2. 条件变量为什么必须配合受 mutex 保护的状态？
3. 原子计数器为什么不能自动保护由多个字段组成的队列不变量？
4. detached 线程是否可以访问创建函数的局部变量？只有能证明变量仍存活时才可以。

## 动手练习

1. 运行 `examples/16_threads.c`，解释 atomic、mutex 和 FIFO 队列三部分的同步关系。
2. 编写独立的数据竞争示例，用 ThreadSanitizer 观察报告。
3. 完成 `exercises/11_thread_pool.c`，让提交和销毁返回可检查状态。
4. 删除所有基于 `usleep` 的完成等待，使用队列状态、条件变量和 join 验证所有任务结束。
