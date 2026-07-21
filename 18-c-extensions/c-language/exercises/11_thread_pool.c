/**
 * 练习 11: 线程池 (Thread Pool)
 *
 * 实现一个简单的固定大小线程池，支持任务提交和优雅关闭。
 *
 * 编译: clang -std=c17 -Wall -Wextra -Wpedantic -pthread -o 11_thread_pool 11_thread_pool.c
 */

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdbool.h>
#include <unistd.h>

/* 任务节点结构体 - 链表实现的任务队列 */
typedef struct task {
    void (*function)(void *arg);  // 任务函数指针
    void *arg;                    // 任务参数
    struct task *next;            // 下一个任务
} task_t;

/* 线程池结构体 */
typedef struct {
    pthread_t *threads;           // 工作线程数组
    int thread_count;             // 线程数量
    task_t *queue_head;           // 任务队列头
    task_t *queue_tail;           // 任务队列尾
    pthread_mutex_t mutex;        // 保护队列的互斥锁
    pthread_cond_t cond;          // 通知新任务的条件变量
    bool shutdown;                // 关闭标志
} thread_pool_t;

/**
 * 工作线程函数
 * 循环等待任务，取出并执行
 */
void *worker_thread(void *arg) {
    thread_pool_t *pool = (thread_pool_t *)arg;

    while (true) {
        // TODO: 加锁

        // TODO: 当队列为空且未关闭时，在条件变量上等待

        // TODO: 如果收到关闭信号且队列为空，解锁并退出线程

        // TODO: 从队列头部取出一个任务

        // TODO: 解锁

        // TODO: 执行任务并释放任务节点内存
    }
    return NULL;
}

/**
 * 创建线程池
 * @param num_threads 工作线程数量
 * @return 线程池指针，失败返回 NULL
 */
thread_pool_t *pool_create(int num_threads) {
    // TODO: 分配线程池结构体内存

    // TODO: 初始化各字段（线程数、队列指针、shutdown标志）

    // TODO: 初始化互斥锁和条件变量

    // TODO: 分配线程数组并创建工作线程

    return NULL; // 替换为正确的返回值
}

/**
 * 向线程池提交任务
 * @param pool 线程池指针
 * @param function 任务函数
 * @param arg 任务参数
 */
bool pool_submit(thread_pool_t *pool, void (*function)(void *), void *arg) {
    // TODO: 创建新的任务节点

    // TODO: 加锁，将任务添加到队列尾部

    // TODO: 通过条件变量通知一个等待中的工作线程

    // TODO: 解锁

    return false; // 成功提交后改为 true
}

/**
 * 销毁线程池
 * 通知所有线程退出，等待它们完成后释放资源
 */
void pool_destroy(thread_pool_t *pool) {
    // TODO: 加锁，设置 shutdown 标志

    // TODO: 广播条件变量，唤醒所有等待的线程

    // TODO: 解锁

    // TODO: 等待所有工作线程结束 (pthread_join)

    // TODO: 释放所有资源（互斥锁、条件变量、线程数组、线程池）
}

/* 示例任务函数 */
void example_task(void *arg) {
    int task_num = *(int *)arg;
    printf("  任务 %d 正在线程 %lu 中执行\n", task_num, (unsigned long)pthread_self());
    free(arg);
}

int main(void) {
    printf("=== 线程池测试 ===\n\n");

    // 创建包含 4 个工作线程的线程池
    thread_pool_t *pool = pool_create(4);
    if (!pool) {
        fprintf(stderr, "创建线程池失败\n");
        return 1;
    }
    printf("线程池已创建（4个工作线程）\n\n");

    // 提交 20 个任务
    printf("提交 20 个任务...\n");
    for (int i = 0; i < 20; i++) {
        int *task_num = malloc(sizeof(int));
        if (!task_num) {
            fprintf(stderr, "任务参数分配失败\n");
            pool_destroy(pool);
            return 1;
        }
        *task_num = i + 1;
        if (!pool_submit(pool, example_task, task_num)) {
            free(task_num); // 提交失败时所有权仍属于调用者
            fprintf(stderr, "任务提交失败\n");
            pool_destroy(pool);
            return 1;
        }
    }

    // 销毁会停止接收任务、排空队列并等待工作线程退出
    pool_destroy(pool);
    printf("\n线程池已销毁\n");

    return 0;
}
