/**
 * 18_shared_libs.c - 使用 dlopen/dlsym 加载同目录共享库
 */
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef int (*binary_int_function)(int, int);
typedef double (*power_function)(double, double);

static char *library_path_next_to_executable(const char *program) {
#if defined(__APPLE__)
    const char library_name[] = "libmathlib.dylib";
#else
    const char library_name[] = "libmathlib.so";
#endif
    const char *slash = strrchr(program, '/');
    size_t directory_length = slash == NULL ? 1 : (size_t)(slash - program);
    const char *directory = slash == NULL ? "." : program;
    size_t needed = directory_length + 1 + sizeof library_name;
    char *path = malloc(needed);
    if (path == NULL) return NULL;

    snprintf(path, needed, "%.*s/%s",
             (int)directory_length, directory, library_name);
    return path;
}

static void *find_symbol(void *handle, const char *name) {
    dlerror();
    void *symbol = dlsym(handle, name);
    const char *error = dlerror();
    if (error != NULL) {
        fprintf(stderr, "dlsym %s: %s\n", name, error);
        return NULL;
    }
    return symbol;
}

int main(int argc, char **argv) {
    if (argc > 2) {
        fprintf(stderr, "usage: %s [library-path]\n", argv[0]);
        return EXIT_FAILURE;
    }

    char *derived_path = NULL;
    const char *library_path = argc == 2 ? argv[1] :
        (derived_path = library_path_next_to_executable(argv[0]));
    if (library_path == NULL) {
        fputs("failed to build library path\n", stderr);
        return EXIT_FAILURE;
    }

    void *handle = dlopen(library_path, RTLD_NOW | RTLD_LOCAL);
    if (handle == NULL) {
        fprintf(stderr, "dlopen %s: %s\n", library_path, dlerror());
        free(derived_path);
        return EXIT_FAILURE;
    }
    printf("loaded: %s\n", library_path);

    binary_int_function add =
        (binary_int_function)find_symbol(handle, "mathlib_add");
    binary_int_function multiply =
        (binary_int_function)find_symbol(handle, "mathlib_multiply");
    power_function power =
        (power_function)find_symbol(handle, "mathlib_power");
    if (add == NULL || multiply == NULL || power == NULL) {
        dlclose(handle);
        free(derived_path);
        return EXIT_FAILURE;
    }

    printf("add(3, 5) = %d\n", add(3, 5));
    printf("multiply(4, 7) = %d\n", multiply(4, 7));
    printf("power(2, 10) = %.0f\n", power(2.0, 10.0));

    if (dlclose(handle) != 0) {
        fprintf(stderr, "dlclose: %s\n", dlerror());
        free(derived_path);
        return EXIT_FAILURE;
    }
    free(derived_path);
    return EXIT_SUCCESS;
}
