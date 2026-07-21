/**
 * 练习 13: 带 ABI 版本检查的插件加载器
 * 插件应导出：
 *   unsigned plugin_abi_version(void);  // 返回 1
 *   const char *plugin_name(void);
 *   int plugin_execute(int input);
 */
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>

#define HOST_ABI_VERSION 1u

typedef struct {
    void *handle;
    const char *(*name)(void);
    int (*execute)(int);
} Plugin;

static void *required_symbol(void *handle, const char *name) {
    dlerror();
    void *symbol = dlsym(handle, name);
    const char *error = dlerror();
    if (error != NULL) {
        fprintf(stderr, "dlsym %s: %s\n", name, error);
        return NULL;
    }
    return symbol;
}

static Plugin *load_plugin(const char *path) {
    void *handle = dlopen(path, RTLD_NOW | RTLD_LOCAL);
    if (handle == NULL) {
        fprintf(stderr, "dlopen %s: %s\n", path, dlerror());
        return NULL;
    }

    unsigned (*abi_version)(void) =
        (unsigned (*)(void))required_symbol(handle, "plugin_abi_version");
    const char *(*name)(void) =
        (const char *(*)(void))required_symbol(handle, "plugin_name");
    int (*execute)(int) =
        (int (*)(int))required_symbol(handle, "plugin_execute");
    if (abi_version == NULL || name == NULL || execute == NULL) {
        dlclose(handle);
        return NULL;
    }
    if (abi_version() != HOST_ABI_VERSION) {
        fprintf(stderr, "%s: incompatible plugin ABI %u (expected %u)\n",
                path, abi_version(), HOST_ABI_VERSION);
        dlclose(handle);
        return NULL;
    }

    Plugin *plugin = malloc(sizeof *plugin);
    if (plugin == NULL) {
        dlclose(handle);
        return NULL;
    }
    plugin->handle = handle;
    plugin->name = name;
    plugin->execute = execute;
    return plugin;
}

static int unload_plugin(Plugin *plugin) {
    if (plugin == NULL) return 0;
    int result = dlclose(plugin->handle);
    if (result != 0) fprintf(stderr, "dlclose: %s\n", dlerror());
    free(plugin);
    return result;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s <plugin> [plugin ...]\n", argv[0]);
        return 2;
    }

    int result = EXIT_SUCCESS;
    for (int i = 1; i < argc; ++i) {
        Plugin *plugin = load_plugin(argv[i]);
        if (plugin == NULL) {
            result = EXIT_FAILURE;
            continue;
        }
        printf("%s: execute(42) = %d\n", plugin->name(), plugin->execute(42));
        if (unload_plugin(plugin) != 0) result = EXIT_FAILURE;
    }
    return result;
}
