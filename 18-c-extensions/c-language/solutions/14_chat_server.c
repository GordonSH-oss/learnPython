/**
 * 练习 14: fork-per-connection TCP 回显服务器
 */
#define _POSIX_C_SOURCE 200809L

#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <unistd.h>

#define DEFAULT_PORT 8080
#define BUFFER_SIZE 1024
#define BACKLOG 32

static volatile sig_atomic_t stop_requested = 0;
static volatile sig_atomic_t children_changed = 0;

static void handle_stop(int signal_number) {
    (void)signal_number;
    stop_requested = 1;
}

static void handle_child(int signal_number) {
    (void)signal_number;
    children_changed = 1;
}

static int install_handler(int signal_number, void (*handler)(int)) {
    struct sigaction action = {0};
    action.sa_handler = handler;
    sigemptyset(&action.sa_mask);
    return sigaction(signal_number, &action, NULL);
}

static void reap_children(void) {
    int saved_errno = errno;
    while (waitpid(-1, NULL, WNOHANG) > 0) {}
    children_changed = 0;
    errno = saved_errno;
}

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

static void serve_client(int client, const struct sockaddr_in *address) {
    char host[INET_ADDRSTRLEN] = "unknown";
    inet_ntop(AF_INET, &address->sin_addr, host, sizeof host);
    dprintf(STDOUT_FILENO, "client %s:%u connected\n",
            host, (unsigned)ntohs(address->sin_port));

    char buffer[BUFFER_SIZE];
    for (;;) {
        ssize_t count = recv(client, buffer, sizeof buffer, 0);
        if (count > 0) {
            if (send_all(client, buffer, (size_t)count) == -1) break;
        } else if (count == 0) {
            break;
        } else if (errno != EINTR) {
            break;
        }
    }
    close(client);
}

static bool parse_port(const char *text, uint16_t *port) {
    char *end = NULL;
    errno = 0;
    long value = strtol(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0' ||
        value < 1 || value > 65535) {
        return false;
    }
    *port = (uint16_t)value;
    return true;
}

int main(int argc, char **argv) {
    uint16_t port = DEFAULT_PORT;
    if (argc > 2 || (argc == 2 && !parse_port(argv[1], &port))) {
        fprintf(stderr, "usage: %s [1-65535]\n", argv[0]);
        return 2;
    }
    if (install_handler(SIGINT, handle_stop) == -1 ||
        install_handler(SIGTERM, handle_stop) == -1 ||
        install_handler(SIGCHLD, handle_child) == -1) {
        perror("sigaction");
        return EXIT_FAILURE;
    }
    signal(SIGPIPE, SIG_IGN);

    int listener = socket(AF_INET, SOCK_STREAM, 0);
    if (listener == -1) {
        perror("socket");
        return EXIT_FAILURE;
    }
    int enabled = 1;
    if (setsockopt(listener, SOL_SOCKET, SO_REUSEADDR,
                   &enabled, sizeof enabled) == -1) {
        perror("setsockopt");
        close(listener);
        return EXIT_FAILURE;
    }
    struct sockaddr_in server = {
        .sin_family = AF_INET,
        .sin_port = htons(port),
        .sin_addr.s_addr = htonl(INADDR_ANY),
    };
    if (bind(listener, (struct sockaddr *)&server, sizeof server) == -1 ||
        listen(listener, BACKLOG) == -1) {
        perror("bind/listen");
        close(listener);
        return EXIT_FAILURE;
    }
    printf("echo server listening on port %u\n", (unsigned)port);
    fflush(stdout);

    while (!stop_requested) {
        if (children_changed) reap_children();

        struct sockaddr_in client_address;
        socklen_t address_length = sizeof client_address;
        int client = accept(listener, (struct sockaddr *)&client_address,
                            &address_length);
        if (client == -1) {
            if (errno == EINTR) continue;
            perror("accept");
            break;
        }

        pid_t pid = fork();
        if (pid == -1) {
            perror("fork");
            close(client);
        } else if (pid == 0) {
            close(listener);
            serve_client(client, &client_address);
            _exit(0);
        } else {
            close(client);
        }
    }

    close(listener);
    reap_children();
    puts("server stopped accepting new connections");
    return EXIT_SUCCESS;
}
