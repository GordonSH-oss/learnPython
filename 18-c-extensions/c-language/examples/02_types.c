#include <stdbool.h>
#include <stdio.h>

int main(void) {
    int items = 5;
    double price = 12.50;
    double total = items * price;
    bool discounted = total >= 50.0;

    printf("integer division: 5 / 2 = %d\n", 5 / 2);
    printf("floating division: 5 / 2 = %.1f\n", (double)5 / 2);
    printf("total: %.2f, discounted: %s\n", total, discounted ? "yes" : "no");
    return 0;
}
