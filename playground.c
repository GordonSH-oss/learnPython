#include <stdbool.h>
#include <stdio.h>

int main(void) {
    int a = 1, b = 2;

    // ① const 在*左边：锁数据
    const int *p1 = &a;
    p1 = &b;    // OK 换指向
    *p1 = 99;   // 报错，数据只读

    // ② const 在*右边：锁指针
    int *const p2 = &a;
    *p2 = 99;   // OK 修改数据
    p2 = &b;    // 报错，指针固定
    return 0;
}