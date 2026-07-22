#include "student.h"

#include <stdio.h>

bool student_create(Student *student, int id, const char *name, double score) {
    /* 把校验集中在构造函数中，让 CLI 输入和文件加载共用同一套规则。 */
    if (student == NULL || name == NULL || id <= 0 || name[0] == '\0' ||
        score < 0.0 || score > 100.0) {
        return false;
    }

    /* snprintf 在缓冲区有空间时会写入 '\0'；返回值可判断原姓名是否过长。 */
    int written = snprintf(student->name, sizeof student->name, "%s", name);
    if (written < 0 || (size_t)written >= sizeof student->name) return false;

    /* 所有校验成功后再写入其余字段，避免留下半初始化对象。 */
    student->id = id;
    student->score = score;
    return true;
}
