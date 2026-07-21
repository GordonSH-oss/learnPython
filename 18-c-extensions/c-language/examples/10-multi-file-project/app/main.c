#include "task_list.h"
#include "task_store.h"

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DEFAULT_STORE_PATH "tasks.tsv"

static void print_usage(const char *program) {
    printf("Usage:\n");
    printf("  %s add <title>\n", program);
    printf("  %s list\n", program);
    printf("  %s done <id>\n", program);
    printf("  %s remove <id>\n", program);
    printf("Set TASKER_FILE to choose a different data file.\n");
}

static bool parse_id(const char *text, unsigned long *id) {
    if (text == NULL || id == NULL || text[0] == '\0') return false;

    errno = 0;
    char *end;
    unsigned long value = strtoul(text, &end, 10);
    if (errno != 0 || *end != '\0' || value == 0) return false;

    *id = value;
    return true;
}

static void print_tasks(const TaskList *list) {
    if (list->count == 0) {
        puts("No tasks.");
        return;
    }

    for (size_t index = 0; index < list->count; index++) {
        const Task *task = &list->items[index];
        printf("%lu [%c] %s\n", task->id, task->completed ? 'x' : ' ', task->title);
    }
}

int main(int argc, char **argv) {
    if (argc < 2) {
        print_usage(argv[0]);
        return 0;
    }

    const char *store_path = getenv("TASKER_FILE");
    if (store_path == NULL || store_path[0] == '\0') store_path = DEFAULT_STORE_PATH;

    TaskList list;
    if (!task_store_load(store_path, &list)) {
        fprintf(stderr, "Could not load tasks from %s\n", store_path);
        return 1;
    }

    bool changed = false;
    if (strcmp(argv[1], "list") == 0 && argc == 2) {
        print_tasks(&list);
    } else if (strcmp(argv[1], "add") == 0 && argc == 3) {
        Task *added;
        if (!task_list_add(&list, argv[2], &added)) {
            fputs("Could not add task. Check the title or list capacity.\n", stderr);
            return 1;
        }
        printf("Added task %lu.\n", added->id);
        changed = true;
    } else if ((strcmp(argv[1], "done") == 0 || strcmp(argv[1], "remove") == 0) && argc == 3) {
        unsigned long id;
        if (!parse_id(argv[2], &id)) {
            fputs("Task id must be a positive integer.\n", stderr);
            return 1;
        }

        bool succeeded = strcmp(argv[1], "done") == 0
            ? task_list_complete(&list, id)
            : task_list_remove(&list, id);
        if (!succeeded) {
            fprintf(stderr, "Task %lu was not found.\n", id);
            return 1;
        }
        changed = true;
    } else {
        print_usage(argv[0]);
        return 1;
    }

    if (changed && !task_store_save(store_path, &list)) {
        fprintf(stderr, "Could not save tasks to %s\n", store_path);
        return 1;
    }
    return 0;
}
