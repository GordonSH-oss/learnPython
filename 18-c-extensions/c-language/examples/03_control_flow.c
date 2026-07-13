#include <stdio.h>

int main(void) {
    int sum = 0;
    for (int value = 1; value <= 10; value++) {
        if (value % 2 == 0) {
            sum += value;
        }
    }

    printf("sum of even values from 1 through 10: %d\n", sum);
    return 0;
}
