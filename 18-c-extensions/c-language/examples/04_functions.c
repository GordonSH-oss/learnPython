#include <stdbool.h>
#include <stdio.h>

static bool min_max(const int values[], size_t length, int *minimum, int *maximum) {
    if (values == NULL || length == 0 || minimum == NULL || maximum == NULL) {
        return false;
    }
    *minimum = values[0];
    *maximum = values[0];
    for (size_t i = 1; i < length; i++) {
        if (values[i] < *minimum) *minimum = values[i];
        if (values[i] > *maximum) *maximum = values[i];
    }
    return true;
}

int main(void) {
    int values[] = {7, -2, 11, 4};
    int minimum;
    int maximum;
    if (min_max(values, sizeof values / sizeof values[0], &minimum, &maximum)) {
        printf("min=%d max=%d\n", minimum, maximum);
    }
    return 0;
}
