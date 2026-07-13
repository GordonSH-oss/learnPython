#include <stdio.h>

int main(void) {
    double celsius;
    if (scanf("%lf", &celsius) != 1) {
        fputs("invalid temperature\n", stderr);
        return 1;
    }
    printf("%.1f\n", celsius * 9.0 / 5.0 + 32.0);
    return 0;
}
