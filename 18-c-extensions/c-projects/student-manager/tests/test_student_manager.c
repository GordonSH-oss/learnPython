#include "student_registry.h"

#include <assert.h>
#include <string.h>

int main(void) {
    Student invalid;
    assert(!student_create(&invalid, 0, "Ada", 90));
    assert(!student_create(&invalid, 1, "Ada", 101));

    StudentRegistry registry;
    student_registry_init(&registry);
    Student ada;
    Student grace;
    assert(student_create(&ada, 1, "Ada", 88.5));
    assert(student_create(&grace, 2, "Grace", 96.0));
    assert(student_registry_add(&registry, ada));
    assert(student_registry_add(&registry, grace));
    assert(!student_registry_add(&registry, ada));
    assert(strcmp(student_registry_find(&registry, 2)->name, "Grace") == 0);

    ScoreStatistics statistics;
    assert(student_registry_statistics(&registry, &statistics));
    assert(statistics.average == 92.25);
    student_registry_sort_by_score(&registry, true);
    assert(registry.items[0].id == 2);
    assert(student_registry_remove(&registry, 1));
    assert(registry.size == 1);
    student_registry_destroy(&registry);
}

