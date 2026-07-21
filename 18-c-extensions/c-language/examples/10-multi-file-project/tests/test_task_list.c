#include "task_list.h"
#include "task_store.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static void test_add_complete_and_remove(void) {
    TaskList list;
    task_list_init(&list);

    Task *first;
    assert(task_list_add(&list, "learn headers", &first));
    assert(first->id == 1);
    assert(strcmp(first->title, "learn headers") == 0);
    assert(!first->completed);

    assert(task_list_add(&list, "learn linking", NULL));
    assert(task_list_complete(&list, 2));
    assert(list.items[1].completed);
    assert(task_list_remove(&list, 1));
    assert(list.count == 1);
    assert(list.items[0].id == 2);
    assert(!task_list_remove(&list, 99));
}

static void test_rejects_invalid_titles(void) {
    TaskList list;
    task_list_init(&list);

    char long_title[TASK_TITLE_CAPACITY + 1];
    memset(long_title, 'a', sizeof long_title - 1);
    long_title[sizeof long_title - 1] = '\0';

    assert(!task_list_add(&list, "", NULL));
    assert(!task_list_add(&list, long_title, NULL));
    assert(list.count == 0);
    assert(list.next_id == 1);
}

static void test_store_round_trip(void) {
    const char *path = "/tmp/tasker-multi-file-test.tsv";
    TaskList original;
    task_list_init(&original);
    assert(task_list_add(&original, "persist me", NULL));
    assert(task_list_complete(&original, 1));
    assert(task_store_save(path, &original));

    TaskList loaded;
    assert(task_store_load(path, &loaded));
    assert(loaded.count == 1);
    assert(loaded.next_id == 2);
    assert(loaded.items[0].completed);
    assert(strcmp(loaded.items[0].title, "persist me") == 0);
    assert(remove(path) == 0);
}

int main(void) {
    test_add_complete_and_remove();
    test_rejects_invalid_titles();
    test_store_round_trip();
    puts("21-multi-file-project tests passed.");
    return 0;
}
