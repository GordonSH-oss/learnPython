/**
 * 练习 13: 插件加载器 - 动态加载共享库
 *
 * 学习目标:
 *   - 使用 dlfcn.h 进行动态加载 (dlopen, dlsym, dlclose, dlerror)
 *   - 设计插件接口结构体
 *   - 运行时发现并调用外部函数
 *
 * 编译: clang -std=c17 -Wall -Wextra -Wpedantic -o plugin_loader 13_plugin_loader.c -ldl
 *
 * 示例插件源码 (plugin_double.c):
 * ---------------------------------------------------------------
 *   #include <stddef.h>
 *   const char* plugin_name(void) { return "double"; }
 *   int plugin_execute(int input) { return input * 2; }
 * ---------------------------------------------------------------
 * 编译插件: clang -shared -fPIC -o plugin_double.so plugin_double.c
 *
 * 用法: ./plugin_loader ./plugin_double.so ./plugin_triple.so ...
 */

#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

// TODO: 定义插件结构体 Plugin
// 包含:
//   - void *handle        (dlopen 返回的句柄)
//   - const char* (*name)(void)   (获取插件名称的函数指针)
//   - int (*execute)(int)         (执行插件逻辑的函数指针)

typedef struct {
    // TODO: 填写结构体成员
} Plugin;

// TODO: 实现 load_plugin
// 1. 用 dlopen 打开共享库 (RTLD_LAZY)
// 2. 用 dlsym 查找 "plugin_name" 和 "plugin_execute"
// 3. 任何步骤失败时用 dlerror() 打印错误并返回 NULL
// 4. 成功时分配并返回 Plugin 结构体
Plugin* load_plugin(const char *path) {
    // TODO: 实现此函数
    return NULL;
}

// TODO: 实现 unload_plugin
// 1. dlclose 关闭句柄
// 2. 释放 Plugin 结构体内存
void unload_plugin(Plugin *plugin) {
    // TODO: 实现此函数
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "用法: %s <plugin.so> [plugin2.so ...]\n", argv[0]);
        return EXIT_FAILURE;
    }

    // TODO: 遍历命令行参数 (argv[1] 到 argv[argc-1])
    // 对每个插件路径:
    //   1. 调用 load_plugin 加载
    //   2. 打印插件名称 (调用 plugin->name())
    //   3. 调用 plugin->execute(42) 并打印结果
    //   4. 调用 unload_plugin 卸载

    return EXIT_SUCCESS;
}
