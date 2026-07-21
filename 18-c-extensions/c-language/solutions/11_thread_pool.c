/**
 * 练习 11: 固定大小线程池参考答案
 * 提交成功后任务参数所有权转移给任务函数；提交失败仍归调用者。
 */
#include <pthread.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct task {
    void (*function)(void *argument);
    void *argument;
    struct task *next;
} task_t;

typedef struct {
    pthread_t *threads;
    int thread_count;
    int created_threads;
    task_t *queue_head;
    task_t *queue_tail;
    pthread_mutex_t mutex;
    pthread_cond_t task_available;
    bool shutting_down;
} thread_pool_t;

static void report_pthread_error(const char *operation, int error) {
    fprintf(stderr, "%s: %s\n", operation, strerror(error));
}

static void *worker_thread(void *argument) {
    thread_pool_t *pool = argument;

    for (;;) {
        int error = pthread_mutex_lock(&pool->mutex);
        if (error != 0) {
            report_pthread_error("pthread_mutex_lock", error);
            return NULL;
        }

        while (pool->queue_head == NULL && !pool->shutting_down) {
            error = pthread_cond_wait(&pool->task_available, &pool->mutex);
            if (error != 0) {
                report_pthread_error("pthread_cond_wait", error);
                pthread_mutex_unlock(&pool->mutex);
                return NULL;
            }
        }

        if (pool->queue_head == NULL && pool->shutting_down) {
            pthread_mutex_unlock(&pool->mutex);
            return NULL;
        }

        task_t *task = pool->queue_head;
        pool->queue_head = task->next;
        if (pool->queue_head == NULL) pool->queue_tail = NULL;
        pthread_mutex_unlock(&pool->mutex);

        task->function(task->argument);
        free(task);
    }
}

static void stop_and_join_created_threads(thread_pool_t *pool) {
    pthread_mutex_lock(&pool->mutex);
    pool->shutting_down = true;
    pthread_cond_broadcast(&pool->task_available);
    pthread_mutex_unlock(&pool->mutex);

    for (int i = 0; i < pool->created_threads; ++i) {
        int error = pthread_join(pool->threads[i], NULL);
        if (error != 0) report_pthread_error("pthread_join", error);
    }
}

thread_pool_t *pool_create(int thread_count) {
    if (thread_count <= 0) return NULL;

    thread_pool_t *pool = calloc(1, sizeof *pool);
    if (pool == NULL) return NULL;
    pool->thread_count = thread_count;

    int error = pthread_mutex_init(&pool->mutex, NULL);
    if (error != 0) {
        report_pthread_error("pthread_mutex_init", error);
        free(pool);
        return NULL;
    }
    error = pthread_cond_init(&pool->task_available, NULL);
    if (error != 0) {
        report_pthread_error("pthread_cond_init", error);
        pthread_mutex_destroy(&pool->mutex);
        free(pool);
        return NULL;
    }

    pool->threads = calloc((size_t)thread_count, sizeof *pool->threads);
    if (pool->threads == NULL) {
        pthread_cond_destroy(&pool->task_available);
        pthread_mutex_destroy(&pool->mutex);
        free(pool);
        return NULL;
    }

    for (int i = 0; i < thread_count; ++i) {
        error = pthread_create(&pool->threads[i], NULL, worker_thread, pool);
        if (error != 0) {
            report_pthread_error("pthread_create", error);
            stop_and_join_created_threads(pool);
            pthread_cond_destroy(&pool->task_available);
            pthread_mutex_destroy(&pool->mutex);
            free(pool->threads);
            free(pool);
            return NULL;
        }
        ++pool->created_threads;
    }
    return pool;
}

bool pool_submit(thread_pool_t *pool,
                 void (*function)(void *), void *argument) {
    if (pool == NULL || function == NULL) return false;

    task_t *task = malloc(sizeof *task);
    if (task == NULL) return false;
    task->function = function;
    task->argument = argument;
    task->next = NULL;

    int error = pthread_mutex_lock(&pool->mutex);
    if (error != 0) {
        report_pthread_error("pthread_mutex_lock", error);
        free(task);
        return false;
    }
    if (pool->shutting_down) {
        pthread_mutex_unlock(&pool->mutex);
        free(task);
        return false;
    }

    if (pool->queue_tail != NULL) {
        pool->queue_tail->next = task;
    } else {
        pool->queue_head = task;
    }
    pool->queue_tail = task;
    error = pthread_cond_signal(&pool->task_available);
    pthread_mutex_unlock(&pool->mutex);
    if (error != 0) report_pthread_error("pthread_cond_signal", error);
    return true;
}

void pool_destroy(thread_pool_t *pool) {
    if (pool == NULL) return;

    stop_and_join_created_threads(pool);

    task_t *task = pool->queue_head;
    while (task != NULL) {
        task_t *next = task->next;
        free(task);
        task = next;
    }

    pthread_cond_destroy(&pool->task_available);
    pthread_mutex_destroy(&pool->mutex);
    free(pool->threads);
    free(pool);
}

static void example_task(void *argument) {
    int task_number = *(int *)argument;
    printf("task %d completed\n", task_number);
    free(argument);
}

int main(void) {
    thread_pool_t *pool = pool_create(4);
    if (pool == NULL) {
        fputs("failed to create thread pool\n", stderr);
        return EXIT_FAILURE;
    }

    for (int i = 0; i < 20; ++i) {
        int *task_number = malloc(sizeof *task_number);
        if (task_number == NULL) {
            pool_destroy(pool);
            return EXIT_FAILURE;
        }
        *task_number = i + 1;
        if (!pool_submit(pool, example_task, task_number)) {
            free(task_number);
            pool_destroy(pool);
            return EXIT_FAILURE;
        }
    }

    pool_destroy(pool);
    puts("all queued tasks completed");
    return EXIT_SUCCESS;
}
