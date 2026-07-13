#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "usage: %s FILE\n", argv[0]);
        return 2;
    }
    FILE *file = fopen(argv[1], "r");
    if (file == NULL) {
        perror(argv[1]);
        return 1;
    }
    size_t lines = 0, words = 0, chars = 0;
    bool in_word = false;
    int ch;
    while ((ch = fgetc(file)) != EOF) {
        chars++;
        if (ch == '\n') lines++;
        if (isspace((unsigned char)ch)) in_word = false;
        else if (!in_word) { words++; in_word = true; }
    }
    if (ferror(file)) {
        fputs("read error\n", stderr);
        fclose(file);
        return 1;
    }
    if (fclose(file) != 0) return 1;
    printf("lines=%zu words=%zu chars=%zu\n", lines, words, chars);
    return 0;
}
