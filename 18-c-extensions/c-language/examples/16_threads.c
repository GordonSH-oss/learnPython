/**
 * 16_threads.c - POSIX 线程、原子计数和 FIFO 条件变量队列
 */
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define THREAD_COUNT 4
#define INCREMENTS 100000
#define BUFFER_CAPACITY 5
#define ITEM_COUNT 12

static void report_pthread_error(const char *operation, int error) {
    fprintf(stderr, "%s: %s\n", operation, strerror(error));
}

static atomic_long atomic_counter = 0;
static long mutex_counter = 0;
static pthread_mutex_t counter_mutex = PTHREAD_MUTEX_INITIALIZER;

static void *count_with_atomics(void *unused) {
    (void)unused;
    for (int i = 0; i < INCREMENTS; ++i) {
        atomic_fetch_add(&atomic_counter, 1);
    }
    return NULL;
}

static void *count_with_mutex(void *unused) {
    (void)unused;
    long local_total = 0;
    for (int i = 0; i < INCREMENTS; ++i) {
        ++local_total;
    }
    pthread_mutex_lock(&counter_mutex);
    mutex_counter += local_total;
    pthread_mutex_unlock(&counter_mutex);
    return NULL;
}

typedef struct {
    int items[BUFFER_CAPACITY];
    size_t head;
    size_t tail;
    size_t count;
    pthread_mutex_t mutex;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
} Queue;

static Queue queue = {
    .mutex = PTHREAD_MUTEX_INITIALIZER,
    .not_empty = PTHREAD_COND_INITIALIZER,
    .not_full = PTHREAD_COND_INITIALIZER,
};

static void *producer(void *unused) {
    (void)unused;
    for (int item = 1; item <= ITEM_COUNT; ++item) {
        pthread_mutex_lock(&queue.mutex);
        while (queue.count == BUFFER_CAPACITY) {
            pthread_cond_wait(&queue.not_full, &queue.mutex);
        }
        queue.items[queue.tail] = item;
        queue.tail = (queue.tail + 1) % BUFFER_CAPACITY;
        ++queue.count;
        pthread_cond_signal(&queue.not_empty);
        pthread_mutex_unlock(&queue.mutex);
    }
    return NULL;
}

static void *consumer(void *unused) {
    (void)unused;
    for (int index = 0; index < ITEM_COUNT; ++index) {
        pthread_mutex_lock(&queue.mutex);
        while (queue.count == 0) {
            pthread_cond_wait(&queue.not_empty, &queue.mutex);
        }
        int item = queue.items[queue.head];
        queue.head = (queue.head + 1) % BUFFER_CAPACITY;
        --queue.count;
        pthread_cond_signal(&queue.not_full);
        pthread_mutex_unlock(&queue.mutex);
        printf("consumed %d\n", item);
    }
    return NULL;
}

static int run_workers(void *(*worker)(void *), const char *label) {
    pthread_t threads[THREAD_COUNT];
    int created = 0;
    for (; created < THREAD_COUNT; ++created) {
        int error = pthread_create(&threads[created], NULL, worker, NULL);
        if (error != 0) {
            report_pthread_error("pthread_create", error);
            break;
        }
    }

    int result = created == THREAD_COUNT ? 0 : -1;
    for (int i = 0; i < created; ++i) {
        int error = pthread_join(threads[i], NULL);
        if (error != 0) {
            report_pthread_error("pthread_join", error);
            result = -1;
        }
    }
    if (result == 0) printf("%s workers joined\n", label);
    return result;
}

int main(void) {
    if (run_workers(count_with_atomics, "atomic") < 0) return EXIT_FAILURE;
    printf("atomic counter: %ld\n", atomic_load(&atomic_counter));

    if (run_workers(count_with_mutex, "mutex") < 0) return EXIT_FAILURE;
    printf("mutex counter: %ld\n", mutex_counter);

    pthread_t producer_thread;
    pthread_t consumer_thread;
    int error = pthread_create(&consumer_thread, NULL, consumer, NULL);
    if (error != 0) {
        report_pthread_error("pthread_create consumer", error);
        return EXIT_FAILURE;
    }
    error = pthread_create(&producer_thread, NULL, producer, NULL);
    if (error != 0) {
        report_pthread_error("pthread_create producer", error);
        pthread_cancel(consumer_thread);
        pthread_join(consumer_thread, NULL);
        return EXIT_FAILURE;
    }

    int producer_error = pthread_join(producer_thread, NULL);
    int consumer_error = pthread_join(consumer_thread, NULL);
    if (producer_error != 0 || consumer_error != 0) {
        if (producer_error != 0) report_pthread_error("join producer", producer_error);
        if (consumer_error != 0) report_pthread_error("join consumer", consumer_error);
        return EXIT_FAILURE;
    }

    pthread_mutex_destroy(&counter_mutex);
    pthread_mutex_destroy(&queue.mutex);
    pthread_cond_destroy(&queue.not_empty);
    pthread_cond_destroy(&queue.not_full);
    return EXIT_SUCCESS;
}
