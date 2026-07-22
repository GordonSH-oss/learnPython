#include "student_registry.h"

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

void student_registry_init(StudentRegistry *registry) {
    if (registry == NULL) return;
    /* NULL 指针配合零 size、零 capacity 表示有效的空状态。 */
    registry->items = NULL;
    registry->size = 0;
    registry->capacity = 0;
}

void student_registry_destroy(StudentRegistry *registry) {
    if (registry == NULL) return;
    free(registry->items);
    /* 释放后重置字段，避免对象中残留悬空指针。 */
    student_registry_init(registry);
}

static bool ensure_capacity(StudentRegistry *registry) {
    if (registry->size < registry->capacity) return true;

    /* 按倍数扩容，避免每次添加学生都重新分配内存。 */
    size_t new_capacity = registry->capacity == 0 ? 8 : registry->capacity * 2;

    /* 同时防止容量翻倍和“元素数乘元素大小”发生整数溢出。 */
    if (new_capacity < registry->capacity ||
        new_capacity > SIZE_MAX / sizeof *registry->items) return false;

    /* realloc 可能移动内存；先用临时指针，失败时才能保留原数组。 */
    Student *items = realloc(registry->items,
                             new_capacity * sizeof *registry->items);
    if (items == NULL) return false;
    registry->items = items;
    registry->capacity = new_capacity;
    return true;
}

const Student *student_registry_find_const(const StudentRegistry *registry, int id) {
    if (registry == NULL) return NULL;
    for (size_t index = 0; index < registry->size; ++index) {
        if (registry->items[index].id == id) return &registry->items[index];
    }
    return NULL;
}

Student *student_registry_find(StudentRegistry *registry, int id) {
    /* 复用只读查找；传入的是可修改注册表，因此这里可以去掉 const。 */
    return (Student *)student_registry_find_const(registry, id);
}

bool student_registry_add(StudentRegistry *registry, Student student) {
    if (registry == NULL || student_registry_find_const(registry, student.id) != NULL)
        return false;
    if (!ensure_capacity(registry)) return false;
    /* 后置自增先按旧 size 写入元素，再把元素数量加一。 */
    registry->items[registry->size++] = student;
    return true;
}

bool student_registry_remove(StudentRegistry *registry, int id) {
    if (registry == NULL) return false;
    for (size_t index = 0; index < registry->size; ++index) {
        if (registry->items[index].id == id) {
            /* 源和目标区域可能重叠，因此必须使用 memmove 而不是 memcpy。 */
            memmove(&registry->items[index], &registry->items[index + 1],
                    (registry->size - index - 1) * sizeof *registry->items);
            --registry->size;
            return true;
        }
    }
    return false;
}

bool student_registry_statistics(const StudentRegistry *registry,
                                 ScoreStatistics *statistics) {
    if (registry == NULL || statistics == NULL || registry->size == 0) return false;

    /* 用第一个成绩初始化统计值，无需人为选择最大值或最小值哨兵。 */
    double total = registry->items[0].score;
    double minimum = total;
    double maximum = total;
    for (size_t index = 1; index < registry->size; ++index) {
        double score = registry->items[index].score;
        total += score;
        if (score < minimum) minimum = score;
        if (score > maximum) maximum = score;
    }
    statistics->average = total / (double)registry->size;
    statistics->minimum = minimum;
    statistics->maximum = maximum;
    return true;
}

static int score_ascending(const void *left, const void *right) {
    const Student *a = left;
    const Student *b = right;
    /* qsort 只要求负数、零或正数；这种写法还避免浮点差值转 int。 */
    return (a->score > b->score) - (a->score < b->score);
}

static int score_descending(const void *left, const void *right) {
    return score_ascending(right, left);
}

void student_registry_sort_by_score(StudentRegistry *registry, bool descending) {
    if (registry == NULL || registry->size < 2) return;
    /* qsort 面向原始数组，因此需要元素数量、单个元素字节数和比较函数。 */
    qsort(registry->items, registry->size, sizeof *registry->items,
          descending ? score_descending : score_ascending);
}
