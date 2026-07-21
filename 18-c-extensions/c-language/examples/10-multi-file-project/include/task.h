#ifndef TASKER_TASK_H
#define TASKER_TASK_H

#include <stdbool.h>
#include <stddef.h>

#define TASK_TITLE_CAPACITY 128

typedef struct {
    unsigned long id;
    bool completed;
    char title[TASK_TITLE_CAPACITY];
} Task;

bool task_create(Task *task, unsigned long id, const char *title);
void task_complete(Task *task);

#endif
