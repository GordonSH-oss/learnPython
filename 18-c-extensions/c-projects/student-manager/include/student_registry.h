#ifndef STUDENT_MANAGER_REGISTRY_H
#define STUDENT_MANAGER_REGISTRY_H

#include "student.h"

#include <stdbool.h>
#include <stddef.h>

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

void student_registry_init(StudentRegistry *registry);
void student_registry_destroy(StudentRegistry *registry);
bool student_registry_add(StudentRegistry *registry, Student student);
Student *student_registry_find(StudentRegistry *registry, int id);
const Student *student_registry_find_const(const StudentRegistry *registry, int id);
bool student_registry_remove(StudentRegistry *registry, int id);
bool student_registry_statistics(const StudentRegistry *registry,
                                 ScoreStatistics *statistics);
void student_registry_sort_by_score(StudentRegistry *registry, bool descending);

#endif

