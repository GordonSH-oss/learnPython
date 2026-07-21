# 18 静态库、共享库与动态加载

## 学习目标

完成本章后，你应该能够：

- 区分目标文件、静态库、共享库和运行时插件
- 解释链接时符号解析与运行时库搜索的不同职责
- 在 Linux 和 macOS 上创建并检查共享库
- 使用 rpath、SONAME 或 install name 管理部署关系
- 正确使用 `dlopen`、`dlsym`、`dlerror` 和 `dlclose`
- 设计具有版本和所有权契约的插件 ABI

## 四种构建产物

| 产物 | 常见后缀 | 作用 |
| --- | --- | --- |
| 目标文件 | `.o` | 单个翻译单元生成的机器码与符号 |
| 静态库 | `.a` | 多个目标文件的归档，链接器按需取出成员 |
| 共享库 | `.so`/`.dylib` | 可执行文件记录依赖，动态链接器在装载时解析 |
| 插件 | `.so`/`.dylib` | 程序主动在运行时打开并查询约定符号 |

静态链接不是简单复制整个 `.a`；链接器通常只提取解决当前未定义符号所需的成员。共享库也不是“随便替换就无需重编译”：只有 ABI 保持兼容时才成立。

## 创建静态库

```bash
clang -std=c17 -Wall -Wextra -Wpedantic -c mathutil.c -o mathutil.o
ar rcs libmathutil.a mathutil.o
clang main.o -L. -lmathutil -o main
```

库参数通常放在引用它的目标文件之后，以兼容按从左到右解析的静态链接器。

## 创建共享库

Linux：

```bash
clang -std=c17 -fPIC -shared mathutil.c \
  -Wl,-soname,libmathutil.so.1 -o libmathutil.so.1
```

macOS：

```bash
clang -std=c17 -dynamiclib mathutil.c \
  -Wl,-install_name,@rpath/libmathutil.dylib \
  -o libmathutil.dylib
```

位置无关代码允许库映射到不同虚拟地址。现代平台具体生成方式由工具链决定，不能把 ELF、Mach-O 选项和检查命令混用。

## 链接时依赖与运行时搜索

```bash
clang main.c -L. -lmathutil -o main
```

这一步让链接器验证所需符号并把共享库依赖记录进可执行文件。程序启动时，动态链接器仍需要找到兼容库。

更可部署的方式是记录相对 rpath：

```bash
# Linux：库与程序位于同一目录
clang main.c -L. -lmathutil -Wl,-rpath,'$ORIGIN' -o main

# macOS
clang main.c -L. -lmathutil -Wl,-rpath,@loader_path -o main
```

`LD_LIBRARY_PATH` 和 `DYLD_LIBRARY_PATH` 适合调试，不宜成为唯一部署方案；macOS 的变量还可能受 SIP 和进程启动方式限制。

## ABI、SONAME 与 install name

共享库契约不仅是函数名，还包括：

- 参数和返回类型、调用约定
- 结构体大小、布局与对齐
- 导出符号名称与可见性
- 谁分配、谁释放，以及应使用哪个分配器
- 线程安全和初始化顺序
- 错误码与版本兼容规则

Linux 常用 SONAME 表示兼容 ABI 主版本；macOS 使用 install name 和兼容版本元数据。破坏 ABI 时应发布新主版本，而不是用同名文件静默替换。

## 检查依赖和符号

Linux：

```bash
readelf -d main
ldd main
nm -D --defined-only libmathutil.so
```

macOS：

```bash
otool -L main
otool -l main
nm -gU libmathutil.dylib
```

## `dlopen` 与 `dlsym`

插件宿主不在普通链接阶段绑定插件符号，而是在运行中主动加载：

```c
void *handle = dlopen(path, RTLD_NOW | RTLD_LOCAL);
if (handle == NULL) {
    fprintf(stderr, "dlopen: %s\n", dlerror());
    return 1;
}
```

- `RTLD_NOW` 在打开时解析所需符号，错误更早暴露。
- `RTLD_LOCAL` 避免插件符号默认污染后续全局解析范围。

查询每个符号前清除旧错误，并在查询后立即检查：

```c
typedef int (*add_function)(int, int);

dlerror();
void *symbol = dlsym(handle, "mathlib_add");
const char *error = dlerror();
if (error != NULL) {
    fprintf(stderr, "dlsym: %s\n", error);
    dlclose(handle);
    return 1;
}

add_function add;
memcpy(&add, &symbol, sizeof add);
```

POSIX 为 `dlsym` 与函数指针互操作提供实际接口约定，但 ISO C 不一般性保证对象指针和函数指针可互换。使用 `memcpy` 可以避免直接强制转换触发的严格 C 诊断，并应配合平台文档。

查询多个符号后只调用一次 `dlerror` 会丢失具体失败位置。每个符号都应独立检查。

## 插件 ABI

插件不应只导出一组没有版本的任意函数。一个简单入口可以返回版本化函数表：

```c
typedef struct {
    unsigned abi_version;
    const char *name;
    int (*initialize)(void);
    void (*shutdown)(void);
} PluginApi;

const PluginApi *plugin_get_api(unsigned host_version);
```

宿主先验证 ABI 版本，再保存函数表。`dlclose` 前必须确保：

- 没有线程仍执行插件代码
- 没有回调函数指针仍被保存
- 插件创建的对象已按约定销毁
- 插件的 shutdown 已完成

否则卸载后调用旧函数指针会跳转到已取消映射的代码。

## 符号可见性

```c
#if defined(_WIN32)
#define MATHLIB_EXPORT __declspec(dllexport)
#else
#define MATHLIB_EXPORT __attribute__((visibility("default")))
#endif
```

配合 `-fvisibility=hidden` 默认隐藏内部实现，只导出公共 ABI。这样可以减少符号冲突和意外依赖，但平台导出机制需要分别处理。

## 与 Python FFI 的联系

`ctypes.CDLL` 会加载动态库并查找符号。正确设置 `argtypes` 和 `restype` 是 ABI 契约的一部分；错误签名可能破坏寄存器、栈或返回值解释，而不只是得到错误 Python 值。

动态库中返回的内存通常应由同一库提供的释放函数回收，尤其在不同 C 运行库或分配器边界上。

## 常见错误

- 把静态库理解为总是整库复制
- 假定替换共享库永远不需要重新构建
- 把 Linux 的 `nm -D`、SONAME 和 `.so` 命令直接用于 macOS
- 只靠当前工作目录拼接插件路径
- 多次 `dlsym` 后只检查一次错误
- 卸载插件后继续保存其函数指针或对象
- 公共结构体改变布局却不提升 ABI 版本

## 检查点

1. 普通链接共享库与运行时 `dlopen` 有什么区别？
2. 为什么 API 源码兼容不一定意味着 ABI 兼容？
3. 为什么 `dlclose` 前必须停止插件线程和回调？

## 动手练习

1. 运行 `examples/18_shared_libs.c`，使用 `otool -L` 或 `ldd` 检查依赖。
2. 完成 `exercises/13_plugin_loader.c`，为插件增加 ABI 版本检查。
3. 使用默认隐藏可见性，验证内部函数无法通过 `dlsym` 查询。
4. 故意修改导出结构体布局，解释为什么需要新 ABI 主版本。
