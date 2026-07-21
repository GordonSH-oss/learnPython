/**
 * 15_processes.c - POSIX 进程生命周期示例
 */
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

static int wait_for_child(pid_t pid, const char *label) {
    int status;
    pid_t waited;
    do {
        waited = waitpid(pid, &status, 0);
    } while (waited == -1 && errno == EINTR);

    if (waited == -1) {
        perror("waitpid");
        return -1;
    }
    if (WIFEXITED(status)) {
        printf("[%s] exited with status %d\n", label, WEXITSTATUS(status));
    } else if (WIFSIGNALED(status)) {
        printf("[%s] terminated by signal %d\n", label, WTERMSIG(status));
    }
    return 0;
}

static int demo_fork_wait(void) {
    puts("\n--- fork + waitpid ---");
    if (fflush(NULL) == EOF) {
        perror("fflush");
        return -1;
    }

    pid_t pid = fork();
    if (pid == -1) {
        perror("fork");
        return -1;
    }
    if (pid == 0) {
        dprintf(STDOUT_FILENO, "[child] PID=%ld PPID=%ld\n",
                (long)getpid(), (long)getppid());
        _exit(42);
    }

    printf("[parent] created child PID=%ld\n", (long)pid);
    return wait_for_child(pid, "child");
}

static int demo_fork_exec(void) {
    puts("\n--- fork + execvp ---");
    if (fflush(NULL) == EOF) {
        perror("fflush");
        return -1;
    }

    pid_t pid = fork();
    if (pid == -1) {
        perror("fork");
        return -1;
    }
    if (pid == 0) {
        char *const arguments[] = {
            "echo", "[exec] child process replaced its image", NULL
        };
        execvp(arguments[0], arguments);
        int error = errno;
        dprintf(STDERR_FILENO, "execvp failed: %s\n", strerror(error));
        _exit(127);
    }
    return wait_for_child(pid, "exec child");
}

int main(void) {
    printf("=== POSIX processes ===\nPID=%ld PPID=%ld\n",
           (long)getpid(), (long)getppid());

    if (demo_fork_wait() < 0 || demo_fork_exec() < 0) {
        return EXIT_FAILURE;
    }

    const char *home = getenv("HOME");
    printf("\nHOME=%s\n", home != NULL ? home : "(not set)");
    return EXIT_SUCCESS;
}
