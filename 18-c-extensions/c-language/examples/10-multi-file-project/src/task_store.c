#include "task_store.h"

#include <stdio.h>
#include <string.h>

static void remove_line_ending(char *text) {
    text[strcspn(text, "\r\n")] = '\0';
}

bool task_store_load(const char *path, TaskList *list) {
    if (path == NULL || list == NULL) return false;

    FILE *file = fopen(path, "r");
    if (file == NULL) {
        task_list_init(list);
        return true;
    }

    TaskList loaded;
    task_list_init(&loaded);
    char line[256];

    while (fgets(line, sizeof line, file) != NULL) {
        Task task;
        int completed;
        int consumed;

        remove_line_ending(line);
        if (sscanf(line, "%lu\t%d\t%n", &task.id, &completed, &consumed) != 2 ||
            line[consumed] == '\0' || strlen(&line[consumed]) >= TASK_TITLE_CAPACITY ||
            loaded.count >= TASK_LIST_CAPACITY) {
            fclose(file);
            return false;
        }

        task.completed = completed != 0;
        strcpy(task.title, &line[consumed]);
        loaded.items[loaded.count++] = task;
        if (task.id >= loaded.next_id) loaded.next_id = task.id + 1;
    }

    if (ferror(file) != 0 || fclose(file) != 0) return false;
    *list = loaded;
    return true;
}

bool task_store_save(const char *path, const TaskList *list) {
    if (path == NULL || list == NULL) return false;

    FILE *file = fopen(path, "w");
    if (file == NULL) return false;

    for (size_t index = 0; index < list->count; index++) {
        const Task *task = &list->items[index];
        if (fprintf(file, "%lu\t%d\t%s\n", task->id, task->completed, task->title) < 0) {
            fclose(file);
            return false;
        }
    }

    return fclose(file) == 0;
}
