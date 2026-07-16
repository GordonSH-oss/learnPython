/**
 * 练习 13 参考答案: 插件加载器 - 动态加载共享库
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

/* 插件接口结构体: 封装句柄和函数指针 */
typedef struct {
    void *handle;                   /* dlopen 返回的共享库句柄 */
    const char* (*name)(void);      /* 获取插件名称 */
    int (*execute)(int);            /* 执行插件逻辑 */
} Plugin;

/* 加载插件: 打开共享库并解析符号 */
Plugin* load_plugin(const char *path) {
    /* 打开共享库, RTLD_LAZY 表示延迟绑定 */
    void *handle = dlopen(path, RTLD_LAZY);
    if (!handle) {
        fprintf(stderr, "加载失败 [%s]: %s\n", path, dlerror());
        return NULL;
    }

    /* 清除之前的错误状态 */
    dlerror();

    /* 查找 plugin_name 符号 */
    const char* (*name_fn)(void) =
        (const char* (*)(void))dlsym(handle, "plugin_name");
    char *err = dlerror();
    if (err) {
        fprintf(stderr, "符号查找失败 [plugin_name]: %s\n", err);
        dlclose(handle);
        return NULL;
    }

    /* 查找 plugin_execute 符号 */
    int (*exec_fn)(int) = (int (*)(int))dlsym(handle, "plugin_execute");
    err = dlerror();
    if (err) {
        fprintf(stderr, "符号查找失败 [plugin_execute]: %s\n", err);
        dlclose(handle);
        return NULL;
    }

    /* 分配并填充插件结构体 */
    Plugin *plugin = malloc(sizeof(Plugin));
    if (!plugin) {
        fprintf(stderr, "内存分配失败\n");
        dlclose(handle);
        return NULL;
    }
    plugin->handle = handle;
    plugin->name = name_fn;
    plugin->execute = exec_fn;
    return plugin;
}

/* 卸载插件: 关闭共享库并释放内存 */
void unload_plugin(Plugin *plugin) {
    if (!plugin) return;
    if (plugin->handle) {
        dlclose(plugin->handle);
    }
    free(plugin);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "用法: %s <plugin.so> [plugin2.so ...]\n", argv[0]);
        return EXIT_FAILURE;
    }

    /* 遍历所有插件路径 */
    for (int i = 1; i < argc; i++) {
        printf("--- 加载插件: %s ---\n", argv[i]);

        Plugin *plugin = load_plugin(argv[i]);
        if (!plugin) continue;

        /* 调用插件接口 */
        printf("  名称: %s\n", plugin->name());
        int result = plugin->execute(42);
        printf("  execute(42) = %d\n", result);

        unload_plugin(plugin);
        printf("  已卸载\n\n");
    }

    return EXIT_SUCCESS;
}
