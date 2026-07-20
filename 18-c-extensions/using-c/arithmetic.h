#ifndef ARITHMETIC_H
#define ARITHMETIC_H

#include <stddef.h>
#include <stdint.h>

#if defined(_WIN32)
#define ARITHMETIC_API __declspec(dllexport)
#else
#define ARITHMETIC_API __attribute__((visibility("default")))
#endif

ARITHMETIC_API int add_int32(int32_t left, int32_t right, int32_t *result);
ARITHMETIC_API int sum_squares(int32_t limit, int64_t *result);
ARITHMETIC_API int sum_doubles(const double *values, size_t length,
                               double *result);
ARITHMETIC_API size_t count_byte(const char *data, size_t length, char needle);

#endif
