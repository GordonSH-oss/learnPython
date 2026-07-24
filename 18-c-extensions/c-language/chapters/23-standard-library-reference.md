# 23 标准库速查：ISO C 与 POSIX

## 本章目的

C 程序可以使用的函数和类型来自两套标准：ISO C（语言标准自带）和 POSIX（操作系统接口标准）。初学者经常分不清哪些是"C 本身的"、哪些是"Unix/Linux/macOS 提供的"。本章按功能分类列出两套标准的头文件，帮助你建立全景印象。不需要记住每个函数，需要时查阅即可。

## 如何区分

| 属性 | ISO C 标准库 | POSIX |
| --- | --- | --- |
| 定义者 | ISO/IEC 9899（C17） | IEEE Std 1003.1（The Open Group） |
| 可移植性 | 所有符合标准的 C 编译器 | Unix/Linux/macOS/BSD，Windows 需要兼容层 |
| 头文件前缀 | `<stdio.h>`, `<stdlib.h>` 等 | 通常有 `<unistd.h>`, `<sys/*.h>`, `<pthread.h>` 等 |
| 编译标志 | 默认可用 | 可能需要 `-D_POSIX_C_SOURCE=200809L` |
| 典型场景 | 跨平台基础功能 | 系统编程、进程、线程、网络、文件系统 |

判断依据：如果 `man 函数名` 在 SYNOPSIS 中只包含 `<std*.h>` 或 `<math.h>` 等 C 标准头文件，它通常是 ISO C 的；如果出现 `<unistd.h>`、`<sys/...>` 或要求 `_POSIX_C_SOURCE`，则是 POSIX 的。

---

## 第一部分：ISO C 标准库（C17）

C17 标准定义了 29 个头文件。以下按功能分组。

### 输入输出

| 头文件 | 核心内容 | 常用函数/宏 |
| --- | --- | --- |
| `<stdio.h>` | 流式 I/O | `printf`, `scanf`, `fopen`, `fclose`, `fgets`, `fread`, `fwrite`, `snprintf`, `fprintf` |

### 通用工具

| 头文件 | 核心内容 | 常用函数/宏 |
| --- | --- | --- |
| `<stdlib.h>` | 内存分配、进程控制、转换 | `malloc`, `free`, `realloc`, `calloc`, `exit`, `atoi`, `strtol`, `strtod`, `qsort`, `bsearch`, `abs`, `rand` |
| `<string.h>` | 字节和字符串操作 | `memcpy`, `memmove`, `memset`, `memcmp`, `strlen`, `strcpy`, `strcat`, `strcmp`, `strchr`, `strstr`, `strtok` |
| `<math.h>` | 数学运算（需链接 `-lm`） | `sin`, `cos`, `sqrt`, `pow`, `log`, `exp`, `fabs`, `ceil`, `floor`, `fmod`, `isnan`, `isinf` |
| `<ctype.h>` | 字符分类与转换 | `isalpha`, `isdigit`, `isspace`, `isupper`, `islower`, `toupper`, `tolower`, `isalnum` |
| `<errno.h>` | 错误号 | `errno`, `EDOM`, `ERANGE`, `EILSEQ` |
| `<assert.h>` | 断言 | `assert(expr)`, 定义 `NDEBUG` 可禁用 |

### 类型与限制

| 头文件 | 核心内容 | 常用定义 |
| --- | --- | --- |
| `<stdint.h>` | 固定宽度整数 | `int8_t`, `int16_t`, `int32_t`, `int64_t`, `uint8_t`, `uint32_t`, `SIZE_MAX`, `INT64_MAX` |
| `<stddef.h>` | 基本类型定义 | `size_t`, `ptrdiff_t`, `NULL`, `offsetof` |
| `<limits.h>` | 整数类型范围 | `INT_MAX`, `INT_MIN`, `UINT_MAX`, `CHAR_BIT`, `LONG_MAX` |
| `<float.h>` | 浮点特性 | `FLT_MAX`, `DBL_MAX`, `FLT_EPSILON`, `DBL_DIG` |
| `<stdbool.h>` | 布尔类型 | `bool`, `true`, `false`（C23 起内置，不再需要此头文件） |
| `<inttypes.h>` | 固定宽度整数的格式化宏 | `PRId64`, `PRIu32`, `SCNd64`（配合 `printf`/`scanf`） |

### 可变参数与信号

| 头文件 | 核心内容 | 常用函数/宏 |
| --- | --- | --- |
| `<stdarg.h>` | 可变参数 | `va_list`, `va_start`, `va_arg`, `va_end`, `va_copy` |
| `<signal.h>` | 信号处理 | `signal`, `raise`, `SIGINT`, `SIGTERM`, `SIGSEGV`, `SIG_IGN`, `SIG_DFL` |
| `<setjmp.h>` | 非局部跳转 | `setjmp`, `longjmp`, `jmp_buf` |

### 时间与本地化

| 头文件 | 核心内容 | 常用函数/宏 |
| --- | --- | --- |
| `<time.h>` | 日历和处理器时间 | `time`, `clock`, `difftime`, `mktime`, `strftime`, `localtime`, `gmtime`, `timespec_get`（C11） |
| `<locale.h>` | 本地化设置 | `setlocale`, `localeconv`, `LC_ALL`, `LC_NUMERIC` |
| `<wchar.h>` | 宽字符操作 | `wprintf`, `wcslen`, `wcscpy`, `mbrtowc`, `wcrtomb`, `fwprintf` |
| `<wctype.h>` | 宽字符分类 | `iswalpha`, `iswdigit`, `towupper` |

### 并发与原子（C11 新增）

| 头文件 | 核心内容 | 常用函数/宏 |
| --- | --- | --- |
| `<threads.h>` | C11 线程 | `thrd_create`, `thrd_join`, `mtx_lock`, `mtx_unlock`, `cnd_wait`（实际项目多用 POSIX `pthread`） |
| `<stdatomic.h>` | 原子操作 | `atomic_int`, `atomic_load`, `atomic_store`, `atomic_fetch_add`, `memory_order_*` |

### 其他

| 头文件 | 核心内容 | 常用函数/宏 |
| --- | --- | --- |
| `<stdalign.h>` | 对齐 | `alignof`, `alignas`（C23 起为关键字） |
| `<stdnoreturn.h>` | 不返回标记 | `noreturn`（C23 起为 `[[noreturn]]`） |
| `<tgmath.h>` | 类型泛型数学宏 | 根据参数类型自动选择 `sinf`/`sin`/`sinl` |
| `<fenv.h>` | 浮点环境 | `fesetround`, `fegetexcept`, `FE_TONEAREST` |
| `<complex.h>` | 复数 | `cabs`, `creal`, `cimag`, `_Complex` |
| `<uchar.h>` | Unicode 字符（C11） | `char16_t`, `char32_t`, `mbrtoc16`, `c32rtomb` |

### ISO C 标准库小结

```text
总计 29 个头文件（C17），涵盖：
- I/O、字符串、数学、内存分配等基础功能
- 类型定义与跨平台整数
- 并发原语（C11 起，但实际不如 POSIX pthread 普及）
- 不涉及：文件系统遍历、网络、进程管理、用户权限
```

---

## 第二部分：POSIX 标准（IEEE 1003.1-2017）

POSIX 在 ISO C 基础上扩展，定义了操作系统级接口。以下列出最常用的部分。

### 进程与信号

| 头文件 | 核心内容 | 常用函数 |
| --- | --- | --- |
| `<unistd.h>` | 系统调用入口 | `fork`, `exec*`, `pipe`, `dup2`, `close`, `read`, `write`, `lseek`, `getcwd`, `chdir`, `getpid`, `sleep`, `access` |
| `<sys/wait.h>` | 进程等待 | `wait`, `waitpid`, `WIFEXITED`, `WEXITSTATUS`, `WIFSIGNALED` |
| `<sys/types.h>` | 系统类型定义 | `pid_t`, `uid_t`, `gid_t`, `off_t`, `ssize_t` |
| `<signal.h>`（POSIX 扩展） | 可靠信号 | `sigaction`, `sigprocmask`, `sigpending`, `sigsuspend`, `kill`, `sigset_t` |
| `<spawn.h>` | 进程创建（替代 fork+exec） | `posix_spawn`, `posix_spawnattr_*` |

### 线程（pthread）

| 头文件 | 核心内容 | 常用函数 |
| --- | --- | --- |
| `<pthread.h>` | 线程与同步 | `pthread_create`, `pthread_join`, `pthread_detach`, `pthread_mutex_*`, `pthread_cond_*`, `pthread_rwlock_*`, `pthread_key_*` |
| `<semaphore.h>` | 信号量 | `sem_init`, `sem_wait`, `sem_post`, `sem_destroy` |

### 文件系统与 I/O

| 头文件 | 核心内容 | 常用函数 |
| --- | --- | --- |
| `<fcntl.h>` | 文件控制 | `open`, `creat`, `fcntl`, `O_RDONLY`, `O_WRONLY`, `O_CREAT`, `O_TRUNC`, `O_APPEND` |
| `<sys/stat.h>` | 文件状态 | `stat`, `fstat`, `lstat`, `mkdir`, `chmod`, `S_ISREG`, `S_ISDIR` |
| `<dirent.h>` | 目录遍历 | `opendir`, `readdir`, `closedir`, `struct dirent` |
| `<sys/mman.h>` | 内存映射 | `mmap`, `munmap`, `mprotect`, `msync`, `MAP_SHARED`, `MAP_PRIVATE` |
| `<poll.h>` | I/O 多路复用 | `poll`, `struct pollfd`, `POLLIN`, `POLLOUT` |
| `<sys/select.h>` | I/O 多路复用（旧） | `select`, `FD_SET`, `FD_CLR`, `FD_ISSET`, `FD_ZERO` |

### 网络（Socket）

| 头文件 | 核心内容 | 常用函数/宏 |
| --- | --- | --- |
| `<sys/socket.h>` | Socket 核心 | `socket`, `bind`, `listen`, `accept`, `connect`, `send`, `recv`, `shutdown` |
| `<netinet/in.h>` | IPv4/IPv6 地址 | `struct sockaddr_in`, `struct sockaddr_in6`, `INADDR_ANY`, `htons`, `ntohs` |
| `<arpa/inet.h>` | 地址转换 | `inet_pton`, `inet_ntop`, `inet_addr` |
| `<netdb.h>` | 主机/服务查询 | `getaddrinfo`, `freeaddrinfo`, `gai_strerror`, `getnameinfo` |

### 时间（POSIX 扩展）

| 头文件 | 核心内容 | 常用函数 |
| --- | --- | --- |
| `<sys/time.h>` | 高精度时间 | `gettimeofday`, `struct timeval` |
| `<time.h>`（POSIX 扩展） | 时钟与定时器 | `clock_gettime`, `clock_nanosleep`, `CLOCK_REALTIME`, `CLOCK_MONOTONIC`, `nanosleep` |

### 动态链接

| 头文件 | 核心内容 | 常用函数 |
| --- | --- | --- |
| `<dlfcn.h>` | 动态加载 | `dlopen`, `dlsym`, `dlclose`, `dlerror`, `RTLD_LAZY`, `RTLD_NOW` |

### 用户与权限

| 头文件 | 核心内容 | 常用函数 |
| --- | --- | --- |
| `<pwd.h>` | 用户信息 | `getpwnam`, `getpwuid`, `struct passwd` |
| `<grp.h>` | 组信息 | `getgrnam`, `getgrgid`, `struct group` |
| `<sys/resource.h>` | 资源限制 | `getrlimit`, `setrlimit`, `getrusage`, `RLIMIT_NOFILE` |

### 进程间通信（IPC）

| 头文件 | 核心内容 | 常用函数 |
| --- | --- | --- |
| `<sys/ipc.h>` | IPC 共用定义 | `ftok`, `IPC_CREAT`, `IPC_RMID` |
| `<sys/shm.h>` | 共享内存（System V） | `shmget`, `shmat`, `shmdt`, `shmctl` |
| `<sys/msg.h>` | 消息队列（System V） | `msgget`, `msgsnd`, `msgrcv` |
| `<mqueue.h>` | POSIX 消息队列 | `mq_open`, `mq_send`, `mq_receive`, `mq_close` |

### 正则与字符串（POSIX 扩展）

| 头文件 | 核心内容 | 常用函数 |
| --- | --- | --- |
| `<regex.h>` | POSIX 正则表达式 | `regcomp`, `regexec`, `regfree`, `regerror` |
| `<strings.h>` | BSD 兼容字符串 | `strcasecmp`, `strncasecmp`, `bzero`（已废弃，用 `memset`） |
| `<fnmatch.h>` | 文件名模式匹配 | `fnmatch`, `FNM_PATHNAME`, `FNM_PERIOD` |
| `<glob.h>` | 路径名展开 | `glob`, `globfree` |
| `<wordexp.h>` | Shell 风格词展开 | `wordexp`, `wordfree` |

---

## 第三部分：快速对照表

以下按"想做什么"快速定位该用哪个头文件：

| 想做什么 | ISO C | POSIX |
| --- | --- | --- |
| 格式化输出 | `<stdio.h>` printf | — |
| 打开/读写文件（带缓冲） | `<stdio.h>` fopen | — |
| 打开/读写文件（无缓冲） | — | `<fcntl.h>` open + `<unistd.h>` read/write |
| 分配内存 | `<stdlib.h>` malloc | `<sys/mman.h>` mmap |
| 字符串操作 | `<string.h>` | `<strings.h>`（大小写无关比较） |
| 数学运算 | `<math.h>` | — |
| 获取当前时间 | `<time.h>` time/clock | `<time.h>` clock_gettime |
| 创建子进程 | — | `<unistd.h>` fork + `<sys/wait.h>` |
| 创建线程 | `<threads.h>`（C11，少用） | `<pthread.h>` |
| 网络通信 | — | `<sys/socket.h>` + `<netdb.h>` |
| 遍历目录 | — | `<dirent.h>` |
| 动态加载库 | — | `<dlfcn.h>` |
| 正则匹配 | — | `<regex.h>` |
| 信号处理 | `<signal.h>`（基础） | `<signal.h>`（sigaction，更可靠） |
| 原子操作 | `<stdatomic.h>`（C11） | — |
| 内存映射文件 | — | `<sys/mman.h>` |
| 查询文件属性 | — | `<sys/stat.h>` |

---

## 第四部分：编译时如何启用

### ISO C17

```bash
clang -std=c17 -Wall -Wextra -Wpedantic main.c -o main -lm
```

`-lm` 链接数学库。其余标准库函数默认链接。`-std=c17` 启用 C17 标准并禁用编译器扩展。

### POSIX

```bash
# 方式一：通过宏声明（推荐放在源文件最顶部或编译参数中）
clang -std=c17 -D_POSIX_C_SOURCE=200809L -Wall main.c -o main

# 方式二：在源文件顶部（必须在任何 #include 之前）
#define _POSIX_C_SOURCE 200809L
#include <unistd.h>
```

macOS 默认对 POSIX 函数可见性较为宽松，但显式声明宏是良好习惯，避免在其他平台编译失败。

### 需要额外链接的库

| 功能 | 链接参数 |
| --- | --- |
| 数学函数 | `-lm` |
| POSIX 线程 | `-pthread`（注意不是 `-lpthread`，虽然两者通常等价） |
| 动态加载 | `-ldl`（Linux；macOS 默认包含） |
| 实时扩展（mq、shm） | `-lrt`（Linux；macOS 无需） |

---

## 第五部分：macOS 与 Linux 的差异

| 方面 | macOS | Linux |
| --- | --- | --- |
| 编译器 | Apple Clang（基于 LLVM） | GCC 或 Clang |
| `<threads.h>` | 不支持（用 pthread） | GCC 12+ / Clang 支持 |
| `epoll` | 不可用（用 `kqueue`） | `<sys/epoll.h>` |
| `kqueue` | `<sys/event.h>` | 不可用（用 `epoll`） |
| `sendfile` | 签名不同 | `<sys/sendfile.h>` |
| 内存泄漏检测 | `leaks` / MallocStackLogging | valgrind / ASan |
| `/proc` 文件系统 | 无 | `/proc/self/maps` 等 |
| `dlopen` | 默认可用 | 需要 `-ldl` |

本课程的系统编程章节（15-20）均在 macOS 上验证通过。遇到平台差异时，`man` 页面的 CONFORMING TO 部分会标明函数来源。

---

## 使用建议

1. **先学 ISO C 标准库**：前 12 章涉及的全部是标准库函数，跨平台通用。
2. **系统编程用 POSIX**：第 15-20 章进入 POSIX 领域，这是 Unix 世界的通用接口。
3. **不要死记**：建立"哪类功能在哪个头文件"的印象即可。需要具体函数签名时查 `man` 或在线文档。
4. **查阅顺序**：`man 3 函数名`（库函数）→ `man 2 函数名`（系统调用）→ 在线 POSIX spec。
5. **CPython 相关**：CPython 自身大量使用 POSIX API（`fork`、`mmap`、`pthread`、`dlopen`），理解这些接口有助于阅读 CPython 源码。

```bash
# 快速查看某个函数属于哪个标准
man printf      # CONFORMING TO 段落会标明 C99, POSIX.1-2001 等
man 2 open      # 系统调用
man 3 pthread_create  # POSIX 线程库
```
