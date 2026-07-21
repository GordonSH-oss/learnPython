#include "task_list.h"

void task_list_init(TaskList *list) {
    if (list == NULL) return;
    list->count = 0;
    list->next_id = 1;
}

bool task_list_add(TaskList *list, const char *title, Task **added_task) {
    if (list == NULL || list->count >= TASK_LIST_CAPACITY) return false;

    Task *task = &list->items[list->count];
    if (!task_create(task, list->next_id, title)) return false;

    list->count++;
    list->next_id++;
    if (added_task != NULL) *added_task = task;
    return true;
}

Task *task_list_find(TaskList *list, unsigned long id) {
    if (list == NULL) return NULL;

    for (size_t index = 0; index < list->count; index++) {
        if (list->items[index].id == id) return &list->items[index];
    }
    return NULL;
}

bool task_list_complete(TaskList *list, unsigned long id) {
    Task *task = task_list_find(list, id);
    if (task == NULL) return false;
    task_complete(task);
    return true;
}

bool task_list_remove(TaskList *list, unsigned long id) {
    if (list == NULL) return false;

    for (size_t index = 0; index < list->count; index++) {
        if (list->items[index].id != id) continue;

        for (size_t next = index + 1; next < list->count; next++) {
            list->items[next - 1] = list->items[next];
        }
        list->count--;
        return true;
    }
    return false;
}
