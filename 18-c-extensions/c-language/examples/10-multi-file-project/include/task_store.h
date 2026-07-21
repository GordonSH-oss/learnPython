#ifndef TASKER_TASK_STORE_H
#define TASKER_TASK_STORE_H

#include "task_list.h"

#include <stdbool.h>

bool task_store_load(const char *path, TaskList *list);
bool task_store_save(const char *path, const TaskList *list);

#endif
