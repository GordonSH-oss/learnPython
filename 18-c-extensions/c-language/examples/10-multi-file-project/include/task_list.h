#ifndef TASKER_TASK_LIST_H
#define TASKER_TASK_LIST_H

#include "task.h"

#include <stdbool.h>
#include <stddef.h>

#define TASK_LIST_CAPACITY 100

typedef struct {
    Task items[TASK_LIST_CAPACITY];
    size_t count;
    unsigned long next_id;
} TaskList;

void task_list_init(TaskList *list);
bool task_list_add(TaskList *list, const char *title, Task **added_task);
Task *task_list_find(TaskList *list, unsigned long id);
bool task_list_complete(TaskList *list, unsigned long id);
bool task_list_remove(TaskList *list, unsigned long id);

#endif
