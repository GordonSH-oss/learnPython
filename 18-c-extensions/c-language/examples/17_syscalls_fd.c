/**
 * 17_syscalls_fd.c - fd、短写循环、重定向和管道
 */
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

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

static ssize_t read_retry(int fd, void *buffer, size_t capacity) {
    ssize_t count;
    do {
        count = read(fd, buffer, capacity);
    } while (count == -1 && errno == EINTR);
    return count;
}

int main(void) {
    const char direct[] = "1) write_all to stdout\n";
    if (write_all(STDOUT_FILENO, direct, sizeof direct - 1) == -1) {
        perror("write stdout");
        return EXIT_FAILURE;
    }

    int source = open("/etc/hosts", O_RDONLY | O_CLOEXEC);
    if (source == -1) {
        perror("open /etc/hosts");
        return EXIT_FAILURE;
    }
    char buffer[81];
    ssize_t count = read_retry(source, buffer, sizeof buffer - 1);
    if (count == -1) {
        perror("read /etc/hosts");
        close(source);
        return EXIT_FAILURE;
    }
    buffer[count] = '\0';
    printf("2) read %zd bytes from fd %d:\n%s\n", count, source, buffer);
    if (close(source) == -1) {
        perror("close source");
        return EXIT_FAILURE;
    }

    if (fflush(stdout) == EOF) {
        perror("fflush");
        return EXIT_FAILURE;
    }
    int saved_stdout = dup(STDOUT_FILENO);
    if (saved_stdout == -1) {
        perror("dup");
        return EXIT_FAILURE;
    }
    int output = open("/tmp/learn-c-redirection.txt",
                      O_WRONLY | O_CREAT | O_TRUNC | O_CLOEXEC, 0644);
    if (output == -1 || dup2(output, STDOUT_FILENO) == -1) {
        perror(output == -1 ? "open output" : "dup2 output");
        if (output != -1) close(output);
        close(saved_stdout);
        return EXIT_FAILURE;
    }
    close(output);
    puts("3) this line is redirected");
    if (fflush(stdout) == EOF || dup2(saved_stdout, STDOUT_FILENO) == -1) {
        perror("restore stdout");
        close(saved_stdout);
        return EXIT_FAILURE;
    }
    close(saved_stdout);
    puts("3) stdout restored");

    int pipe_ends[2];
    if (pipe(pipe_ends) == -1) {
        perror("pipe");
        return EXIT_FAILURE;
    }
    const char pipe_message[] = "message through pipe";
    if (write_all(pipe_ends[1], pipe_message, sizeof pipe_message - 1) == -1 ||
        close(pipe_ends[1]) == -1) {
        perror("pipe write");
        close(pipe_ends[0]);
        return EXIT_FAILURE;
    }
    char pipe_buffer[64];
    count = read_retry(pipe_ends[0], pipe_buffer, sizeof pipe_buffer - 1);
    if (count == -1) {
        perror("pipe read");
        close(pipe_ends[0]);
        return EXIT_FAILURE;
    }
    pipe_buffer[count] = '\0';
    printf("4) pipe returned: %s\n", pipe_buffer);
    if (close(pipe_ends[0]) == -1) {
        perror("close pipe");
        return EXIT_FAILURE;
    }

    printf("5) FILE stdout wraps fd %d\n", fileno(stdout));
    return EXIT_SUCCESS;
}
