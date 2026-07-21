/*
 * 练习 06: 指针基础
 * 编译: gcc -Wall -Wextra -g -fsanitize=address 06_pointer_basics.c -o 06_pointer_basics
 * 目标: 理解取地址、解引用、指针与数组的关系
 */
#include <stdio.h>
#include <stdbool.h>

/* ========== 练习 1: 取地址与解引用 ========== */
/* 实现函数: 通过指针交换两个整数的值 */
static void swap(int *a, int *b) {
    /* TODO 1: 实现交换逻辑，画出交换前后的内存示意图 */
}

/* ========== 练习 2: 输出参数模式 ========== */
/* 实现安全除法: 成功返回 true 并通过 result 输出结果，除零返回 false */
static bool safe_divide(int numerator, int denominator, int *result) {
    /* TODO 2: 实现安全除法 */
    return false;
}

/* ========== 练习 3: 指针遍历数组 ========== */
/* 用指针（非下标）遍历数组，返回所有元素之和 */
static int array_sum(const int *arr, int len) {
    /* TODO 3: 使用 past-the-end 指针模式遍历 */
    return 0;
}

/* ========== 练习 4: 查找最大最小值 ========== */
/* 通过输出参数返回数组中的最大值和最小值 */
static void find_min_max(const int *arr, int len, int *out_min, int *out_max) {
    /* TODO 4: 遍历数组，将结果写入 out_min 和 out_max */
}

/* ========== 练习 5: const 方向辨析 ========== */
/* 下面哪些操作是合法的？取消注释并编译验证你的判断 */
static void const_quiz(void) {
    int x = 10, y = 20;
    const int *p1 = &x;
    int *const p2 = &x;
    const int *const p3 = &x;

    /* 逐一取消注释，判断哪些能编译通过: */
    /* *p1 = 100; */
    /* p1 = &y;   */
    /* *p2 = 100; */
    /* p2 = &y;   */
    /* *p3 = 100; */
    /* p3 = &y;   */
    (void)p1; (void)p2; (void)p3; (void)y;
}

int main(void) {
    printf("===== 练习 1: swap =====\n");
    int a = 3, b = 7;
    printf("交换前: a=%d, b=%d\n", a, b);
    swap(&a, &b);
    printf("交换后: a=%d, b=%d (期望: a=7, b=3)\n\n", a, b);

    printf("===== 练习 2: safe_divide =====\n");
    int result;
    if (safe_divide(10, 3, &result))
        printf("10 / 3 = %d (期望: 3)\n", result);
    if (!safe_divide(10, 0, &result))
        printf("10 / 0 = 失败 (期望: 失败)\n\n");

    printf("===== 练习 3: array_sum =====\n");
    int nums[] = {1, 2, 3, 4, 5};
    printf("sum = %d (期望: 15)\n\n", array_sum(nums, 5));

    printf("===== 练习 4: find_min_max =====\n");
    int data[] = {3, -1, 7, 0, 5};
    int mn, mx;
    find_min_max(data, 5, &mn, &mx);
    printf("min=%d, max=%d (期望: min=-1, max=7)\n\n", mn, mx);

    printf("===== 练习 5: const_quiz =====\n");
    const_quiz();
    printf("请逐一取消注释验证编译结果\n");

    return 0;
}
