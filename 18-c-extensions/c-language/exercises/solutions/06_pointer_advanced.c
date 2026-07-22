/*
 * 练习 06b: 指针进阶 — 参考答案
 * 编译: gcc -Wall -Wextra -g -fsanitize=address 06_pointer_advanced.c -o 06_pointer_advanced
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ========== 练习 1: 结构体指针与 -> 运算符 ========== */
typedef struct {
    char name[32];
    int age;
    float score;
} Student;

static void student_set(Student *s, const char *name, int age, float score) {
    strncpy(s->name, name, sizeof(s->name) - 1);
    s->name[sizeof(s->name) - 1] = '\0';  /* 保证 null 终止 */
    s->age = age;
    s->score = score;
}

static void student_print(const Student *s) {
    printf("Student: %s, age=%d, score=%.1f\n", s->name, s->age, s->score);
}

/* ========== 练习 2: void* 通用交换 ========== */
static void generic_swap(void *a, void *b, size_t size) {
    unsigned char *pa = (unsigned char *)a;
    unsigned char *pb = (unsigned char *)b;
    unsigned char temp;

    for (size_t i = 0; i < size; i++) {
        temp = pa[i];
        pa[i] = pb[i];
        pb[i] = temp;
    }
}

/* ========== 练习 3: 二级指针 — 修改调用者的指针 ========== */
static int create_array(int **out, int len) {
    if (!out || len <= 0) return -1;

    int *arr = malloc(sizeof(int) * (size_t)len);
    if (!arr) return -1;

    for (int i = 0; i < len; i++)
        arr[i] = i;

    *out = arr;  /* 将新分配的地址写入调用者的指针变量 */
    return 0;
}

/* ========== 练习 4: 指针数组与字符串排序 ========== */
static void sort_strings(const char *arr[], int len) {
    for (int i = 0; i < len - 1; i++) {
        for (int j = i + 1; j < len; j++) {
            if (strcmp(arr[i], arr[j]) > 0) {
                const char *temp = arr[i];
                arr[i] = arr[j];
                arr[j] = temp;
            }
        }
    }
}

/* ========== 练习 5: 回调函数指针 ========== */
typedef int (*compare_fn)(const void *, const void *);

static int int_ascending(const void *a, const void *b) {
    return *(const int *)a - *(const int *)b;
}

static int int_descending(const void *a, const void *b) {
    return *(const int *)b - *(const int *)a;
}

static void sort_ints(int *arr, int len, compare_fn cmp) {
    for (int i = 0; i < len - 1; i++) {
        for (int j = i + 1; j < len; j++) {
            if (cmp(&arr[i], &arr[j]) > 0) {
                int temp = arr[i];
                arr[i] = arr[j];
                arr[j] = temp;
            }
        }
    }
}

int main(void) {
    printf("===== 练习 1-2: 结构体指针 =====\n");
    Student s;
    student_set(&s, "Alice", 20, 95.5f);
    student_print(&s);

    printf("\n===== 练习 2: generic_swap =====\n");
    int x = 42, y = 99;
    generic_swap(&x, &y, sizeof(int));
    printf("int swap: x=%d, y=%d (期望: 99, 42)\n", x, y);
    double d1 = 3.14, d2 = 2.71;
    generic_swap(&d1, &d2, sizeof(double));
    printf("double swap: d1=%.2f, d2=%.2f (期望: 2.71, 3.14)\n", d1, d2);

    printf("\n===== 练习 3: 二级指针 =====\n");
    int *arr = NULL;
    if (create_array(&arr, 5) == 0) {
        for (int i = 0; i < 5; i++)
            printf("%d ", arr[i]);
        printf("(期望: 0 1 2 3 4)\n");
        free(arr);
    } else {
        printf("create_array 失败\n");
    }

    printf("\n===== 练习 4: 字符串指针排序 =====\n");
    const char *words[] = {"banana", "apple", "cherry", "date"};
    sort_strings(words, 4);
    for (int i = 0; i < 4; i++) printf("%s ", words[i]);
    printf("(期望: apple banana cherry date)\n");

    printf("\n===== 练习 5: 函数指针排序 =====\n");
    int nums[] = {5, 2, 8, 1, 9};
    sort_ints(nums, 5, int_ascending);
    printf("升序: ");
    for (int i = 0; i < 5; i++) printf("%d ", nums[i]);
    printf("(期望: 1 2 5 8 9)\n");
    sort_ints(nums, 5, int_descending);
    printf("降序: ");
    for (int i = 0; i < 5; i++) printf("%d ", nums[i]);
    printf("(期望: 9 8 5 2 1)\n");

    return 0;
}
