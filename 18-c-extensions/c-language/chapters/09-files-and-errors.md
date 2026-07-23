# 09 文件与错误处理

## 学习目标

完成本章后，你应该能够：

- 安全打开、读取、写入和关闭文本或二进制文件
- 区分 EOF、解析失败和 I/O 错误
- 理解三种缓冲模式及其对输出行为的影响
- 使用 `setjmp`/`longjmp` 实现非局部跳转，并识别其危险
- 设计调用者可以处理的结构化错误返回值
- 在多条失败路径上正确释放已获得资源
- 处理部分读取、部分写入和关闭阶段错误
- 使用 POSIX 接口操作目录和文件元数据
- 理解文件锁的协作性质和使用场景

## 先运行示例

```c
// demo_file.c — 观察缓冲和错误行为
#include <stdio.h>
#include <errno.h>
#include <string.h>

int main(void) {
    FILE *f = fopen("/tmp/demo_output.txt", "w");
    if (!f) {
        fprintf(stderr, "打开失败: %s\n", strerror(errno));
        return 1;
    }

    fprintf(f, "第一行\n");
    printf("写入尚未落盘 — 数据在缓冲区\n");

    if (fflush(f) != 0) {
        perror("fflush");
    }
    printf("fflush 后数据已提交到内核\n");

    if (fclose(f) != 0) {
        perror("fclose");
        return 1;
    }
    printf("文件安全关闭\n");
    return 0;
}
```

编译运行：`gcc -Wall -o demo_file demo_file.c && ./demo_file`

在运行前后用 `cat /tmp/demo_output.txt` 观察文件内容变化。

## 文件流生命周期

```text
fopen -> 检查 -> 设置缓冲(可选) -> 读写 -> 检查流状态 -> fflush(写入时) -> fclose
```

```c
FILE *file = fopen(path, "r");
if (file == NULL) {
    perror(path);
    return 1;
}

/* 使用 file */

if (fclose(file) != 0) {
    perror("fclose");
    return 1;
}
```

写入可能先停留在用户态缓冲区，因此 `fprintf` 成功后，`fflush` 或 `fclose` 仍可能因磁盘空间、设备或网络文件系统错误而失败。永远检查 `fclose` 返回值。

## 标准流

程序启动时有三个预定义流：

| 流 | 文件描述符 | 默认缓冲 | 用途 |
|---|---|---|---|
| `stdin` | 0 | 行缓冲（终端）/ 全缓冲（管道） | 读取用户输入 |
| `stdout` | 1 | 行缓冲（终端）/ 全缓冲（管道） | 正常输出 |
| `stderr` | 2 | 无缓冲 | 错误消息 |

Python 中 `sys.stdout` 和 `sys.stderr` 的关系与此对应。`stderr` 无缓冲意味着错误消息立即可见，即使程序随后崩溃。

```c
// 验证缓冲行为
fprintf(stdout, "这条消息可能被缓冲");
fprintf(stderr, "这条立即可见\n");
// 如果重定向 stdout 到文件，第一条可能在程序结束时才出现
```

**管道交互**：当 `stdout` 被重定向到管道时，缓冲模式从行缓冲变为全缓冲。这就是为什么 `printf` 在管道中可能不会立即输出——需要显式 `fflush(stdout)` 或用 `setlinebuf(stdout)` 恢复行缓冲。

**检查写入错误**：向 `stdout` 写入也可能失败（管道断裂、磁盘满）。健壮程序在退出前检查：

```c
if (fflush(stdout) != 0 || ferror(stdout)) {
    return EXIT_FAILURE;
}
```

## 缓冲模式

C 标准定义三种缓冲策略，可用 `setvbuf` 在第一次 I/O 之前设置：

```c
// 全缓冲：缓冲区满或 fflush 时才写出
setvbuf(file, NULL, _IOFBF, 8192);

// 行缓冲：遇到换行或缓冲区满时写出
setvbuf(file, NULL, _IOLBF, 1024);

// 无缓冲：每次操作立即写出
setvbuf(file, NULL, _IONBF, 0);
```

| 模式 | 宏 | 何时刷新 | 典型用途 |
|---|---|---|---|
| 全缓冲 | `_IOFBF` | 缓冲区满 / `fflush` / `fclose` | 文件 I/O |
| 行缓冲 | `_IOLBF` | 换行 / 缓冲区满 / `fflush` | 终端交互 |
| 无缓冲 | `_IONBF` | 每次调用 | 错误日志 |

**为什么 `stderr` 无缓冲**：如果错误信息也被缓冲，程序在 `abort()` 或段错误后缓冲区内容就丢失了。无缓冲保证每个 `fprintf(stderr, ...)` 立即到达目的地。

**`fflush` 语义**：

```c
fflush(file);   // 刷新指定流
fflush(NULL);   // 刷新所有打开的输出流
```

`fflush` 只保证数据从用户态缓冲区传给内核。要确保数据写入物理存储，还需要 `fsync(fileno(file))`（POSIX）。

注意：对输入流调用 `fflush` 是未定义行为（某些系统扩展允许，但不可移植）。

## 文本读取

`fgets` 适合逐行读取，但要区分正常结束和错误：

```c
char line[256];
while (fgets(line, sizeof line, file) != NULL) {
    /* 处理本次读取到的内容；一行过长时可能分成多次。 */
}

if (ferror(file)) {
    perror("read");
}
```

`fscanf` 返回成功转换的字段数量。返回 `EOF` 可能表示输入结束，也可能表示读取错误；格式不匹配时可能返回 `0`，并把不匹配输入留在流中。因此面向用户输入时，先读取整行再用 `strtol` 等函数解析通常更容易恢复。

## 二进制读写与部分完成

`fread` 和 `fwrite` 以"元素"为单位返回实际完成数量：

```c
size_t written = fwrite(values, sizeof values[0], count, file);
if (written != count) {
    if (ferror(file)) {
        perror("fwrite");
    }
    /* 文件现在可能只包含前 written 个元素。 */
}
```

一次调用没有完成全部请求时，程序必须决定重试、报告部分成功，还是删除不完整输出。不能把文件写入当作天然事务。

对比 Python：`f.write(data)` 在普通文件上通常完整写入或抛出异常；C 要求你自己处理部分完成的情况。

## 错误模型

C 没有标准异常机制。常见接口设计包括：

- 返回 `bool`，通过输出参数返回结果
- 返回枚举错误码，区分无效输入、内存不足和 I/O 错误
- 返回指针，以 `NULL` 表示失败
- 返回已处理数量，让调用者识别部分成功

`errno` 只应在某个 API 的文档明确说明"失败时设置 errno"且返回值已经表示失败后读取。并非所有标准库函数都会设置它，成功调用后也不能把旧 `errno` 当作新错误。

```c
errno = 0;
long value = strtol(text, &end, 10);
if (errno == ERANGE) {
    /* 超出 long 范围 */
}
```

**`perror` 和 `strerror` 的区别**：

```c
perror("open");            // 打印 "open: No such file or directory\n" 到 stderr
strerror(errno)            // 返回错误描述字符串，供自定义消息使用
fprintf(stderr, "打开 %s 失败: %s\n", path, strerror(errno));
```

`strerror` 返回的字符串在下次调用 `strerror` 前有效；多线程环境用 `strerror_r`（POSIX）或 `strerror_s`（C11）。

## 结构化错误处理模式

当项目规模增长后，简单的 `int` 返回码不够用。可以设计错误枚举加上下文结构体：

```c
typedef enum {
    ERR_OK = 0,
    ERR_IO,
    ERR_PARSE,
    ERR_NOMEM,
    ERR_OVERFLOW,
} ErrorCode;

typedef struct {
    ErrorCode code;
    int       os_errno;     // 保存失败时的 errno
    const char *file;       // __FILE__
    int       line;         // __LINE__
    char      message[256]; // 人类可读描述
} Error;

#define MAKE_ERROR(err, ec, fmt, ...) do { \
    (err)->code = (ec);                    \
    (err)->os_errno = errno;               \
    (err)->file = __FILE__;                \
    (err)->line = __LINE__;                \
    snprintf((err)->message, sizeof (err)->message, fmt, ##__VA_ARGS__); \
} while (0)
```

调用方式：

```c
bool read_config(const char *path, Config *out, Error *err) {
    FILE *f = fopen(path, "r");
    if (!f) {
        MAKE_ERROR(err, ERR_IO, "无法打开配置文件 %s", path);
        return false;
    }
    // ...解析逻辑...
    fclose(f);
    return true;
}
```

这种模式的优势：调用者可以根据 `code` 决定重试或报告，`message` 提供用户友好描述，`os_errno` 保留系统级细节用于调试。对比 Python 的异常链（`raise ... from ...`），C 需要手动传递上下文。

## 资源清理与 goto 模式

函数逐步获取多个资源时，可以使用单一清理区：

```c
int copy_file(const char *source_path, const char *target_path) {
    int result = -1;
    FILE *source = NULL;
    FILE *target = NULL;
    char *buffer = NULL;

    source = fopen(source_path, "rb");
    if (source == NULL) goto cleanup;

    target = fopen(target_path, "wb");
    if (target == NULL) goto cleanup;

    buffer = malloc(COPY_BUF_SIZE);
    if (buffer == NULL) goto cleanup;

    size_t n;
    while ((n = fread(buffer, 1, COPY_BUF_SIZE, source)) > 0) {
        if (fwrite(buffer, 1, n, target) != n) goto cleanup;
    }
    if (ferror(source)) goto cleanup;

    result = 0;  // 全部成功

cleanup:
    free(buffer);
    if (target != NULL && fclose(target) != 0) result = -1;
    if (source != NULL) fclose(source);
    return result;
}
```

`goto cleanup` 在这种局部资源回滚场景中可以减少重复代码。关键是所有跳转都只向前进入清理区，不形成难以跟踪的控制流。

## 多资源清理的完整模式

对比嵌套 `if` 方式和 `goto` 方式处理三个以上资源：

**嵌套 if（深层缩进，易遗漏）**：

```c
int process(const char *a_path, const char *b_path, const char *out_path) {
    FILE *a = fopen(a_path, "r");
    if (a) {
        FILE *b = fopen(b_path, "r");
        if (b) {
            FILE *out = fopen(out_path, "w");
            if (out) {
                char *buf = malloc(4096);
                if (buf) {
                    /* 实际工作 */
                    free(buf);
                }
                fclose(out);
            }
            fclose(b);
        }
        fclose(a);
    }
    return a && /* ... */ ? 0 : -1;  // 错误信息已丢失
}
```

**goto 方式（线性、清晰）**：

```c
int process(const char *a_path, const char *b_path, const char *out_path) {
    int rc = -1;
    FILE *a = NULL, *b = NULL, *out = NULL;
    char *buf = NULL;

    a = fopen(a_path, "r");    if (!a) goto done;
    b = fopen(b_path, "r");    if (!b) goto done;
    out = fopen(out_path, "w");if (!out) goto done;
    buf = malloc(4096);        if (!buf) goto done;

    /* 实际工作 */
    rc = 0;

done:
    free(buf);
    if (out) fclose(out);
    if (b) fclose(b);
    if (a) fclose(a);
    return rc;
}
```

释放顺序与获取顺序相反——和 Python `with` 语句嵌套退出的顺序相同。`free(NULL)` 是安全的；`fclose(NULL)` 不安全，所以需要 `if` 守护。

## `setjmp` / `longjmp`：非局部跳转

C 提供 `<setjmp.h>` 实现跨函数的跳转，类似极简版异常：

```c
#include <setjmp.h>
#include <stdio.h>

static jmp_buf recover_point;

void risky_operation(void) {
    // 模拟深层调用中发现不可恢复错误
    longjmp(recover_point, 1);  // 跳回 setjmp 处，返回值 1
    // 以下代码永远不会执行
}

int main(void) {
    int status = setjmp(recover_point);
    if (status == 0) {
        // 正常路径：setjmp 首次返回 0
        printf("开始操作\n");
        risky_operation();
        printf("这行不会执行\n");
    } else {
        // 恢复路径：从 longjmp 跳回，status = 1
        printf("从错误中恢复，status=%d\n", status);
    }
    return 0;
}
```

**危险和限制**：

1. **跳过资源清理**：`longjmp` 不会关闭文件、释放内存或调用析构函数。中间函数分配的资源全部泄漏。
2. **栈帧失效**：只能跳到仍然活跃的栈帧。如果设置 `setjmp` 的函数已经返回，行为未定义。
3. **局部变量状态**：`setjmp` 和 `longjmp` 之间修改的非 `volatile` 局部变量值不确定。
4. **信号处理**：`sigsetjmp`/`siglongjmp` 额外保存信号掩码。

```c
// volatile 确保变量在 longjmp 后可用
volatile int resource_count = 0;
```

**为什么 C++ 发明了异常**：C++ 异常在栈展开时自动调用析构函数（RAII），解决了 `longjmp` 跳过清理的根本问题。CPython 内部不使用 `longjmp` 做错误处理，而是用返回值 + 全局异常状态（`PyErr_SetString` 等）。

**实际使用场景**：`setjmp`/`longjmp` 在实践中主要用于：
- 从深层递归中紧急跳出（如解析器遇到不可恢复语法错误）
- 实现协程（早期实现）
- 某些测试框架的 `assert` 恢复机制

## 临时文件

**`tmpfile()`（标准 C）**：

```c
FILE *tmp = tmpfile();
if (!tmp) {
    perror("tmpfile");
    return -1;
}
// tmp 是一个匿名文件，关闭或程序退出时自动删除
fprintf(tmp, "临时数据\n");
rewind(tmp);
// ...读回数据...
fclose(tmp);  // 文件自动消失
```

`tmpfile` 创建的文件没有可见的目录名，安全且方便。缺点是无法将其 `rename` 到目标路径（因为没有路径名）。

**`mkstemp()`（POSIX）**：

```c
#include <stdlib.h>
#include <unistd.h>

char template[] = "/tmp/myapp_XXXXXX";  // 必须可写
int fd = mkstemp(template);
if (fd == -1) {
    perror("mkstemp");
    return -1;
}
// template 现在包含实际文件名，如 "/tmp/myapp_a3f9K2"
// fd 是已打开的文件描述符
FILE *tmp = fdopen(fd, "w+");
// ... 使用 ...
fclose(tmp);
// 用完后需要手动 unlink
unlink(template);
```

`mkstemp` 原子地创建文件并返回描述符，避免竞态条件。模板中的 `XXXXXX` 被替换为唯一字符。

**为什么 `tmpnam` 不安全**：`tmpnam` 只返回一个文件名但不创建文件，在返回名字和打开文件之间存在 TOCTOU（time-of-check-to-time-of-use）竞态——攻击者可以抢先创建同名文件（符号链接攻击）。现代代码应使用 `mkstemp` 或 `tmpfile`。

## 安全替换文件

覆盖重要文件时，直接打开目标并截断可能在中途失败后丢失旧内容。常见策略是：

1. 在同一文件系统用 `mkstemp` 创建临时文件。
2. 写入全部内容。
3. 调用 `fflush` 确保用户态缓冲区清空。
4. 调用 `fsync(fileno(tmp))` 确保数据持久化到磁盘（需要持久性保证时）。
5. 检查 `fclose` 返回值。
6. 使用 `rename(tmp_path, target_path)` 原子替换目标目录项。

```c
int safe_write(const char *path, const char *data, size_t len) {
    char tmp_path[] = "/tmp/safe_XXXXXX";
    int fd = mkstemp(tmp_path);
    if (fd == -1) return -1;

    FILE *f = fdopen(fd, "w");
    if (!f) { close(fd); unlink(tmp_path); return -1; }

    if (fwrite(data, 1, len, f) != len) goto fail;
    if (fflush(f) != 0) goto fail;
    if (fsync(fileno(f)) != 0) goto fail;
    if (fclose(f) != 0) { f = NULL; goto fail; }
    f = NULL;

    if (rename(tmp_path, path) != 0) {
        unlink(tmp_path);
        return -1;
    }
    return 0;

fail:
    if (f) fclose(f);
    unlink(tmp_path);
    return -1;
}
```

注意：`rename` 只在同一文件系统内保证原子性。跨文件系统需要复制加删除。

## 目录操作（POSIX）

C 标准库不提供目录遍历接口，需要 POSIX 的 `<dirent.h>`：

```c
#include <dirent.h>
#include <stdio.h>
#include <string.h>

int list_c_files(const char *dir_path) {
    DIR *dir = opendir(dir_path);
    if (!dir) {
        perror(dir_path);
        return -1;
    }

    struct dirent *entry;
    errno = 0;
    while ((entry = readdir(dir)) != NULL) {
        // 跳过 . 和 ..
        if (strcmp(entry->d_name, ".") == 0 ||
            strcmp(entry->d_name, "..") == 0) continue;

        const char *ext = strrchr(entry->d_name, '.');
        if (ext && strcmp(ext, ".c") == 0) {
            printf("  %s\n", entry->d_name);
        }
    }

    if (errno != 0) {
        perror("readdir");
    }
    closedir(dir);
    return 0;
}
```

`readdir` 返回 `NULL` 表示结束或错误——需要在循环前清除 `errno`，循环后检查它。

**`stat` 获取文件元数据**：

```c
#include <sys/stat.h>

struct stat st;
if (stat(path, &st) != 0) {
    perror(path);
    return -1;
}

printf("大小: %lld 字节\n", (long long)st.st_size);
printf("是普通文件: %s\n", S_ISREG(st.st_mode) ? "是" : "否");
printf("是目录: %s\n", S_ISDIR(st.st_mode) ? "是" : "否");
printf("最后修改: %ld\n", (long)st.st_mtime);
```

对比 Python 的 `os.stat()` 和 `pathlib.Path.stat()`，C 的 `stat` 结构体直接对应内核数据。`lstat` 不跟随符号链接，`fstat` 操作已打开的文件描述符。

## 文件锁

多个进程同时读写同一文件时，需要协调访问。POSIX 提供两种主要锁机制：

**`flock`（BSD 咨询锁）**：

```c
#include <sys/file.h>

int fd = open(path, O_RDWR);

// 获取独占锁（写锁），阻塞等待
if (flock(fd, LOCK_EX) != 0) {
    perror("flock");
    close(fd);
    return -1;
}

// ... 对文件进行读写操作 ...

// 释放锁
flock(fd, LOCK_UN);
close(fd);  // close 也会自动释放锁
```

`LOCK_SH` 是共享锁（多个读者可同时持有），`LOCK_EX` 是独占锁。添加 `LOCK_NB` 可以非阻塞尝试。

**`fcntl` 锁（POSIX 记录锁）**：

```c
#include <fcntl.h>

struct flock lock = {
    .l_type = F_WRLCK,     // 写锁
    .l_whence = SEEK_SET,
    .l_start = 0,          // 从文件开头
    .l_len = 0,            // 0 表示锁定整个文件
};

if (fcntl(fd, F_SETLKW, &lock) == -1) {  // F_SETLKW 阻塞等待
    perror("fcntl lock");
    return -1;
}
// ... 操作 ...
lock.l_type = F_UNLCK;
fcntl(fd, F_SETLK, &lock);
```

`fcntl` 锁可以锁定文件的一部分（字节范围），比 `flock` 更精细。但注意：`fcntl` 锁绑定到进程+inode，同一进程内任何一个引用该文件的 fd 被关闭都会释放锁。

**关键概念——咨询锁**：POSIX 文件锁是"咨询性"的（advisory），不遵守协议的进程可以无视锁直接读写文件。只有所有参与进程都使用锁时，协调才有效。这和 Python 的 `fcntl.flock()` 行为一致。

## 常见错误

- 只检查 `fopen`，忽略读取、写入和关闭错误
- 把 EOF 和读取错误混为一谈（`fgets` 返回 `NULL` 不一定是错误）
- 假定一次写入必定完整
- 解析失败后继续使用未初始化结果
- 打印错误后仍按成功路径运行
- 所有函数都盲目读取 `errno`（`errno` 只在失败确认后有意义）
- 多条失败路径遗漏关闭或释放
- 在管道输出中不 `fflush`，导致数据丢失
- 使用 `tmpnam` 创建临时文件（TOCTOU 竞态）
- `longjmp` 跳过了资源释放代码
- 对 `NULL` 调用 `fclose`（未定义行为，不像 `free(NULL)` 安全）
- 混淆 `flock` 和 `fcntl` 锁的语义（它们不互通）
- `setvbuf` 在第一次 I/O 之后调用（行为未定义）
- `readdir` 循环不区分结束和错误（两者都返回 `NULL`）

## 检查点

1. `fgets` 返回 `NULL` 是否一定表示错误？如何区分 EOF 和 I/O 错误？
2. 为什么写入函数成功后仍要检查 `fclose`？
3. 为什么 `errno` 必须与具体失败返回值一起解释？
4. `setvbuf` 必须在什么时候调用才有效？
5. `tmpfile()` 和 `mkstemp()` 各适合什么场景？
6. `longjmp` 相比 `goto cleanup` 有什么根本性劣势？
7. 为什么 `fcntl` 锁在同一进程中关闭任意一个 fd 就会释放？
8. `stdout` 重定向到管道后缓冲行为如何变化？

## 动手练习

1. 完成 `exercises/07_word_count.c`，统计行、单词和字节数量。
2. 测试空文件、最后一行没有换行、文件不存在和无权限路径。
3. 修改程序，让读取错误与普通 EOF 返回不同状态。
4. 实现临时文件加 `rename` 的安全保存流程，并设计失败清理。
5. 编写一个程序，用 `setvbuf` 设置不同缓冲模式，重定向到文件后观察 `strace`/`dtruss` 中 `write` 系统调用的频率差异。
6. 实现一个递归目录遍历函数，使用 `opendir`/`readdir`/`stat` 打印所有普通文件的路径和大小。
7. 编写使用 `setjmp`/`longjmp` 的简单解析器，在语法错误时跳出递归下降，观察如果中途有 `malloc` 分配会发生什么。
8. 实现一个简单的文件锁演示：两个进程竞争写入同一文件，对比有锁和无锁时的输出交错情况。
