/**
 * 练习 11: 线程池 (Thread Pool) - 参考答案
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

/* 工作线程函数：循环等待任务，取出并执行 */
void *worker_thread(void *arg) {
    thread_pool_t *pool = (thread_pool_t *)arg;

    while (true) {
        pthread_mutex_lock(&pool->mutex);

        /* 当队列为空且未关闭时，等待条件变量 */
        while (!pool->queue_head && !pool->shutdown) {
            pthread_cond_wait(&pool->cond, &pool->mutex);
        }

        /* 如果收到关闭信号且队列已空，退出 */
        if (pool->shutdown && !pool->queue_head) {
            pthread_mutex_unlock(&pool->mutex);
            pthread_exit(NULL);
        }

        /* 从队列头部取出任务 */
        task_t *task = pool->queue_head;
        pool->queue_head = task->next;
        if (!pool->queue_head) {
            pool->queue_tail = NULL;
        }

        pthread_mutex_unlock(&pool->mutex);

        /* 执行任务并释放节点 */
        task->function(task->arg);
        free(task);
    }
    return NULL;
}

/* 创建线程池 */
thread_pool_t *pool_create(int num_threads) {
    thread_pool_t *pool = malloc(sizeof(thread_pool_t));
    if (!pool) return NULL;

    pool->thread_count = num_threads;
    pool->queue_head = NULL;
    pool->queue_tail = NULL;
    pool->shutdown = false;

    pthread_mutex_init(&pool->mutex, NULL);
    pthread_cond_init(&pool->cond, NULL);

    pool->threads = malloc(sizeof(pthread_t) * (size_t)num_threads);
    if (!pool->threads) {
        free(pool);
        return NULL;
    }

    for (int i = 0; i < num_threads; i++) {
        pthread_create(&pool->threads[i], NULL, worker_thread, pool);
    }
    return pool;
}

/* 向线程池提交任务 */
void pool_submit(thread_pool_t *pool, void (*function)(void *), void *arg) {
    task_t *new_task = malloc(sizeof(task_t));
    if (!new_task) return;

    new_task->function = function;
    new_task->arg = arg;
    new_task->next = NULL;

    pthread_mutex_lock(&pool->mutex);
    if (pool->queue_tail) {
        pool->queue_tail->next = new_task;
    } else {
        pool->queue_head = new_task;
    }
    pool->queue_tail = new_task;
    pthread_cond_signal(&pool->cond);
    pthread_mutex_unlock(&pool->mutex);
}

/* 销毁线程池：通知所有线程退出，等待完成后释放资源 */
void pool_destroy(thread_pool_t *pool) {
    pthread_mutex_lock(&pool->mutex);
    pool->shutdown = true;
    pthread_cond_broadcast(&pool->cond);
    pthread_mutex_unlock(&pool->mutex);

    /* 等待所有工作线程结束 */
    for (int i = 0; i < pool->thread_count; i++) {
        pthread_join(pool->threads[i], NULL);
    }

    /* 清理可能残留的任务 */
    task_t *task = pool->queue_head;
    while (task) {
        task_t *next = task->next;
        free(task);
        task = next;
    }

    pthread_mutex_destroy(&pool->mutex);
    pthread_cond_destroy(&pool->cond);
    free(pool->threads);
    free(pool);
}

/* 示例任务函数 */
void example_task(void *arg) {
    int task_num = *(int *)arg;
    printf("  任务 %d 正在线程 %lu 中执行\n", task_num, (unsigned long)pthread_self());
    free(arg);
}

int main(void) {
    printf("=== 线程池测试 ===\n\n");

    thread_pool_t *pool = pool_create(4);
    if (!pool) {
        fprintf(stderr, "创建线程池失败\n");
        return 1;
    }
    printf("线程池已创建（4个工作线程）\n\n");

    printf("提交 20 个任务...\n");
    for (int i = 0; i < 20; i++) {
        int *task_num = malloc(sizeof(int));
        *task_num = i + 1;
        pool_submit(pool, example_task, task_num);
    }

    printf("\n等待任务完成...\n");
    usleep(500000);

    pool_destroy(pool);
    printf("\n线程池已销毁\n");

    return 0;
}
