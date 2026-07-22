#include "student.h"

#include <stdio.h>

bool student_create(Student *student, int id, const char *name, double score) {
    if (student == NULL || name == NULL || id <= 0 || name[0] == '\0' ||
        score < 0.0 || score > 100.0) {
        return false;
    }
    int written = snprintf(student->name, sizeof student->name, "%s", name);
    if (written < 0 || (size_t)written >= sizeof student->name) return false;
    student->id = id;
    student->score = score;
    return true;
}

