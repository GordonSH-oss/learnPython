#include <stdbool.h>
#include <stdio.h>

static bool statistics(const int values[], size_t length, int *min, int *max, double *mean) {
    if (values == NULL || length == 0 || min == NULL || max == NULL || mean == NULL) return false;
    long long sum = values[0];
    *min = values[0];
    *max = values[0];
    for (size_t i = 1; i < length; i++) {
        if (values[i] < *min) *min = values[i];
        if (values[i] > *max) *max = values[i];
        sum += values[i];
    }
    *mean = (double)sum / length;
    return true;
}

int main(void) {
    int values[] = {8, 3, 11, -2, 6};
    int min;
    int max;
    double mean;
    if (!statistics(values, sizeof values / sizeof values[0], &min, &max, &mean)) return 1;
    printf("min=%d max=%d mean=%.2f\n", min, max, mean);
    return 0;
}
