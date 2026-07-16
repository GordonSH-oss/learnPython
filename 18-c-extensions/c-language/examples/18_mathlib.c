// 共享库示例 - 数学运算库
// 编译: gcc -shared -fPIC -o libmathlib.so 18_mathlib.c -lm (Linux)
//       gcc -shared -fPIC -o libmathlib.dylib 18_mathlib.c -lm (macOS)

#include <math.h>

// 加法
int mathlib_add(int a, int b) {
    return a + b;
}

// 乘法
int mathlib_multiply(int a, int b) {
    return a * b;
}

// 幂运算
double mathlib_power(double base, double exp) {
    return pow(base, exp);
}
