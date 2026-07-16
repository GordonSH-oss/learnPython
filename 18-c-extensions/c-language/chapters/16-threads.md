# 16 线程与并发

## 学习目标

使用 POSIX threads 创建并发程序，理解竞态条件并掌握互斥锁、条件变量等同步原语。

## 线程 vs 进程

进程拥有独立地址空间，线程共享同一进程的地址空间（代码段、堆、全局变量），但每个线程有独立的栈和寄存器上下文。线程切换开销远小于进程。

## 创建与等待线程

```c
#include <pthread.h>
#include <stdio.h>

void *worker(void *arg) {
    int id = *(int *)arg;
    printf("thread %d running\n", id);
    return NULL;
}

int main(void) {
    pthread_t t1, t2;
    int id1 = 1, id2 = 2;
    pthread_create(&t1, NULL, worker, &id1);
    pthread_create(&t2, NULL, worker, &id2);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    return 0;
}
```

编译：`gcc -o threads threads.c -pthread`

## 竞态条件

多线程同时修改共享变量时，结果不可预测：

```c
int counter = 0;

void *increment(void *arg) {
    for (int i = 0; i < 1000000; i++) {
        counter++;  /* 非原子操作：读-改-写 */
    }
    return NULL;
}
```

两个线程各加 100 万次，最终 `counter` 几乎不会是 200 万。

## 互斥锁

用 `pthread_mutex_t` 保护共享数据，同一时刻只有一个线程能持有锁：

```c
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
int counter = 0;

void *safe_increment(void *arg) {
    for (int i = 0; i < 1000000; i++) {
        pthread_mutex_lock(&lock);
        counter++;
        pthread_mutex_unlock(&lock);
    }
    return NULL;
}
```

加锁后结果始终正确为 200 万。锁的粒度越细性能越好，但设计越复杂。

## 条件变量

条件变量用于线程间通知，典型场景是生产者-消费者：

```c
pthread_mutex_t mtx = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t cond = PTHREAD_COND_INITIALIZER;
int ready = 0;

void *producer(void *arg) {
    pthread_mutex_lock(&mtx);
    ready = 1;
    pthread_cond_signal(&cond);
    pthread_mutex_unlock(&mtx);
    return NULL;
}

void *consumer(void *arg) {
    pthread_mutex_lock(&mtx);
    while (!ready) {
        pthread_cond_wait(&cond, &mtx);  /* 释放锁并等待 */
    }
    printf("consumed\n");
    pthread_mutex_unlock(&mtx);
    return NULL;
}
```

`pthread_cond_wait` 必须在持有锁时调用，且用 `while` 而非 `if` 防止虚假唤醒。

## 死锁

两个线程各持有一把锁并等待对方释放，形成循环等待：

```c
/* 线程 A: lock(m1) -> lock(m2) */
/* 线程 B: lock(m2) -> lock(m1)  -- 死锁！ */
```

避免策略：
- 固定加锁顺序（所有线程按相同顺序获取锁）
- 使用 `pthread_mutex_trylock` 非阻塞尝试
- 减少锁的持有时间，缩小临界区

## 线程安全与可重入

全局/静态变量是线程不安全的根源。使用 `_Thread_local`（C11）让每个线程拥有独立副本：

```c
#include <threads.h>

_Thread_local int tls_var = 0;

void *func(void *arg) {
    tls_var++;  /* 每个线程独立，无需加锁 */
    return NULL;
}
```

可重入函数不依赖任何共享状态，是最安全的设计。标准库中 `strtok_r`、`localtime_r` 等 `_r` 后缀版本即为可重入替代。

## 动手练习

编写一个多线程程序：4 个线程并发对共享计数器各累加 100 万次，先不加锁观察结果，再用 mutex 修正。编译时加 `-pthread`，用 `-fsanitize=thread` 检测数据竞争。
