#include <stdio.h>

int main(void){
int value = 260;
int *p = &value;
// *p 是 int* 解引用，编译器知道从该地址读4个字节，拼成整数42

char *pc = (char *)&value;
// *pc 只会读取起始的1个字节，只能拿到value内存第一个8位二进制
printf("%d\n", *pc);
printf("%d\n", *p);
printf("%c\n", *pc);
return 0;
}
