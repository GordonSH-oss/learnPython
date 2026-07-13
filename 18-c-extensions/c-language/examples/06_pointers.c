#include <stdbool.h>
#include <stdio.h>

static bool swap(int *left, int *right) {
    if (left == NULL || right == NULL) return false;
    int temporary = *left;
    *left = *right;
    *right = temporary;
    return true;
}

int main(void) {
    int first = 10;
    int second = 20;
    printf("before: %d %d\n", first, second);
    swap(&first, &second);
    printf("after:  %d %d\n", first, second);
    return 0;
}
