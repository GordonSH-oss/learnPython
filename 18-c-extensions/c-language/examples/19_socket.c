/**
 * 19_socket.c - 使用内核分配端口的本地 TCP echo 示例
 */
#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#define BUFFER_SIZE 256

static int send_all(int fd, const void *data, size_t length) {
    const unsigned char *cursor = data;
    while (length > 0) {
#if defined(__APPLE__)
        ssize_t sent = send(fd, cursor, length, 0);
#else
        ssize_t sent = send(fd, cursor, length, MSG_NOSIGNAL);
#endif
        if (sent > 0) {
            cursor += sent;
            length -= (size_t)sent;
        } else if (sent == -1 && errno == EINTR) {
            continue;
        } else {
            return -1;
        }
    }
    return 0;
}

static ssize_t receive_retry(int fd, void *buffer, size_t capacity) {
    ssize_t count;
    do {
        count = recv(fd, buffer, capacity, 0);
    } while (count == -1 && errno == EINTR);
    return count;
}

static int create_listener(uint16_t *port) {
    int listener = socket(AF_INET, SOCK_STREAM, 0);
    if (listener == -1) return -1;

    int enabled = 1;
    if (setsockopt(listener, SOL_SOCKET, SO_REUSEADDR,
                   &enabled, sizeof enabled) == -1) {
        close(listener);
        return -1;
    }
#if defined(__APPLE__)
    if (setsockopt(listener, SOL_SOCKET, SO_NOSIGPIPE,
                   &enabled, sizeof enabled) == -1) {
        close(listener);
        return -1;
    }
#endif

    struct sockaddr_in address = {
        .sin_family = AF_INET,
        .sin_port = htons(0),
        .sin_addr.s_addr = htonl(INADDR_LOOPBACK),
    };
    if (bind(listener, (struct sockaddr *)&address, sizeof address) == -1 ||
        listen(listener, 1) == -1) {
        close(listener);
        return -1;
    }

    socklen_t length = sizeof address;
    if (getsockname(listener, (struct sockaddr *)&address, &length) == -1) {
        close(listener);
        return -1;
    }
    *port = ntohs(address.sin_port);
    return listener;
}

static int run_server(int listener) {
    int connection;
    do {
        connection = accept(listener, NULL, NULL);
    } while (connection == -1 && errno == EINTR);
    if (connection == -1) return -1;

    char buffer[BUFFER_SIZE];
    ssize_t count = receive_retry(connection, buffer, sizeof buffer);
    int result = 0;
    if (count == -1 || (count > 0 &&
        send_all(connection, buffer, (size_t)count) == -1)) {
        result = -1;
    }
    if (close(connection) == -1) result = -1;
    return result;
}

static int run_client(uint16_t port) {
    int connection = socket(AF_INET, SOCK_STREAM, 0);
    if (connection == -1) return -1;
#if defined(__APPLE__)
    int enabled = 1;
    if (setsockopt(connection, SOL_SOCKET, SO_NOSIGPIPE,
                   &enabled, sizeof enabled) == -1) {
        close(connection);
        return -1;
    }
#endif

    struct sockaddr_in address = {
        .sin_family = AF_INET,
        .sin_port = htons(port),
        .sin_addr.s_addr = htonl(INADDR_LOOPBACK),
    };
    if (connect(connection, (struct sockaddr *)&address, sizeof address) == -1) {
        close(connection);
        return -1;
    }

    const char message[] = "Hello, TCP stream!";
    if (send_all(connection, message, sizeof message - 1) == -1) {
        close(connection);
        return -1;
    }

    char response[BUFFER_SIZE];
    ssize_t count = receive_retry(connection, response, sizeof response - 1);
    if (count <= 0) {
        close(connection);
        return -1;
    }
    response[count] = '\0';
    printf("echo response: %s\n", response);
    return close(connection);
}

int main(void) {
    signal(SIGPIPE, SIG_IGN);

    uint16_t port;
    int listener = create_listener(&port);
    if (listener == -1) {
        perror("create listener");
        return EXIT_FAILURE;
    }
    printf("listening on 127.0.0.1:%u\n", (unsigned)port);
    if (fflush(stdout) == EOF) {
        perror("fflush");
        close(listener);
        return EXIT_FAILURE;
    }

    pid_t pid = fork();
    if (pid == -1) {
        perror("fork");
        close(listener);
        return EXIT_FAILURE;
    }
    if (pid == 0) {
        int result = run_server(listener);
        close(listener);
        _exit(result == 0 ? 0 : 1);
    }

    close(listener);
    int client_result = run_client(port);
    if (client_result == -1) perror("client");

    int status;
    pid_t waited;
    do {
        waited = waitpid(pid, &status, 0);
    } while (waited == -1 && errno == EINTR);
    if (waited == -1) {
        perror("waitpid");
        return EXIT_FAILURE;
    }
    if (client_result == -1 || !WIFEXITED(status) || WEXITSTATUS(status) != 0) {
        fputs("TCP echo failed\n", stderr);
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
