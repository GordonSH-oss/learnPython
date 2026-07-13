#include <stdio.h>
#include <stdlib.h>

int main(void) {
    size_t count = 5;
    int *squares = malloc(count * sizeof *squares);
    if (squares == NULL) {
        fputs("allocation failed\n", stderr);
        return 1;
    }

    for (size_t i = 0; i < count; i++) squares[i] = (int)(i * i);
    for (size_t i = 0; i < count; i++) printf("%d%c", squares[i], i + 1 == count ? '\n' : ' ');

    free(squares);
    return 0;
}
