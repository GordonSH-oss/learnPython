/*
 * 练习 06: 指针基础 — 参考答案
 * 编译: gcc -Wall -Wextra -g -fsanitize=address 06_pointer_basics.c -o 06_pointer_basics
 */
#include <stdio.h>
#include <stdbool.h>

/* ========== 练习 1: 取地址与解引用 ========== */
static void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

/* ========== 练习 2: 输出参数模式 ========== */
static bool safe_divide(int numerator, int denominator, int *result) {
    if (denominator == 0)
        return false;
    if (result)  /* 防御性检查，虽然本例中调用者总是传有效指针 */
        *result = numerator / denominator;
    return true;
}

/* ========== 练习 3: 指针遍历数组 ========== */
static int array_sum(const int *arr, int len) {
    const int *end = arr + len;  /* past-the-end 指针 */
    int sum = 0;
    for (const int *p = arr; p < end; p++)
        sum += *p;
    return sum;
}

/* ========== 练习 4: 查找最大最小值 ========== */
static void find_min_max(const int *arr, int len, int *out_min, int *out_max) {
    if (len == 0) return;  /* 边界处理 */

    int min = arr[0], max = arr[0];
    for (int i = 1; i < len; i++) {
        if (arr[i] < min) min = arr[i];
        if (arr[i] > max) max = arr[i];
    }

    if (out_min) *out_min = min;
    if (out_max) *out_max = max;
}

/* ========== 练习 5: const 方向辨析 ========== */
static void const_quiz(void) {
    int x = 10, y = 20;
    const int *p1 = &x;      /* 指向 const int 的指针：内容不可变 */
    int *const p2 = &x;      /* const 指针：指针本身不可变 */
    const int *const p3 = &x; /* 两者都不可变 */

    /* 答案解析:
     * *p1 = 100; // ❌ 编译错误：不能通过 p1 修改
     * p1 = &y;   // ✅ 可以重新指向
     * *p2 = 100; // ✅ 可以修改内容
     * p2 = &y;   // ❌ 编译错误：指针本身是 const
     * *p3 = 100; // ❌ 编译错误：内容不可变
     * p3 = &y;   // ❌ 编译错误：指针本身不可变
     */
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
