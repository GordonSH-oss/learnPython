#include "student_registry.h"
#include "student_store.h"

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void usage(const char *program) {
    fprintf(stderr,
            "usage:\n"
            "  %s FILE add ID NAME SCORE\n"
            "  %s FILE list\n"
            "  %s FILE find ID\n"
            "  %s FILE remove ID\n"
            "  %s FILE stats\n",
            program, program, program, program, program);
}

static bool parse_int(const char *text, int *value) {
    char *end;
    errno = 0;
    long parsed = strtol(text, &end, 10);
    /* 拒绝溢出、空输入、尾随字符和无效学号。 */
    if (errno != 0 || end == text || *end != '\0' || parsed < 1 || parsed > 2147483647L)
        return false;
    *value = (int)parsed;
    return true;
}

static bool parse_score(const char *text, double *score) {
    char *end;
    errno = 0;
    double parsed = strtod(text, &end);
    /* strtod 可以只解析前缀，因此还要用 *end 确认整个字符串都已解析。 */
    if (errno != 0 || end == text || *end != '\0' || parsed < 0 || parsed > 100)
        return false;
    *score = parsed;
    return true;
}

static void print_student(const Student *student) {
    printf("%d\t%-20s\t%.2f\n", student->id, student->name, student->score);
}

int main(int argc, char **argv) {
    /* argv[1] 是数据文件路径，argv[2] 用于选择操作。 */
    if (argc < 3) {
        usage(argv[0]);
        return 2;
    }
    const char *path = argv[1];
    const char *command = argv[2];
    StudentRegistry registry;
    student_registry_init(&registry);

    /* 每条命令都先从磁盘加载当前持久化状态。 */
    if (!student_store_load(path, &registry)) {
        fprintf(stderr, "failed to load %s\n", path);
        student_registry_destroy(&registry);
        return 1;
    }

    int result = 0;
    /* 修改类命令先更新内存，成功后再把完整注册表写回磁盘。 */
    if (strcmp(command, "add") == 0 && argc == 6) {
        int id;
        double score;
        Student student;
        if (!parse_int(argv[3], &id) || !parse_score(argv[5], &score) ||
            !student_create(&student, id, argv[4], score) ||
            !student_registry_add(&registry, student) ||
            !student_store_save(path, &registry)) {
            fputs("failed to add student\n", stderr);
            result = 1;
        }
    } else if (strcmp(command, "list") == 0 && argc == 3) {
        /* 排序只改变本次运行中的显示顺序，list 命令不会保存排序结果。 */
        student_registry_sort_by_score(&registry, true);
        for (size_t index = 0; index < registry.size; ++index)
            print_student(&registry.items[index]);
    } else if (strcmp(command, "find") == 0 && argc == 4) {
        int id;
        const Student *student = NULL;
        if (parse_int(argv[3], &id)) student = student_registry_find_const(&registry, id);
        if (student == NULL) {
            fputs("student not found\n", stderr);
            result = 1;
        } else print_student(student);
    } else if (strcmp(command, "remove") == 0 && argc == 4) {
        int id;
        if (!parse_int(argv[3], &id) || !student_registry_remove(&registry, id) ||
            !student_store_save(path, &registry)) {
            fputs("failed to remove student\n", stderr);
            result = 1;
        }
    } else if (strcmp(command, "stats") == 0 && argc == 3) {
        ScoreStatistics statistics;
        if (!student_registry_statistics(&registry, &statistics)) {
            puts("no students");
        } else {
            printf("count=%zu average=%.2f min=%.2f max=%.2f\n",
                   registry.size, statistics.average,
                   statistics.minimum, statistics.maximum);
        }
    } else {
        usage(argv[0]);
        result = 2;
    }

    /* 所有命令分支最终走到同一处释放注册表内存。 */
    student_registry_destroy(&registry);
    return result;
}
