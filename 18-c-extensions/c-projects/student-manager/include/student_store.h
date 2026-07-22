#ifndef STUDENT_MANAGER_STORE_H
#define STUDENT_MANAGER_STORE_H

#include "student_registry.h"

#include <stdbool.h>

/*
 * 使用制表符分隔文本加载和保存注册表：学号<TAB>姓名<TAB>成绩。
 * 输入文件不存在时视为空数据集，而不是错误。
 */
bool student_store_load(const char *path, StudentRegistry *registry);
bool student_store_save(const char *path, const StudentRegistry *registry);

#endif
