/* 练习 12: 使用 POSIX I/O 复制文件。 */
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define BUFFER_SIZE 16384

static int write_all(int fd, const void *data, size_t length) {
    const unsigned char *cursor = data;
    while (length > 0) {
        ssize_t written = write(fd, cursor, length);
        if (written > 0) {
            cursor += written;
            length -= (size_t)written;
        } else if (written == -1 && errno == EINTR) {
            continue;
        } else {
            return -1;
        }
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "usage: %s <source> <target>\n", argv[0]);
        return 2;
    }

    int source = open(argv[1], O_RDONLY | O_CLOEXEC);
    if (source == -1) {
        perror(argv[1]);
        return EXIT_FAILURE;
    }
    int target = open(argv[2], O_WRONLY | O_CREAT | O_TRUNC | O_CLOEXEC, 0644);
    if (target == -1) {
        perror(argv[2]);
        close(source);
        return EXIT_FAILURE;
    }

    int result = EXIT_SUCCESS;
    uintmax_t total = 0;
    unsigned char buffer[BUFFER_SIZE];
    for (;;) {
        ssize_t count = read(source, buffer, sizeof buffer);
        if (count > 0) {
            if (write_all(target, buffer, (size_t)count) == -1) {
                perror("write");
                result = EXIT_FAILURE;
                break;
            }
            total += (uintmax_t)count;
        } else if (count == 0) {
            break;
        } else if (errno != EINTR) {
            perror("read");
            result = EXIT_FAILURE;
            break;
        }
    }

    if (close(source) == -1) {
        perror("close source");
        result = EXIT_FAILURE;
    }
    if (close(target) == -1) {
        perror("close target");
        result = EXIT_FAILURE;
    }
    if (result == EXIT_SUCCESS) printf("copied %" PRIuMAX " bytes\n", total);
    return result;
}
