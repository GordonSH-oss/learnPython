#include <stdio.h>
void redirect(int **target, int *replacement) {
    if (target != NULL) {
        *target = replacement;
    }
}

int main() {

int first = 10;
int second = 20;
int *selected = &first;
printf("%d\n", *selected); 

redirect(&selected, &second);
printf("%d\n", *selected); // 20
return 0;
}