/**
 * 20_unix_api.c - Unix/POSIX 系统信息与目录检查工具
 * 编译: clang -std=c17 -Wall -Wextra -Wpedantic 20_unix_api.c -o 20_unix_api
 * 用法: ./20_unix_api [目录]
 */
#define _DARWIN_C_SOURCE

#include <dirent.h>
#include <errno.h>
#include <inttypes.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/utsname.h>
#include <unistd.h>

static const char *file_type(mode_t mode) {
    if (S_ISREG(mode)) return "file";
    if (S_ISDIR(mode)) return "dir";
    if (S_ISLNK(mode)) return "link";
    if (S_ISCHR(mode)) return "char";
    if (S_ISBLK(mode)) return "block";
    if (S_ISFIFO(mode)) return "fifo";
    if (S_ISSOCK(mode)) return "socket";
    return "other";
}

static void format_permissions(mode_t mode, char output[10]) {
    static const mode_t masks[] = {
        S_IRUSR, S_IWUSR, S_IXUSR,
        S_IRGRP, S_IWGRP, S_IXGRP,
        S_IROTH, S_IWOTH, S_IXOTH,
    };
    static const char symbols[] = "rwxrwxrwx";

    for (size_t i = 0; i < 9; ++i) {
        output[i] = (mode & masks[i]) ? symbols[i] : '-';
    }
    output[9] = '\0';
}

static int join_path(char *output, size_t capacity,
                     const char *directory, const char *name) {
    int written = snprintf(output, capacity, "%s/%s", directory, name);
    if (written < 0 || (size_t)written >= capacity) {
        errno = ENAMETOOLONG;
        return -1;
    }
    return 0;
}

static int inspect_directory(const char *path) {
    DIR *directory = opendir(path);
    if (directory == NULL) {
        perror("opendir");
        return -1;
    }

    printf("\nDirectory: %s\n", path);
    printf("%-10s %-9s %10s  %s\n", "type", "mode", "bytes", "name");

    errno = 0;
    struct dirent *entry;
    while ((entry = readdir(directory)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 ||
            strcmp(entry->d_name, "..") == 0) {
            continue;
        }

        char full_path[PATH_MAX];
        if (join_path(full_path, sizeof full_path, path, entry->d_name) < 0) {
            perror("path");
            continue;
        }

        struct stat info;
        if (lstat(full_path, &info) < 0) {
            perror(full_path);
            continue;
        }

        char permissions[10];
        format_permissions(info.st_mode, permissions);
        printf("%-10s %-9s %10" PRIdMAX "  %s",
               file_type(info.st_mode), permissions,
               (intmax_t)info.st_size, entry->d_name);

        if (S_ISLNK(info.st_mode)) {
            char target[PATH_MAX];
            ssize_t length = readlink(full_path, target, sizeof target - 1);
            if (length >= 0) {
                target[length] = '\0';
                printf(" -> %s", target);
            }
        }
        putchar('\n');
        errno = 0;
    }

    int read_error = errno;
    if (closedir(directory) < 0) {
        perror("closedir");
        return -1;
    }
    if (read_error != 0) {
        errno = read_error;
        perror("readdir");
        return -1;
    }
    return 0;
}

static int print_system_info(void) {
    struct utsname system_info;
    if (uname(&system_info) < 0) {
        perror("uname");
        return -1;
    }

    long cpu_count = sysconf(_SC_NPROCESSORS_ONLN);
    long page_size = sysconf(_SC_PAGESIZE);
    if (cpu_count < 0 || page_size < 0) {
        perror("sysconf");
        return -1;
    }

    char *working_directory = getcwd(NULL, 0);
    if (working_directory == NULL) {
        perror("getcwd");
        return -1;
    }

    printf("System:  %s %s\n", system_info.sysname, system_info.release);
    printf("Machine: %s\n", system_info.machine);
    printf("CPUs:    %ld online\n", cpu_count);
    printf("Page:    %ld bytes\n", page_size);
    printf("PID:     %ld (parent %ld)\n", (long)getpid(), (long)getppid());
    printf("UID/GID: %lu/%lu\n",
           (unsigned long)getuid(), (unsigned long)getgid());
    printf("CWD:     %s\n", working_directory);

    free(working_directory);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc > 2) {
        fprintf(stderr, "usage: %s [directory]\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *path = argc == 2 ? argv[1] : ".";
    if (print_system_info() < 0 || inspect_directory(path) < 0) {
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
