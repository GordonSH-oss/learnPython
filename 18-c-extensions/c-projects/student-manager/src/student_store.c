#include "student_store.h"

#include <errno.h>
#include <stdio.h>

bool student_store_load(const char *path, StudentRegistry *registry) {
    if (path == NULL || registry == NULL) return false;
    FILE *file = fopen(path, "r");
    if (file == NULL) return errno == ENOENT;

    bool success = true;
    char line[256];
    while (fgets(line, sizeof line, file) != NULL) {
        int id;
        char name[STUDENT_NAME_CAPACITY];
        double score;
        char extra;
        if (sscanf(line, "%d\t%63[^\t]\t%lf %c", &id, name, &score, &extra) != 3) {
            success = false;
            break;
        }
        Student student;
        if (!student_create(&student, id, name, score) ||
            !student_registry_add(registry, student)) {
            success = false;
            break;
        }
    }
    if (ferror(file)) success = false;
    if (fclose(file) != 0) success = false;
    return success;
}

bool student_store_save(const char *path, const StudentRegistry *registry) {
    if (path == NULL || registry == NULL) return false;
    FILE *file = fopen(path, "w");
    if (file == NULL) return false;
    bool success = true;
    for (size_t index = 0; index < registry->size; ++index) {
        const Student *student = &registry->items[index];
        if (fprintf(file, "%d\t%s\t%.2f\n", student->id,
                    student->name, student->score) < 0) {
            success = false;
            break;
        }
    }
    if (fclose(file) != 0) success = false;
    return success;
}

