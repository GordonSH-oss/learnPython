#include <stdio.h>
#include <string.h>
#include <stdlib.h>

typedef struct {
    int a;
    int b;
} Entity;
int main(void) {
    Entity *arr = calloc(4, sizeof(Entity));
    arr[0].a = 1;
    arr[0].b = 2;
    printf("%d\n", arr[0].a);
    printf("%d\n", arr[0].b);
    free(arr);
    return 0;
}