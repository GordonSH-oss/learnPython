#include "task.h"

#include <string.h>

bool task_create(Task *task, unsigned long id, const char *title) {
    if (task == NULL || title == NULL || title[0] == '\0') return false;

    size_t title_length = strlen(title);
    if (title_length >= TASK_TITLE_CAPACITY) return false;

    task->id = id;
    task->completed = false;
    memcpy(task->title, title, title_length + 1);
    return true;
}

void task_complete(Task *task) {
    if (task != NULL) task->completed = true;
}
