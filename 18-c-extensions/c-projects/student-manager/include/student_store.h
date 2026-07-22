#ifndef STUDENT_MANAGER_STORE_H
#define STUDENT_MANAGER_STORE_H

#include "student_registry.h"

#include <stdbool.h>

bool student_store_load(const char *path, StudentRegistry *registry);
bool student_store_save(const char *path, const StudentRegistry *registry);

#endif

