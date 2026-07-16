# 18 共享库与动态链接

## 学习目标

理解静态库与共享库的创建方式、运行时链接机制，以及通过 dlopen 实现插件式动态加载。

## 静态库 vs 共享库

| 特性 | 静态库 (.a) | 共享库 (.so / .dylib) |
|------|------------|----------------------|
| 链接时机 | 编译时复制进可执行文件 | 运行时由动态链接器加载 |
| 文件体积 | 可执行文件较大 | 可执行文件小，库文件独立 |
| 更新方式 | 必须重新编译 | 替换 .so 即可，无需重编译 |
| 适用场景 | 嵌入式、无外部依赖部署 | 系统库、插件、多进程共享内存 |

## 创建静态库

```bash
# 编译目标文件
clang -c mathutil.c -o mathutil.o

# 打包为静态库 (ar = archiver, rcs = replace/create/index)
ar rcs libmathutil.a mathutil.o

# 使用: -L 指定库搜索路径, -l 指定库名 (去掉 lib 前缀和后缀)
clang main.c -L. -lmathutil -o main
```

## 创建共享库

```bash
# Linux: -fPIC 生成位置无关代码, -shared 生成 .so
clang -fPIC -shared mathutil.c -o libmathutil.so

# macOS: 使用 -dynamiclib 生成 .dylib
clang -fPIC -dynamiclib mathutil.c -o libmathutil.dylib

# 链接共享库
clang main.c -L. -lmathutil -o main
```

`-fPIC` (Position Independent Code) 使代码通过相对地址访问数据，允许库被加载到任意内存地址。

## 运行时链接

编译时链接了共享库，运行时还需让动态链接器找到它：

```bash
# Linux: 设置搜索路径
export LD_LIBRARY_PATH=/path/to/libs:$LD_LIBRARY_PATH
./main

# macOS: 对应环境变量
export DYLD_LIBRARY_PATH=/path/to/libs:$DYLD_LIBRARY_PATH
./main

# 更好的方式: 编译时写入 rpath (运行时搜索路径)
# Linux
clang main.c -L. -lmathutil -Wl,-rpath,'$ORIGIN' -o main
# macOS
clang main.c -L. -lmathutil -Wl,-rpath,@loader_path -o main
```

`rpath` 将搜索路径嵌入二进制文件，部署时无需设置环境变量。

## dlopen / dlsym 动态加载

不在编译时链接，而是运行时按需加载符号，常用于插件系统：

```c
#include <dlfcn.h>
#include <stdio.h>

int main(void) {
    // 打开共享库 (RTLD_LAZY: 延迟解析符号)
    void *handle = dlopen("./libmathutil.so", RTLD_LAZY);
    if (!handle) {
        fprintf(stderr, "dlopen: %s\n", dlerror());
        return 1;
    }

    // 查找符号 (函数指针)
    typedef int (*add_fn)(int, int);
    add_fn add = (add_fn)dlsym(handle, "add");

    char *err = dlerror();
    if (err) {
        fprintf(stderr, "dlsym: %s\n", err);
        dlclose(handle);
        return 1;
    }

    printf("add(2, 3) = %d\n", add(2, 3));
    dlclose(handle);
    return 0;
}
```

```bash
# 编译时链接 dl 库 (Linux 需要 -ldl, macOS 不需要)
clang plugin_host.c -ldl -o plugin_host
```

## 符号可见性

默认情况下共享库导出所有符号。隐藏内部符号可减小体积、加快加载、避免冲突：

```c
// 编译时 -fvisibility=hidden 将所有符号默认隐藏
// 只显式导出需要的接口

#define EXPORT __attribute__((visibility("default")))
#define HIDDEN __attribute__((visibility("hidden")))

EXPORT int public_add(int a, int b) {
    return a + b;
}

HIDDEN int internal_helper(int x) {
    return x * 2;
}
```

```bash
# 编译: 默认隐藏, 仅 EXPORT 标记的符号可见
clang -fPIC -shared -fvisibility=hidden mathutil.c -o libmathutil.so

# 查看导出符号
nm -D libmathutil.so | grep ' T '
```

## 与 Python ctypes 的联系

Python 的 `ctypes.CDLL` 本质就是对 `dlopen` 的封装：

```python
import ctypes

# 等价于 C 的 dlopen("./libmathutil.so", RTLD_LAZY)
lib = ctypes.CDLL("./libmathutil.so")

# 等价于 dlsym(handle, "add")
lib.add.argtypes = [ctypes.c_int, ctypes.c_int]
lib.add.restype = ctypes.c_int

print(lib.add(2, 3))  # 5
```

理解了共享库的创建和符号导出机制，就理解了 ctypes/cffi 等 FFI 工具的底层原理。

## 动手练习

1. 将一个简单的数学模块分别编译为 `.a` 和 `.so`，对比最终可执行文件大小
2. 编写一个插件宿主程序：用 dlopen 加载目录下所有 `.so` 文件，调用每个插件的 `plugin_init()` 函数
3. 使用 `-fvisibility=hidden` 编译共享库，验证未标记 EXPORT 的函数无法被 dlsym 找到
