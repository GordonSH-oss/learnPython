#include "arithmetic.h"

#include <limits.h>

int add_int32(int32_t left, int32_t right, int32_t *result) {
    if (result == NULL) {
        return -1;
    }
    int64_t wide_result = (int64_t)left + (int64_t)right;
    if (wide_result < INT32_MIN || wide_result > INT32_MAX) {
        return -2;
    }
    *result = (int32_t)wide_result;
    return 0;
}

int sum_squares(int32_t limit, int64_t *result) {
    if (result == NULL || limit < 0) {
        return -1;
    }

    int64_t total = 0;
    for (int64_t value = 1; value <= limit; ++value) {
        int64_t square = value * value;
        if (total > INT64_MAX - square) {
            return -2;
        }
        total += square;
    }
    *result = total;
    return 0;
}

int sum_doubles(const double *values, size_t length, double *result) {
    if (result == NULL || (values == NULL && length != 0)) {
        return -1;
    }

    double total = 0.0;
    for (size_t index = 0; index < length; ++index) {
        total += values[index];
    }
    *result = total;
    return 0;
}

size_t count_byte(const char *data, size_t length, char needle) {
    if (data == NULL) {
        return 0;
    }

    size_t count = 0;
    for (size_t index = 0; index < length; ++index) {
        if (data[index] == needle) {
            ++count;
        }
    }
    return count;
}
