#ifndef STUDENT_MANAGER_STUDENT_H
#define STUDENT_MANAGER_STUDENT_H

#include <stdbool.h>

#define STUDENT_NAME_CAPACITY 64

typedef struct {
    int id;
    char name[STUDENT_NAME_CAPACITY];
    double score;
} Student;

bool student_create(Student *student, int id, const char *name, double score);

#endif

