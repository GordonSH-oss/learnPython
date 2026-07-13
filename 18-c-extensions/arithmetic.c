/*
 * arithmetic.c — 供 Python ctypes 调用的共享库
 *
 * 编译方法：
 *   macOS:  gcc -shared -o libarithmetic.dylib arithmetic.c
 *   Linux:  gcc -shared -fPIC -o libarithmetic.so arithmetic.c
 */

#include <math.h>

/* 基本四则运算 */
int add(int a, int b) {
    return a + b;
}

double divide(double a, double b) {
    if (b == 0.0) return INFINITY;
    return a / b;
}

/* 计算密集型示例：求 1 到 n 的平方和 */
long long sum_of_squares(int n) {
    long long result = 0;
    for (int i = 1; i <= n; i++) {
        result += (long long)i * i;
    }
    return result;
}

/* 数组求和（演示指针传递）*/
double array_sum(double *arr, int length) {
    double sum = 0.0;
    for (int i = 0; i < length; i++) {
        sum += arr[i];
    }
    return sum;
}

/* 字符串操作：统计字符出现次数 */
int count_char(const char *s, char c) {
    int count = 0;
    while (*s) {
        if (*s == c) count++;
        s++;
    }
    return count;
}
