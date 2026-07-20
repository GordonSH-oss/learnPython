#include <stdio.h>
#include <string.h>

struct Student {
    int id;
    char name[20];
    int age;
    float score;
};

int main()
{
    struct Student stu;
    stu.id = 1001;
    stu.score = 80.5;
    strcpy(stu.name, "Zhang San");
    printf("id = %d, name = %s, age = %d, score = %.2f\n",
           stu.id, stu.name, stu.age, stu.score);
    return 0;
}


