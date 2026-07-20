#include <stdio.h>

int main(void) {
    int value = 42;
    int *p = &value;

    printf("before: value=%d, *p=%d\n", value, *p);
    *p = 100;
    printf("after:  value=%d, *p=%d\n", value, *p);
    return 0;
}