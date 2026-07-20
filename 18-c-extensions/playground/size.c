#include <stdio.h>
int main(void)
{
    printf("char: %zu\n", sizeof(char));
    printf("int: %zu\n", sizeof(int));
    printf("long: %zu\n", sizeof(long));
    printf("指针: %zu\n", sizeof(void*));
    return 0;
}