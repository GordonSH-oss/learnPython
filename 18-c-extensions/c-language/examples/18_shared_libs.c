// 动态加载共享库示例 - 使用 dlopen/dlsym
// 编译共享库: gcc -shared -fPIC -o libmathlib.dylib 18_mathlib.c -lm
// 编译主程序: gcc -o 18_shared_libs 18_shared_libs.c (macOS 无需 -ldl)
//            gcc -o 18_shared_libs 18_shared_libs.c -ldl (Linux 需要 -ldl)

#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

// 定义函数指针类型
typedef int (*add_func)(int, int);
typedef int (*mul_func)(int, int);
typedef double (*pow_func)(double, double);

int main(void) {
    // 1. 打开共享库
#ifdef __APPLE__
    const char *lib_path = "./libmathlib.dylib";
#else
    const char *lib_path = "./libmathlib.so";
#endif

    void *handle = dlopen(lib_path, RTLD_LAZY);
    if (!handle) {
        fprintf(stderr, "加载失败: %s\n", dlerror());
        return EXIT_FAILURE;
    }
    printf("共享库加载成功: %s\n", lib_path);

    // 2. 查找符号 (清除之前的错误)
    dlerror();

    add_func my_add = (add_func)dlsym(handle, "mathlib_add");
    mul_func my_mul = (mul_func)dlsym(handle, "mathlib_multiply");
    pow_func my_pow = (pow_func)dlsym(handle, "mathlib_power");

    // 检查错误
    char *error = dlerror();
    if (error) {
        fprintf(stderr, "符号查找失败: %s\n", error);
        dlclose(handle);
        return EXIT_FAILURE;
    }

    // 3. 通过函数指针调用
    printf("add(3, 5)      = %d\n", my_add(3, 5));
    printf("multiply(4, 7) = %d\n", my_mul(4, 7));
    printf("power(2, 10)   = %.0f\n", my_pow(2.0, 10.0));

    // 4. 关闭共享库
    dlclose(handle);
    printf("共享库已卸载\n");

    return EXIT_SUCCESS;
}
