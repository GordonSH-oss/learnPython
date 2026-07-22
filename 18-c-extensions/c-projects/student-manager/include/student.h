#ifndef STUDENT_MANAGER_STUDENT_H
#define STUDENT_MANAGER_STUDENT_H

#include <stdbool.h>

/* 包含字符串结尾的 '\0'，因此最长可存储 63 字节的姓名。 */
#define STUDENT_NAME_CAPACITY 64

/* Student 自己持有定长姓名数组，不需要单独分配和释放姓名内存。 */
typedef struct {
    int id;
    char name[STUDENT_NAME_CAPACITY];
    double score;
} Student;

/* 校验并初始化 *student；任一输入无效时返回 false。 */
bool student_create(Student *student, int id, const char *name, double score);

#endif
