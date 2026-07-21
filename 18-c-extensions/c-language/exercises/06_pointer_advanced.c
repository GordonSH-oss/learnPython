/*
 * 练习 06b: 指针进阶 — 结构体指针、void*、二级指针
 * 编译: gcc -Wall -Wextra -g -fsanitize=address 06_pointer_advanced.c -o 06_pointer_advanced
 * 目标: 掌握结构体指针操作、通用指针、以及二级指针修改调用者变量
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

/* 通过指针修改学生信息 */
static void student_set(Student *s, const char *name, int age, float score) {
    /* TODO 1: 使用 -> 运算符设置字段 */
}

/* 打印学生信息（const 指针，不允许修改） */
static void student_print(const Student *s) {
    /* TODO 2: 用 -> 读取并打印 */
}

/* ========== 练习 2: void* 通用交换 ========== */
/* 实现一个可以交换任意类型的函数，利用 void* 和 size */
static void generic_swap(void *a, void *b, size_t size) {
    /* TODO 3: 用 memcpy + 临时缓冲区实现 */
}

/* ========== 练习 3: 二级指针 — 修改调用者的指针 ========== */
/* 在函数内部分配内存，让调用者的指针指向新内存 */
static int create_array(int **out, int len) {
    /* TODO 4: malloc 一个 int 数组，填入 0..len-1，
     * 将地址写入 *out，成功返回 0，失败返回 -1 */
    return -1;
}

/* ========== 练习 4: 指针数组与字符串排序 ========== */
/* 对字符串指针数组按字典序排序（只交换指针，不移动字符串本身） */
static void sort_strings(const char *arr[], int len) {
    /* TODO 5: 冒泡排序，用 strcmp 比较，交换指针 */
}

/* ========== 练习 5: 回调函数指针 ========== */
typedef int (*compare_fn)(const void *, const void *);

static int int_ascending(const void *a, const void *b) {
    /* TODO 6: 实现升序比较 */
    return 0;
}

static int int_descending(const void *a, const void *b) {
    /* TODO 7: 实现降序比较 */
    return 0;
}

/* 使用函数指针进行排序 */
static void sort_ints(int *arr, int len, compare_fn cmp) {
    /* TODO 8: 冒泡排序，用 cmp 函数指针决定顺序 */
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
        printf("create_array 未实现或失败\n");
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
