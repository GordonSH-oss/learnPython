#include "calculator.h"
#include <stdio.h>

int main(void) {
    double quotient;
    printf("2 + 3 = %.1f\n", calculator_add(2.0, 3.0));
    if (calculator_divide(10.0, 4.0, &quotient)) printf("10 / 4 = %.1f\n", quotient);
    return 0;
}
