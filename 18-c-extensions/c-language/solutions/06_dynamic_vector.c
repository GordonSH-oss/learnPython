#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct { int *data; size_t length; size_t capacity; } Vector;

static bool vector_push(Vector *vector, int value) {
    if (vector == NULL) return false;
    if (vector->length == vector->capacity) {
        size_t capacity = vector->capacity == 0 ? 4 : vector->capacity * 2;
        int *data = realloc(vector->data, capacity * sizeof *data);
        if (data == NULL) return false;
        vector->data = data;
        vector->capacity = capacity;
    }
    vector->data[vector->length++] = value;
    return true;
}

int main(void) {
    Vector vector = {0};
    for (int i = 0; i < 10; i++) {
        if (!vector_push(&vector, i * i)) {
            free(vector.data);
            return 1;
        }
    }
    for (size_t i = 0; i < vector.length; i++) printf("%d%c", vector.data[i], i + 1 == vector.length ? '\n' : ' ');
    free(vector.data);
    return 0;
}
