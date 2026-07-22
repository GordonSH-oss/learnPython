#ifndef STUDENT_MANAGER_REGISTRY_H
#define STUDENT_MANAGER_REGISTRY_H

#include "student.h"

#include <stdbool.h>
#include <stddef.h>

/*
 * 可动态扩容的学生数组。
 * size 表示已初始化元素数量，capacity 表示当前已分配的元素空间。
 */
typedef struct {
    Student *items;
    size_t size;
    size_t capacity;
} StudentRegistry;

typedef struct {
    double average;
    double minimum;
    double maximum;
} ScoreStatistics;

/* 首次使用前必须初始化，使用结束后必须销毁。 */
void student_registry_init(StudentRegistry *registry);
void student_registry_destroy(StudentRegistry *registry);

/* 学号必须唯一；学号重复或内存分配失败时返回 false。 */
bool student_registry_add(StudentRegistry *registry, Student student);

/* 返回的指针指向注册表内部存储，扩容、删除或销毁后可能失效。 */
Student *student_registry_find(StudentRegistry *registry, int id);
const Student *student_registry_find_const(const StudentRegistry *registry, int id);

bool student_registry_remove(StudentRegistry *registry, int id);

/* 空注册表没有统计结果，此时返回 false。 */
bool student_registry_statistics(const StudentRegistry *registry,
                                 ScoreStatistics *statistics);

/* 原地排序，会直接改变 items 中的元素顺序。 */
void student_registry_sort_by_score(StudentRegistry *registry, bool descending);

#endif
