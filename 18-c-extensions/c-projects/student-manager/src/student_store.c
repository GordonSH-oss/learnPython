#include "student_store.h"

#include <errno.h>
#include <stdio.h>

bool student_store_load(const char *path, StudentRegistry *registry) {
    if (path == NULL || registry == NULL) return false;
    FILE *file = fopen(path, "r");
    /* 第一次执行 add 时允许数据文件尚不存在。 */
    if (file == NULL) return errno == ENOENT;

    bool success = true;
    char line[256];
    while (fgets(line, sizeof line, file) != NULL) {
        int id;
        char name[STUDENT_NAME_CAPACITY];
        double score;
        char extra;
        /* %63[^\t] 限制姓名长度，末尾的 %c 用于发现多余内容。 */
        if (sscanf(line, "%d\t%63[^\t]\t%lf %c", &id, name, &score, &extra) != 3) {
            success = false;
            break;
        }
        Student student;
        /* 文件数据也必须经过实体校验和学号唯一性检查。 */
        if (!student_create(&student, id, name, score) ||
            !student_registry_add(registry, student)) {
            success = false;
            break;
        }
    }
    /* 到达 EOF 是正常情况；ferror 用于区分 EOF 和真正的读取错误。 */
    if (ferror(file)) success = false;
    /* 关闭文件也可能报告 I/O 错误，因此需要检查返回值。 */
    if (fclose(file) != 0) success = false;
    return success;
}

bool student_store_save(const char *path, const StudentRegistry *registry) {
    if (path == NULL || registry == NULL) return false;
    FILE *file = fopen(path, "w");
    if (file == NULL) return false;
    bool success = true;
    /* 使用 "w" 打开会用注册表当前状态覆盖原文件。 */
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
