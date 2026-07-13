#include <stdio.h>
#include <string.h>

int main(void) {
    int scores[] = {90, 85, 78, 96};
    size_t count = sizeof scores / sizeof scores[0];
    int total = 0;
    for (size_t i = 0; i < count; i++) total += scores[i];

    char language[16] = "C language";
    printf("average=%.2f\n", (double)total / count);
    printf("%s has %zu characters\n", language, strlen(language));
    return 0;
}
