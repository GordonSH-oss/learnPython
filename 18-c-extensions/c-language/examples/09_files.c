#include <stdio.h>

int main(void) {
    FILE *file = tmpfile();
    if (file == NULL) {
        perror("tmpfile");
        return 1;
    }
    if (fputs("first line\nsecond line\n", file) == EOF) {
        fputs("failed to write temporary file\n", stderr);
        fclose(file);
        return 1;
    }
    rewind(file);

    char line[64];
    size_t lines = 0;
    while (fgets(line, sizeof line, file) != NULL) lines++;
    printf("lines=%zu\n", lines);
    if (fclose(file) != 0) {
        perror("fclose");
        return 1;
    }
    return 0;
}
