#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct { const char *name; int score; } Student;

static int compare_score(const void *left, const void *right) {
    const Student *a = left;
    const Student *b = right;
    return (b->score > a->score) - (b->score < a->score);
}

static const Student *find_student(const Student students[], size_t count, const char *name) {
    for (size_t i = 0; i < count; i++) if (strcmp(students[i].name, name) == 0) return &students[i];
    return NULL;
}

int main(void) {
    Student students[] = {{"Ada", 93}, {"Linus", 88}, {"Grace", 97}};
    size_t count = sizeof students / sizeof students[0];
    qsort(students, count, sizeof students[0], compare_score);
    for (size_t i = 0; i < count; i++) printf("%s %d\n", students[i].name, students[i].score);
    const Student *found = find_student(students, count, "Ada");
    if (found != NULL) printf("found=%s\n", found->name);
    return 0;
}
