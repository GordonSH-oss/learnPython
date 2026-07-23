# 08 动态内存

## 学习目标

完成本章后，你应该能够：

- 使用 `malloc`、`calloc`、`realloc`、`aligned_alloc` 和 `free` 管理动态对象
- 在分配前检查大小计算溢出
- 为指针和资源建立明确所有权
- 识别泄漏、重复释放、释放后使用和错误的 `realloc` 写法
- 实现具有失败回滚能力的动态数组
- 使用柔性数组成员替代旧的 `data[1]` 技巧
- 实现基本引用计数共享所有权
- 理解内存池与 arena 模式的应用场景
- 使用 valgrind / ASan 调试内存问题
- 解释 CPython 为何要求扩展使用 `PyMem_*` 函数

## 先运行示例

```bash
clang -std=c17 -Wall -Wextra -Wpedantic \
  -fsanitize=address,undefined -fno-omit-frame-pointer -g \
  examples/08_dynamic_memory.c -o /tmp/dynamic-memory
/tmp/dynamic-memory
```

如果代码没有内存错误，sanitizer 不会输出任何诊断。如果有泄漏或越界，程序退出时会打印完整的调用栈。先跑通再读代码。

## 为什么需要动态内存

编译时无法确定元素数量，或对象需要在创建函数返回后继续存在时，可以动态分配。动态对象从成功分配开始存在，直到被 `free`；离开创建它的代码块不会自动释放。

Python 中你可以随意 `append`，不用考虑底层分配——解释器帮你做了。C 里一切要自己管：分多大、什么时候释放、谁负责释放。这种显式控制正是 CPython 扩展开发需要掌握的核心能力。

```c
#include <stdint.h>
#include <stdlib.h>

if (count > SIZE_MAX / sizeof(int)) {
    return NULL;  /* 溢出检查：count * sizeof(int) 会回绕 */
}

int *values = malloc(count * sizeof *values);
if (values == NULL && count != 0) {
    return NULL;
}
```

使用 `sizeof *values` 可避免元素类型变化后大小表达式不同步。乘法必须在调用 `malloc` 前检查溢出，否则较大的请求可能回绕成较小分配，随后写入会越界。

## `malloc` 与 `calloc`

`malloc` 返回的字节内容未初始化，读取其中尚未写入的对象值可能产生未定义行为。

```c
int *values = calloc(count, sizeof *values);
```

`calloc` 会把分配区域的所有字节置零，并负责处理元素数量与大小的乘法检查。全零字节通常对应整数零和浮点零，但不能把这个结论推广到所有可能的 C 类型表示——例如空指针的内部表示不一定是全零（虽然主流平台都是）。

选择建议：

- 需要清零的缓冲区、数组：用 `calloc`
- 即将被完全覆盖的缓冲区（如 `read` 填充）：用 `malloc` 避免无用清零
- 不确定时：用 `calloc`，安全优先

## `aligned_alloc`——对齐分配

普通 `malloc` 返回的地址满足 `max_align_t` 对齐（通常 8 或 16 字节）。但某些场景需要更严格的对齐：

- SIMD 指令（SSE 要求 16 字节，AVX 要求 32 字节）
- 硬件 DMA 要求页对齐
- 某些数据结构利用低位地址位存储标志

C11 提供了 `aligned_alloc`：

```c
#include <stdlib.h>

/* 分配 32 字节对齐的 1024 字节缓冲区 */
void *buf = aligned_alloc(32, 1024);
if (buf == NULL) { /* 处理失败 */ }

/* 使用完毕后用普通 free 释放 */
free(buf);
```

约束：`size` 必须是 `alignment` 的整数倍，`alignment` 必须是 2 的幂。违反这些约束时行为未定义。

在 C11 之前，POSIX 提供 `posix_memalign`，Windows 提供 `_aligned_malloc`（需配对 `_aligned_free`）。如果你的代码需要跨平台，可以封装一层：

```c
void *aligned_malloc(size_t alignment, size_t size) {
#if defined(_WIN32)
    return _aligned_malloc(size, alignment);
#else
    void *ptr = NULL;
    if (posix_memalign(&ptr, alignment, size) != 0) return NULL;
    return ptr;
#endif
}
```

## 所有权与生命周期

每块动态内存都应有一个明确的释放责任。接口应说明：

- **借用**：函数临时使用指针，不保存也不释放
- **接管**：函数成功后负责释放对象
- **返回所有权**：调用者获得对象并必须释放
- **共享**：多个使用者通过额外协议（如引用计数）协调生命周期

```c
free(values);
values = NULL;
```

设为 `NULL` 只能避免通过这个变量再次使用；其他保存了同一地址的指针仍然会悬空。在代码审查中，所有权必须在文档注释或命名约定中体现，而不是靠隐式约定。

## 安全使用 `realloc`

`realloc` 可能原地扩展，也可能分配新区域、复制内容并释放旧区域：

```c
if (new_count > SIZE_MAX / sizeof *values) {
    return false;
}

int *new_values = realloc(values, new_count * sizeof *values);
if (new_values == NULL) {
    /* values 仍然有效，由原所有者决定继续使用还是释放。 */
    return false;
}
values = new_values;
```

不要直接写 `values = realloc(values, ...)`，否则失败时会丢失旧地址。也不要依赖 `realloc(ptr, 0)` 的平台差异（C11 将其行为定义为实现决定）；需要释放时直接调用 `free(ptr)`。

## 动态数组扩容

扩容通常分为四步：

1. 判断是否需要扩容（`len >= capacity`）。
2. 计算新容量并检查加倍和字节乘法溢出。
3. 用临时指针调用 `realloc`。
4. 只有成功后才提交新指针和新容量。

```c
typedef struct {
    int    *data;
    size_t  len;
    size_t  capacity;
} IntVec;

/* 返回 true 表示成功，false 表示内存不足（原数组不变）。 */
bool intvec_push(IntVec *v, int value) {
    if (v->len >= v->capacity) {
        size_t new_cap = v->capacity == 0 ? 4 : v->capacity * 2;
        if (new_cap > SIZE_MAX / sizeof *v->data) return false;
        int *tmp = realloc(v->data, new_cap * sizeof *v->data);
        if (tmp == NULL) return false;
        v->data     = tmp;
        v->capacity = new_cap;
    }
    v->data[v->len++] = value;
    return true;
}
```

```text
旧状态 --realloc 失败--> 旧状态保持有效，返回 false
   |
   +--realloc 成功--> 同时更新 data 和 capacity，再追加元素
```

这是一种事务式更新：失败不能留下"指针已改变但容量没改变"的半成品状态。

## 柔性数组成员（Flexible Array Members）

C99 引入了柔性数组成员，用于在结构体末尾放置可变长度的数组：

```c
typedef struct {
    size_t len;
    int    data[];  /* 柔性数组成员，大小为 0 */
} IntArray;
```

分配时一次性分配头部和数据：

```c
IntArray *arr = malloc(sizeof(IntArray) + count * sizeof(int));
if (arr == NULL) return NULL;
arr->len = count;
/* arr->data[0] 到 arr->data[count-1] 已可用（未初始化） */
```

优点：

- 一次 `malloc`、一次 `free`——没有内部指针需要单独释放
- 头部和数据在内存中连续，缓存友好
- 不会出现"释放了结构体但忘了释放内部缓冲区"的错误

与旧技巧 `data[1]` 的区别：

```c
/* 旧写法（C89 hack，技术上是未定义行为） */
struct OldArray { size_t len; int data[1]; };
struct OldArray *p = malloc(sizeof *p + (n - 1) * sizeof(int));

/* C99 正确写法 */
struct NewArray { size_t len; int data[]; };
struct NewArray *p = malloc(sizeof *p + n * sizeof(int));
```

旧技巧中 `data[1]` 只有一个合法元素，访问 `data[2]` 及之后在标准层面是未定义行为。柔性数组成员把这种模式标准化了。CPython 内部的 `PyBytesObject` 就使用类似模式在对象头后直接跟字节数据。

约束：柔性数组成员必须是结构体的最后一个成员，且结构体至少还需有一个其他成员。不能对含有柔性数组成员的结构体使用 `sizeof` 来计算完整大小——`sizeof(IntArray)` 只包含 `len` 的大小加上可能的填充。

## 内存池与 arena 模式

当程序需要大量分配同一尺寸的小对象时，频繁调用 `malloc`/`free` 带来的开销和碎片化会成为瓶颈。内存池（memory pool）和 arena 是两种优化模式。

### Bump Allocator（arena）

arena 是最简单的分配器：维护一大块预分配的内存和一个偏移指针，每次分配只需移动偏移量：

```c
typedef struct {
    char   *base;
    size_t  capacity;
    size_t  offset;
} Arena;

Arena arena_create(size_t capacity) {
    Arena a = { .base = malloc(capacity), .capacity = capacity, .offset = 0 };
    return a;
}

void *arena_alloc(Arena *a, size_t size) {
    /* 对齐到 8 字节 */
    size = (size + 7) & ~(size_t)7;
    if (a->offset + size > a->capacity) return NULL;
    void *ptr = a->base + a->offset;
    a->offset += size;
    return ptr;
}

void arena_destroy(Arena *a) {
    free(a->base);
    a->base = NULL;
    a->capacity = a->offset = 0;
}
```

特点：

- 分配极快——只是一次加法和比较
- 不支持单个对象释放——只能一次性销毁整个 arena
- 适用场景：编译器的 AST 节点、请求处理中的临时对象、游戏的帧级分配

### 固定大小对象池

如果所有对象大小相同，可以用空闲链表管理：

```c
typedef struct Block {
    struct Block *next;
} Block;

typedef struct {
    Block  *free_list;
    char   *storage;
    size_t  block_size;
    size_t  count;
} Pool;
```

初始化时把整块内存切成等大的 block，每个 block 的前几个字节存放指向下一个空闲 block 的指针。分配就是取链表头，释放就是插入链表头。常数时间，零碎片。

CPython 内部的 `obmalloc` 对小对象（<= 512 字节）就采用类似的池化策略。

## 引用计数

当多个使用者需要共享同一块动态内存时，"谁来释放"成为难题。引用计数是最直接的解决方案：给对象附加一个计数器，每多一个使用者加一，用完减一，减到零时释放。

```c
typedef struct {
    size_t refcount;
    size_t len;
    char   data[];
} SharedBuf;

SharedBuf *sharedbuf_create(size_t len) {
    SharedBuf *buf = malloc(sizeof(SharedBuf) + len);
    if (buf == NULL) return NULL;
    buf->refcount = 1;
    buf->len = len;
    return buf;
}

SharedBuf *sharedbuf_retain(SharedBuf *buf) {
    buf->refcount++;
    return buf;
}

void sharedbuf_release(SharedBuf *buf) {
    if (buf == NULL) return;
    if (--buf->refcount == 0) {
        free(buf);
    }
}
```

使用模式：

```c
SharedBuf *original = sharedbuf_create(1024);
SharedBuf *alias = sharedbuf_retain(original);  /* refcount = 2 */

/* ... 两个地方各自独立使用 ... */

sharedbuf_release(alias);     /* refcount = 1 */
sharedbuf_release(original);  /* refcount = 0，内存释放 */
```

CPython 的对象系统正是基于引用计数。`Py_INCREF` 和 `Py_DECREF` 宏对应上面的 `retain` 和 `release`。当 `ob_refcnt` 归零时，对象的 `tp_dealloc` 被调用。

引用计数的局限：

- **循环引用**：A 引用 B，B 引用 A，两者的计数永远不会归零。CPython 用分代垃圾回收器打破循环。
- **线程安全**：上面的 `++` 和 `--` 不是原子操作。多线程环境需要原子操作或锁。CPython 用 GIL 保护引用计数。
- **性能**：频繁的 incref/decref 会导致缓存行颠簸。这也是 CPython 3.12+ 引入 immortal objects 的原因之一。

## `free` 的实现概念

理解 `free` 内部发生了什么，有助于理解为何某些错误是灾难性的。

### 空闲链表与元数据

典型的分配器（如 glibc 的 ptmalloc）在每块分配区域前存储一个小型头部，记录该块的大小、是否已分配等标志。`free(ptr)` 时，分配器：

1. 把 `ptr` 前几个字节当作头部读取，获取该块大小
2. 标记该块为"空闲"
3. 尝试与相邻空闲块合并（coalescing），减少碎片
4. 将合并后的块放入空闲链表

```text
         ptr 指向这里
              |
  [size|flags][用户数据区域...           ]
  ^
  分配器头部（用户不可见）
```

### 为何 double-free 会崩溃

第一次 `free` 把头部中的 flags 改为"已释放"，并把该块放入空闲链表。第二次 `free` 再次读取头部——但此时那块内存可能已经被重新分配出去并被写入了新数据。分配器把这些新数据当作头部解释，导致读取到损坏的大小或链表指针，随后写入到任意内存地址。这是典型的可利用漏洞：攻击者精心构造链表节点，让 `free` 把任意值写入任意地址。

### 为何 use-after-free 是可利用的

`free` 后那块内存仍然存在，只是被标记为可重用。如果：

1. 程序 A `free` 了 `ptr`
2. 程序再分配一块内存，恰好拿到同一地址
3. 程序 B 通过旧的 `ptr` 写入数据
4. 程序 A 读取新对象的数据时，实际读到了被篡改的值

攻击者可以通过控制重分配时机和写入内容，伪造对象的函数指针，从而执行任意代码。这类漏洞在浏览器引擎中极为常见。

## 分配失败策略

`malloc` 返回 `NULL` 时该怎么办？没有唯一正确答案，取决于上下文：

### 策略一：直接终止（abort）

```c
void *xmalloc(size_t size) {
    void *ptr = malloc(size);
    if (ptr == NULL && size != 0) {
        fprintf(stderr, "fatal: out of memory (%zu bytes)\n", size);
        abort();
    }
    return ptr;
}
```

适用于：工具程序、一次性脚本。简单粗暴但不会遗留不一致状态。Git 的源码就大量使用这种模式。

### 策略二：向上传播错误

```c
int *create_buffer(size_t count) {
    if (count > SIZE_MAX / sizeof(int)) return NULL;
    int *buf = malloc(count * sizeof(int));
    return buf;  /* 可能为 NULL，调用者检查 */
}
```

适用于：库代码。让调用者决定如何处理——重试、降级、还是终止。这也是 CPython C API 的标准模式：分配失败时设置 `PyErr_NoMemory()` 并返回 `NULL`。

### 策略三：预分配

在系统启动时一次性分配所有需要的内存，运行时不再调用 `malloc`。适用于实时系统和嵌入式系统，保证不会在运行时失败。

### 选择建议

| 场景 | 策略 |
|------|------|
| CPython 扩展 | 传播错误 + `PyErr_NoMemory()` |
| 命令行工具 | abort |
| 库（被第三方使用） | 传播错误 |
| 嵌入式/实时 | 预分配 |

## 调试内存问题

### AddressSanitizer（跨平台，推荐首选）

```bash
clang -std=c17 -Wall -Wextra \
  -fsanitize=address,undefined -fno-omit-frame-pointer -g \
  myprogram.c -o myprogram
./myprogram
```

ASan 能检测：越界读写、堆 use-after-free、double-free、栈越界、全局变量越界。报错示例：

```text
==12345==ERROR: AddressSanitizer: heap-use-after-free on address 0x602000000010
READ of size 4 at 0x602000000010 thread T0
    #0 0x401234 in main myprogram.c:42
```

读法：第一行说明错误类型和地址，后面的调用栈告诉你在哪行触发了错误，再往下还会有"分配在哪里"和"释放在哪里"的调用栈。

### Valgrind（Linux，检测更全面）

```bash
# 安装（Ubuntu/Debian）
sudo apt install valgrind

# 运行，检测内存泄漏
valgrind --leak-check=full --track-origins=yes ./myprogram
```

输出示例：

```text
==12345== LEAK SUMMARY:
==12345==    definitely lost: 1,024 bytes in 1 blocks
==12345==    indirectly lost: 0 bytes in 0 blocks
==12345==      possibly lost: 0 bytes in 0 blocks
==12345==    still reachable: 0 bytes in 0 blocks
```

`definitely lost` 是真正的泄漏——程序持有这块内存的唯一指针，但没有释放。`still reachable` 通常指程序退出时仍可访问的全局结构，不一定是 bug。

Valgrind 通过模拟 CPU 执行，速度较 ASan 慢约 20 倍，但不需要重新编译即可使用。

### macOS：leaks 与 MallocStackLogging

```bash
# 启用栈记录，运行程序
MallocStackLogging=1 ./myprogram

# 另一个终端查看泄漏
leaks --atExit -- ./myprogram
```

或使用 Xcode Instruments 的 Allocations 和 Leaks 模板，可视化所有分配和泄漏。

### 常见泄漏模式

1. **提前返回忘记 free**：
   ```c
   int *buf = malloc(1024);
   if (some_condition) return -1;  /* 泄漏！*/
   free(buf);
   ```
   修复：在每个 return 前释放，或使用 goto cleanup 模式。

2. **error path 遗漏释放**：
   ```c
   int *a = malloc(100);
   int *b = malloc(200);
   if (b == NULL) { return -1; }  /* a 泄漏！*/
   ```
   修复：失败时释放已分配的所有资源。

## 与 Python 的对比

| 概念 | Python | C |
|------|--------|---|
| 分配 | 隐式（`list.append()`、`dict[k]=v`） | 显式（`malloc`/`calloc`） |
| 释放 | 引用计数 + GC 自动处理 | 显式 `free`，忘了就泄漏 |
| 扩容 | `list` 内部自动 realloc | 手动 realloc + 溢出检查 |
| 对齐 | 不需要关心 | 某些场景需要 `aligned_alloc` |
| 共享所有权 | 引用计数自动管理 | 手动实现引用计数 |
| 循环引用 | 分代 GC 打破 | 需要手动设计弱引用 |

### CPython 的内存分配层次

CPython 有三层分配器：

```text
层 3: 对象层    PyObject_Malloc / PyObject_Free
层 2: 内存层    PyMem_Malloc / PyMem_Free
层 1: 原始层    PyMem_RawMalloc / PyMem_RawFree（= malloc/free）
```

为什么 CPython 扩展不能直接用 `malloc`/`free`？

1. **统计与调试**：CPython 可以追踪所有分配，帮助检测泄漏
2. **自定义分配器**：层 2 和层 3 使用 `obmalloc`（池化分配器），对小对象更快
3. **GIL 依赖**：层 2 和层 3 假设持有 GIL。如果你在释放 GIL 后分配内存，必须使用层 1 的 `PyMem_RawMalloc`
4. **一致性**：Python 对象的内存必须用 `PyObject_*` 系列分配，否则 tracemalloc 无法追踪

在 CPython 扩展中的正确做法：

```c
/* 分配 Python 对象用 PyObject_Malloc */
MyObject *obj = (MyObject *)PyObject_Malloc(sizeof(MyObject));

/* 分配非对象内存（如缓冲区），持有 GIL 时 */
char *buf = (char *)PyMem_Malloc(1024);

/* 分配非对象内存，不持有 GIL 时 */
Py_BEGIN_ALLOW_THREADS
char *raw = (char *)PyMem_RawMalloc(4096);
Py_END_ALLOW_THREADS

/* 释放必须配对 */
PyObject_Free(obj);
PyMem_Free(buf);
PyMem_RawFree(raw);
```

错配分配器和释放器（如用 `malloc` 分配后用 `PyMem_Free` 释放）是未定义行为。

## 常见错误

### 1. 整数溢出导致分配过小

```c
/* 错误：count 很大时 count * sizeof(int) 可能回绕 */
int *buf = malloc(count * sizeof(int));

/* 正确 */
if (count > SIZE_MAX / sizeof(int)) { /* 处理溢出 */ }
int *buf = malloc(count * sizeof(int));
```

### 2. 读取 `malloc` 的未初始化内存

```c
int *arr = malloc(10 * sizeof(int));
printf("%d\n", arr[0]);  /* 未定义行为：内容不确定 */
```

### 3. 泄漏：忘记释放

```c
void process(size_t n) {
    int *tmp = malloc(n * sizeof(int));
    if (n > 1000) return;  /* 泄漏：tmp 未释放 */
    /* ... 使用 tmp ... */
    free(tmp);
}
```

### 4. Double-free

```c
free(ptr);
/* ... 很多代码之后 ... */
free(ptr);  /* 未定义行为，可能崩溃或被利用 */
```

防御措施：`free(ptr); ptr = NULL;` 之后再次调用 `free(NULL)` 是安全的。

### 5. `realloc` 失败后丢失旧指针

```c
/* 错误：realloc 失败时 values 变为 NULL，旧内存泄漏 */
values = realloc(values, new_size);

/* 正确：用临时变量 */
int *tmp = realloc(values, new_size);
if (tmp == NULL) { /* 保留旧 values */ return false; }
values = tmp;
```

### 6. 丢失分配块的中间地址

```c
int *arr = malloc(10 * sizeof(int));
arr++;  /* 移动指针 */
free(arr);  /* 错误：不是 malloc 返回的地址 */
```

### 7. 所有权不清导致重复释放或泄漏

函数接受指针参数时，如果没有文档说明是否接管所有权，调用者和被调用者都可能尝试释放，或者都不释放。

### 8. 柔性数组成员使用 `sizeof` 计算错误

```c
struct Buf { size_t len; char data[]; };
/* 错误：sizeof(struct Buf) 不包含 data 的大小 */
struct Buf *b = malloc(sizeof(struct Buf));  /* 只够放 len */
b->data[0] = 'x';  /* 越界 */

/* 正确 */
struct Buf *b = malloc(sizeof(struct Buf) + capacity);
```

## 使用 sanitizer

```bash
# 推荐的开发时编译命令
clang -std=c17 -Wall -Wextra -Wpedantic \
  -fsanitize=address,undefined -fno-omit-frame-pointer -g \
  examples/08_dynamic_memory.c -o /tmp/dynamic-memory
/tmp/dynamic-memory
```

`-fsanitize=address` 检测的问题：

- 堆缓冲区溢出（读/写）
- 栈缓冲区溢出
- 全局缓冲区溢出
- Use-after-free
- Use-after-return（需加 `ASAN_OPTIONS=detect_stack_use_after_return=1`）
- Double-free
- 内存泄漏（程序退出时报告）

`-fsanitize=undefined` 额外检测：

- 有符号整数溢出
- 空指针解引用
- 数组越界（编译时已知大小的数组）
- 对齐不良的指针访问

注意：ASan 会使程序变慢约 2 倍、内存增大约 3 倍。在 CI 中运行测试时启用，生产构建中关闭。ASan 不能与 valgrind 同时使用。

## 检查点

1. `free(NULL)` 是否安全？——是，什么也不做。
2. `realloc` 失败后旧指针是否仍然有效？——在请求非零大小时是。
3. 把一个指针设为 `NULL` 是否会修复其他别名的悬空问题？——不会。
4. `calloc(n, size)` 相比 `malloc(n * size)` 的额外优点？——自动检查乘法溢出，并置零。
5. `aligned_alloc(64, 100)` 合法吗？——不合法，100 不是 64 的整数倍。应该用 `aligned_alloc(64, 128)`。
6. 柔性数组成员可以放在结构体中间吗？——不可以，必须是最后一个成员。
7. 为什么 CPython 扩展不能用 `free` 释放 `PyObject_Malloc` 分配的内存？——分配器不匹配，内部簿记结构会被破坏。
8. Arena 分配器的最大局限是什么？——不支持单个对象的释放，只能整体销毁。

## 动手练习

### 练习 1：动态数组（基础）

完成 `exercises/06_dynamic_vector.c`：

1. 实现动态整数数组，容量不足时扩为原来的两倍。
2. 检查容量加倍和字节数乘法溢出。
3. 让扩容失败保持原数组完全可用。
4. 用 sanitizer 验证无越界、重复释放和释放后使用。

### 练习 2：引用计数字符串

实现一个引用计数的字符串类型：

```c
typedef struct {
    size_t refcount;
    size_t len;
    char   data[];
} RcString;

RcString *rcstr_create(const char *src);
RcString *rcstr_retain(RcString *s);
void      rcstr_release(RcString *s);
```

验证：创建后 refcount==1，retain 后 refcount==2，release 到 0 时 free。用 ASan 确认无泄漏。

### 练习 3：简易 arena

实现本章描述的 arena 分配器，然后用它分配 1000 个结构体节点构建链表。比较使用 arena 和逐个 malloc 的代码行数、复杂度和 ASan 报告差异。
