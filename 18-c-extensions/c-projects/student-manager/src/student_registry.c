#include "student_registry.h"

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

void student_registry_init(StudentRegistry *registry) {
    if (registry == NULL) return;
    registry->items = NULL;
    registry->size = 0;
    registry->capacity = 0;
}

void student_registry_destroy(StudentRegistry *registry) {
    if (registry == NULL) return;
    free(registry->items);
    student_registry_init(registry);
}

static bool ensure_capacity(StudentRegistry *registry) {
    if (registry->size < registry->capacity) return true;
    size_t new_capacity = registry->capacity == 0 ? 8 : registry->capacity * 2;
    if (new_capacity < registry->capacity ||
        new_capacity > SIZE_MAX / sizeof *registry->items) return false;
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
    return (Student *)student_registry_find_const(registry, id);
}

bool student_registry_add(StudentRegistry *registry, Student student) {
    if (registry == NULL || student_registry_find_const(registry, student.id) != NULL)
        return false;
    if (!ensure_capacity(registry)) return false;
    registry->items[registry->size++] = student;
    return true;
}

bool student_registry_remove(StudentRegistry *registry, int id) {
    if (registry == NULL) return false;
    for (size_t index = 0; index < registry->size; ++index) {
        if (registry->items[index].id == id) {
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
    return (a->score > b->score) - (a->score < b->score);
}

static int score_descending(const void *left, const void *right) {
    return score_ascending(right, left);
}

void student_registry_sort_by_score(StudentRegistry *registry, bool descending) {
    if (registry == NULL || registry->size < 2) return;
    qsort(registry->items, registry->size, sizeof *registry->items,
          descending ? score_descending : score_ascending);
}

