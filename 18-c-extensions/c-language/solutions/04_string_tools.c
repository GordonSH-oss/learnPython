#include <ctype.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    char text[256];
    if (fgets(text, sizeof text, stdin) == NULL) return 1;
    text[strcspn(text, "\n")] = '\0';
    size_t letters = 0, digits = 0, spaces = 0;
    size_t length = strlen(text);
    for (size_t i = 0; i < length; i++) {
        unsigned char ch = (unsigned char)text[i];
        if (isalpha(ch)) letters++;
        if (isdigit(ch)) digits++;
        if (isspace(ch)) spaces++;
    }
    for (size_t left = 0, right = length == 0 ? 0 : length - 1; left < right; left++, right--) {
        char temporary = text[left];
        text[left] = text[right];
        text[right] = temporary;
    }
    printf("letters=%zu digits=%zu spaces=%zu\n%s\n", letters, digits, spaces, text);
    return 0;
}
