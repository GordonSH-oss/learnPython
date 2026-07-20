#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
int main()
{
    int a[5] = {10, 20, 30, 40, 50};
    for (int i = 0; i < 5; i++) {
        printf("a[%d]的值：%d\n", i, a[i]);
    }
    return 0;
}


