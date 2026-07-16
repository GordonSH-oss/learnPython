// 16_threads.c - 多线程编程
// 编译: clang -std=c17 -Wall -Wextra -Wpedantic -pthread 16_threads.c -o 16_threads
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

/* === 1. 基本线程创建 === */
void *hello_thread(void *arg) {
    int id = *(int *)arg;
    printf("线程 %d: 你好!\n", id);
    return NULL;
}

/* === 2. 竞态条件演示 === */
#define NUM_THREADS 4
#define INCREMENTS 100000
int shared_counter = 0;         // 共享计数器(无保护)
int safe_counter = 0;           // 共享计数器(有保护)
pthread_mutex_t counter_lock = PTHREAD_MUTEX_INITIALIZER;

void *unsafe_increment(void *arg) {
    (void)arg;
    for (int i = 0; i < INCREMENTS; i++)
        shared_counter++;       // 竞态条件!
    return NULL;
}
/* === 3. 互斥锁修复 === */
void *safe_increment(void *arg) {
    (void)arg;
    for (int i = 0; i < INCREMENTS; i++) {
        pthread_mutex_lock(&counter_lock);
        safe_counter++;
        pthread_mutex_unlock(&counter_lock);
    }
    return NULL;
}
/* === 4. 生产者-消费者(条件变量) === */
#define BUFFER_SIZE 5
int buffer[BUFFER_SIZE], count = 0;
pthread_mutex_t buf_lock = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t not_empty = PTHREAD_COND_INITIALIZER;
pthread_cond_t not_full = PTHREAD_COND_INITIALIZER;

void *producer(void *arg) {
    (void)arg;
    for (int i = 1; i <= 8; i++) {
        pthread_mutex_lock(&buf_lock);
        while (count == BUFFER_SIZE) pthread_cond_wait(&not_full, &buf_lock);
        buffer[count++] = i;
        printf("生产: %d (缓冲区: %d/%d)\n", i, count, BUFFER_SIZE);
        pthread_cond_signal(&not_empty);
        pthread_mutex_unlock(&buf_lock);
        usleep(50000);
    }
    return NULL;
}

void *consumer(void *arg) {
    (void)arg;
    for (int i = 0; i < 8; i++) {
        pthread_mutex_lock(&buf_lock);
        while (count == 0) pthread_cond_wait(&not_empty, &buf_lock);
        int item = buffer[--count];
        printf("消费: %d (缓冲区: %d/%d)\n", item, count, BUFFER_SIZE);
        pthread_cond_signal(&not_full);
        pthread_mutex_unlock(&buf_lock);
        usleep(80000);
    }
    return NULL;
}

int main(void) {
    pthread_t t, threads[NUM_THREADS];

    // 1. 基本线程
    printf("=== 基本线程创建 ===\n");
    int id = 1;
    pthread_create(&t, NULL, hello_thread, &id);
    pthread_join(t, NULL);

    // 2. 竞态条件
    printf("\n=== 竞态条件(无锁) ===\n");
    for (int i = 0; i < NUM_THREADS; i++)
        pthread_create(&threads[i], NULL, unsafe_increment, NULL);
    for (int i = 0; i < NUM_THREADS; i++)
        pthread_join(threads[i], NULL);
    printf("期望: %d, 实际: %d (可能不一致!)\n", NUM_THREADS * INCREMENTS, shared_counter);

    // 3. 互斥锁修复
    printf("\n=== 互斥锁保护(有锁) ===\n");
    for (int i = 0; i < NUM_THREADS; i++)
        pthread_create(&threads[i], NULL, safe_increment, NULL);
    for (int i = 0; i < NUM_THREADS; i++)
        pthread_join(threads[i], NULL);
    printf("期望: %d, 实际: %d (始终一致)\n", NUM_THREADS * INCREMENTS, safe_counter);

    // 4. 生产者-消费者
    printf("\n=== 生产者-消费者 ===\n");
    pthread_t prod, cons;
    pthread_create(&prod, NULL, producer, NULL);
    pthread_create(&cons, NULL, consumer, NULL);
    pthread_join(prod, NULL);
    pthread_join(cons, NULL);

    pthread_mutex_destroy(&counter_lock);
    pthread_mutex_destroy(&buf_lock);
    pthread_cond_destroy(&not_empty);
    pthread_cond_destroy(&not_full);
    printf("\n完成!\n");
    return 0;
}
