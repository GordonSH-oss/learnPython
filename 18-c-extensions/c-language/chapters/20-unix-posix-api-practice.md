# 20 Unix/POSIX API 实战

## 学习目标

本章面向 Apple Silicon Mac，使用系统自带的 Clang 和终端练习 Unix/POSIX API。学完后，你应能：

- 区分 ISO C、POSIX、Unix 系统调用和平台专用 API。
- 使用手册确认函数签名、头文件、返回值和错误语义。
- 查询进程与系统信息，遍历目录并读取文件元数据。
- 正确处理 `errno`、资源生命周期、路径和部分成功。
- 使用 `sigaction` 处理信号，理解信号处理器的限制。
- 在 macOS 上观察系统调用，并识别常见 Linux/macOS API 差异。

第 15、17、19 章分别介绍进程、文件描述符和 Socket。本章把已有知识组合成实际工作流，重点训练“查文档、调用 API、检查失败、释放资源、观察系统行为”。

## 先理解 API 层次

实际 C 程序会同时使用几个层次的接口：

```text
你的 C 程序
    |
    +-- ISO C 标准库：printf、malloc、fopen
    |
    +-- POSIX API：opendir、lstat、fork、read、sigaction
    |
    +-- macOS/BSD API：kqueue、sysctl、Mach API
    |
    +-- Darwin 内核
```

POSIX 是接口标准，不是一个操作系统。macOS 是经过 Unix 认证的系统，底层 Darwin 结合了 BSD 用户空间和 XNU 内核。Linux 也实现了大量 POSIX 接口，但两者还各有专用功能。

“系统调用”和“POSIX 函数”也不是严格同义词。例如 `read` 通常很接近内核系统调用，而 `opendir` 是库函数，它在内部使用更底层的目录读取能力。编程时最重要的是遵守公开 API 契约，不要依赖某个版本内部恰好调用了什么。

### M1 对本章意味着什么

M1 使用 ARM64/AArch64 指令集，macOS 工具通常把架构显示为 `arm64`。POSIX C 源代码一般不需要因 Intel 或 Apple Silicon 改写，但应注意：

- 不要假设指针和 `long` 固定为某个大小，应使用 `sizeof` 和合适的类型。
- 不要假设主机字节序；网络代码继续使用 `htons`、`ntohl` 等转换。
- 预编译的第三方库必须包含 `arm64` 架构。
- Linux 的 ARM64 二进制不能直接在 macOS 运行，因为操作系统 ABI 不同。

检查本机架构和编译器：

```bash
uname -s
uname -m
arch
clang --version
file /bin/ls
```

在 Apple Silicon Mac 上，`uname -m` 通常输出 `arm64`。`file` 可能显示系统程序是同时包含 `x86_64` 和 `arm64` 的 universal binary。

## 学会查询手册

Unix API 的第一手说明位于 manual pages。不要只记函数名，要确认它属于哪一节：

```bash
man 2 open       # 系统调用
man 2 lstat
man 3 opendir    # C 库函数
man 3 sysconf
man 2 sigaction
man 5 passwd     # 文件格式
```

macOS 的手册分节可能与 Linux 不完全一致。如果指定章节没有结果，使用 `man -a 名称` 查看所有同名页面，或使用：

```bash
apropos "directory stream"
man -k "process ID"
```

阅读一个 API 时，依次找出：

1. 需要包含哪个头文件。
2. 成功时返回什么。
3. 失败时返回什么，是否设置 `errno`。
4. 返回的资源由谁关闭或释放。
5. 输入指针、缓冲区和字符串必须保持多久有效。
6. 是否存在 macOS 版本差异或线程安全限制。

## 案例：系统信息与目录检查工具

配套案例位于 `examples/20_unix_api.c`。它组合使用：

| API | 作用 | 资源或错误规则 |
| --- | --- | --- |
| `uname` | 查询系统名、版本和机器架构 | 失败返回 `-1` |
| `sysconf` | 查询在线 CPU 数和页大小 | 具体选项的错误规则应查手册 |
| `getpid`、`getuid` | 查询当前进程身份 | 返回当前进程属性 |
| `getcwd` | 查询工作目录 | `getcwd(NULL, 0)` 返回的内存要 `free` |
| `opendir` | 打开目录流 | 返回的 `DIR *` 要 `closedir` |
| `readdir` | 逐项读取目录 | 结束和错误都返回 `NULL`，需结合 `errno` |
| `lstat` | 读取目录项自身的元数据 | 不跟随最后一个符号链接 |
| `readlink` | 读取符号链接目标 | 不自动添加字符串结尾的 `\0` |

案例在包含系统头文件前定义 `_DARWIN_C_SOURCE`，以公开 Darwin 提供的完整接口集合。`sysconf` 是 POSIX API，但 `_SC_NPROCESSORS_ONLN` 这个查询名称不是所有严格 POSIX 环境都提供；移植到其他 Unix 时应检查目标平台手册或改用其系统信息接口。

编译并检查课程目录：

```bash
make examples
./build/examples/20_unix_api .
./build/examples/20_unix_api /tmp
```

也可以单独编译：

```bash
clang -std=c17 -Wall -Wextra -Wpedantic \
  examples/20_unix_api.c -o /tmp/20_unix_api
/tmp/20_unix_api chapters
```

预期输出结构如下，具体系统版本、PID 和目录内容以本机为准：

```text
System:  Darwin ...
Machine: arm64
CPUs:    ... online
Page:    16384 bytes
PID:     ...
UID/GID: ...
CWD:     .../18-c-extensions/c-language

Directory: chapters
type       mode           bytes  name
file       rw-r--r--       ...  01-build-and-program.md
...
```

Apple Silicon Mac 的内存页通常是 16 KiB，但程序必须查询 `_SC_PAGESIZE`，不能把 `16384` 写死。

## 执行路径与资源生命周期

案例的执行顺序是：

```text
main
 |
 +-- print_system_info
 |    +-- uname / sysconf / getpid / getuid
 |    +-- getcwd(NULL, 0)
 |    +-- free
 |
 +-- inspect_directory
      +-- opendir
      +-- readdir 循环
      |    +-- 拼接完整路径
      |    +-- lstat
      |    +-- 必要时 readlink
      +-- closedir
```

这里存在两种由调用者管理的资源：

- `getcwd(NULL, 0)` 分配的内存由 `free` 释放。
- `opendir` 创建的目录流由 `closedir` 关闭。

如果中途失败，也必须沿错误路径清理已经获得的资源。这个原则同样适用于 `FILE *`、文件描述符、Socket、线程和动态库句柄。

## 正确遍历目录

`opendir` 返回不透明的 `DIR *`。`readdir` 返回的 `struct dirent *` 指向目录流内部管理的数据，后续调用可能覆盖它，因此需要长期保存名称时应复制 `d_name`。

```c
DIR *directory = opendir(path);
if (directory == NULL) {
    perror("opendir");
    return -1;
}

errno = 0;
struct dirent *entry;
while ((entry = readdir(directory)) != NULL) {
    printf("%s\n", entry->d_name);
    errno = 0;
}

int read_error = errno;
closedir(directory);
if (read_error != 0) {
    errno = read_error;
    perror("readdir");
}
```

为什么需要单独处理 `errno`？因为 `readdir` 用 `NULL` 同时表示“已经读完”和“发生错误”。调用前清零，返回 `NULL` 后再检查，才能区分两种状态。

目录项中的 `d_type` 并非在所有文件系统上都可靠可用，它可能是 `DT_UNKNOWN`。案例使用完整路径调用 `lstat`，以真实元数据判断类型。

## `stat`、`lstat` 与符号链接

`stat` 会跟随符号链接并返回目标对象的信息，`lstat` 返回符号链接本身的信息：

```text
link.txt  --符号链接-->  target.txt

lstat("link.txt")    得到 link.txt 的类型和大小
stat("link.txt")     得到 target.txt 的类型和大小
```

在 `/tmp` 创建安全的实验环境：

```bash
mkdir -p /tmp/posix-lab
printf 'hello\n' > /tmp/posix-lab/target.txt
ln -s target.txt /tmp/posix-lab/link.txt
chmod 640 /tmp/posix-lab/target.txt
./build/examples/20_unix_api /tmp/posix-lab
ls -la /tmp/posix-lab
```

检查两份输出是否都显示 `target.txt` 权限为 `rw-r-----`，并确认案例把 `link.txt` 显示为 `link` 而不是普通文件。

权限位属于 `st_mode`，应使用 `S_IRUSR`、`S_IWUSR` 等掩码检查，不要根据 `ls` 输出字符串反推。创建文件时请求的模式还会受到进程 `umask` 限制：

```text
最终权限 = 请求权限 & ~umask
```

在 shell 中运行 `umask` 查看当前值。不要在练习中对系统目录递归执行 `chmod`。

## 路径不是简单字符串

案例使用 `PATH_MAX` 大小的栈缓冲区帮助聚焦 API，但生产代码不能假设所有路径都适合固定缓冲区。路径处理还应考虑：

- 相对路径依据进程当前工作目录解释，而不是源文件所在目录。
- 文件名可能包含空格、换行和非 ASCII 字节。
- 检查后再使用路径可能存在 TOCTOU 竞态：对象可能在两次操作间被替换。
- 权限失败、文件消失和符号链接循环都是正常运行时情况。

安全敏感代码通常尽量使用 `openat`、`fstatat` 等基于目录文件描述符的接口，减少工作目录变化和路径替换带来的问题。

## 错误处理：返回值与 `errno`

POSIX API 通常使用特殊返回值表示失败，并设置线程局部的 `errno`：

```c
if (lstat(path, &info) < 0) {
    int error = errno;
    fprintf(stderr, "cannot inspect %s: %s\n",
            path, strerror(error));
}
```

规则如下：

- 只在 API 明确报告失败后读取 `errno`。
- 需要跨越其他函数调用保存错误时，立即复制 `errno`。
- `perror("lstat")` 会把上下文和当前错误文本写到标准错误。
- 不要假定一次 `read` 或 `write` 会处理完整缓冲区。
- `EINTR` 表示调用被信号中断；是否重试要根据 API 和业务语义判断。

用不存在和无权限的路径练习失败分支：

```bash
./build/examples/20_unix_api /path/that/does/not/exist
./build/examples/20_unix_api /var/root
echo $?
```

第二条命令是否失败取决于当前系统权限。重点观察错误写到 stderr，程序退出状态为非零。

## 信号：使用 `sigaction`

信号是异步事件通知。相比语义较弱的 `signal`，POSIX 程序应优先使用 `sigaction`：

```c
#define _POSIX_C_SOURCE 200809L

#include <signal.h>
#include <stdio.h>
#include <unistd.h>

static volatile sig_atomic_t stop_requested = 0;

static void handle_signal(int signal_number) {
    (void)signal_number;
    stop_requested = 1;
}

int main(void) {
    struct sigaction action = {0};
    action.sa_handler = handle_signal;
    sigemptyset(&action.sa_mask);

    if (sigaction(SIGINT, &action, NULL) < 0) {
        perror("sigaction");
        return 1;
    }

    puts("Press Ctrl-C to stop");
    while (!stop_requested) {
        pause();
    }
    puts("stopped cleanly");
    return 0;
}
```

信号处理器可能打断程序的任意位置，因此只能调用 async-signal-safe 函数。`printf`、`malloc` 和大部分库函数都不安全。示例中的处理器只写入 `volatile sig_atomic_t` 标志，正常控制流负责输出和清理。

将示例保存到 `/tmp/signal_demo.c` 后编译运行，在另一个终端也可以发送信号：

```bash
clang -std=c17 -Wall -Wextra -Wpedantic \
  /tmp/signal_demo.c -o /tmp/signal_demo
/tmp/signal_demo
```

另一个终端执行：

```bash
pgrep -fl signal_demo
kill -INT PID
```

把 `PID` 替换为实际进程号。不要练习 `kill -9`：`SIGKILL` 无法捕获，程序没有机会清理资源。

## 在 macOS 上观察 API 调用

先从无需提权的工具开始：

```bash
time ./build/examples/20_unix_api chapters
```

`time` 可以比较用户态、内核态和总耗时。观察文件活动可以使用：

```bash
sudo fs_usage -w -f filesystem 20_unix_api
```

在另一个终端运行案例，然后按 Ctrl-C 停止 `fs_usage`。追踪系统调用可使用：

```bash
sudo dtruss ./build/examples/20_unix_api chapters
```

`dtruss` 和 `fs_usage` 需要管理员权限，并可能受 System Integrity Protection 限制。它们不是完成其他练习的必要条件；如果被系统拒绝，跳过即可，不要关闭 SIP。

调试文件描述符泄漏时，可以让程序暂停，然后在另一个终端检查：

```bash
lsof -p PID
```

## Linux 与 macOS 常见差异

优先使用共同的 POSIX 接口，再把平台专用能力封装在小范围条件编译中：

| 需求 | Linux | macOS |
| --- | --- | --- |
| 高扩展性事件通知 | `epoll` | `kqueue` |
| 文件事件 | `inotify` | FSEvents 或 `kqueue` |
| 系统调用跟踪 | `strace` | `dtruss`、Instruments |
| 文件活动观察 | `inotifywait`、`strace` | `fs_usage` |
| 进程伪文件系统 | `/proc` | `sysctl`、`libproc` |
| 动态库扩展名 | `.so` | `.dylib` |
| 动态链接环境变量 | `LD_LIBRARY_PATH` | `DYLD_LIBRARY_PATH`（受 SIP 限制） |

条件编译示例：

```c
#if defined(__APPLE__)
    /* kqueue 实现 */
#elif defined(__linux__)
    /* epoll 实现 */
#else
#error "unsupported platform"
#endif
```

不要仅根据 CPU 架构判断操作系统。`__aarch64__` 可能同时出现在 Linux ARM64 和其他系统；平台分支应检查 `__APPLE__` 或 `__linux__`。

## 实验：用 `kqueue` 观察目录变化

macOS 的 `kqueue` 能监视文件描述符事件。完成下面的实验骨架：

```c
#include <fcntl.h>
#include <stdio.h>
#include <sys/event.h>
#include <unistd.h>

int main(void) {
    int directory_fd = open("/tmp/posix-lab", O_RDONLY);
    if (directory_fd < 0) {
        perror("open");
        return 1;
    }

    int queue = kqueue();
    if (queue < 0) {
        perror("kqueue");
        close(directory_fd);
        return 1;
    }

    struct kevent change;
    EV_SET(&change, directory_fd, EVFILT_VNODE,
           EV_ADD | EV_CLEAR,
           NOTE_WRITE | NOTE_DELETE | NOTE_RENAME,
           0, NULL);

    if (kevent(queue, &change, 1, NULL, 0, NULL) < 0) {
        perror("kevent register");
        close(queue);
        close(directory_fd);
        return 1;
    }

    puts("waiting for a directory change...");
    struct kevent event;
    if (kevent(queue, NULL, 0, &event, 1, NULL) > 0) {
        printf("event flags: 0x%x\n", event.fflags);
    }

    close(queue);
    close(directory_fd);
    return 0;
}
```

在终端 A 运行监听程序，在终端 B 执行：

```bash
touch /tmp/posix-lab/new-file.txt
```

监听程序应解除阻塞并打印事件标志。`kqueue` 通知“目录发生变化”，不会直接给出新增文件名；收到事件后通常需要重新扫描目录并比较状态。

## 综合练习

1. 给 `20_unix_api.c` 增加 `-a` 选项：默认跳过以 `.` 开头的名称，指定 `-a` 后显示。验收时与 `ls -A` 比较条目集合。
2. 增加 `-L` 选项，在 `lstat` 和 `stat` 之间切换。使用 `/tmp/posix-lab/link.txt` 验证类型变化。
3. 增加按文件类型统计的汇总行。即使某个条目的 `lstat` 失败，也继续处理其余条目并让程序最终返回非零。
4. 把固定 `PATH_MAX` 缓冲区替换为按需分配，验证每条成功路径和失败路径都释放内存。
5. 完成 `kqueue` 实验，识别 `NOTE_WRITE`、`NOTE_RENAME` 和 `NOTE_DELETE`。思考被监视目录本身删除后如何重新建立监听。
6. 阅读 `man 2 open`，使用 `openat` 和目录 fd 重写元数据查询，说明它怎样减少对当前工作目录的依赖。

## 完成检查

完成本章后，应能不看答案解释以下问题：

- 为什么 `readdir` 返回 `NULL` 不一定表示错误？
- 为什么目录遍历中使用 `lstat`，而不是只读取 `d_type`？
- 为什么 `readlink` 后需要手动补 `\0`？
- 为什么信号处理器不能直接调用 `printf`？
- 为什么 Linux ARM64 程序不能因为 M1 也是 ARM64 就直接运行？
- 每次成功的 `opendir`、`open` 和 `getcwd(NULL, 0)` 分别需要什么清理操作？

能够回答这些问题，说明你已经开始从“会调用函数”进入“理解 Unix API 契约和资源生命周期”的阶段。
