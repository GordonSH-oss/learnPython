#include <stdio.h>
#include <string.h>

int main(void)
{
    FILE *file = fopen("data.txt", "r");
    if (file == NULL) {
        fprintf(stderr, "Failed to open file\n");
        return 1;
    }
    char buffer[256];
    while (fgets(buffer, sizeof(buffer), file) != NULL) {
        printf("%s", buffer);
    }
    fclose(file);
    return 0;
}