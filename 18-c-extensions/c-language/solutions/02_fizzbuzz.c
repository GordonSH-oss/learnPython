#include <stdio.h>

int main(void) {
    for (int value = 1; value <= 100; value++) {
        if (value % 15 == 0) puts("FizzBuzz");
        else if (value % 3 == 0) puts("Fizz");
        else if (value % 5 == 0) puts("Buzz");
        else printf("%d\n", value);
    }
    return 0;
}
