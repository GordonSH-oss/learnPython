# 14 内存布局与虚拟内存

## 学习目标

完成本章后，你应该能够：

- 区分 C 对象的存储期与进程地址空间中的常见区域
- 解释函数调用、动态分配和结构体对齐背后的基本机制
- 解释虚拟地址、物理内存、页表、缺页异常和写时复制之间的关系
- 使用 macOS 或 Linux 工具观察实际进程的内存映射
- 识别哪些结论由 C 标准保证，哪些取决于编译器、ABI、操作系统和内存分配器

本章使用 Linux 和 macOS 上常见的实现建立心智模型。除非特别说明，地址顺序、栈增长方向、页大小和结构体布局都不是 C 标准作出的保证。

## 存储期不等于内存区域

C 标准描述的是对象何时存在，而不是操作系统必须把对象放在哪个“段”里。

| 存储期 | 常见来源 | 生命周期 | 常见实现位置 |
| --- | --- | --- | --- |
| 自动存储期 | 普通局部变量 | 进入代码块后创建，离开后失效 | 栈或寄存器 |
| 静态存储期 | 全局变量、`static` 变量 | 整个程序运行期间 | data、bss 或只读区域 |
| 线程存储期 | `_Thread_local` 对象 | 所在线程的生命周期 | 线程局部存储区域 |
| 动态分配 | `malloc` 返回的对象 | 从成功分配到 `free` | 分配器管理的映射区域 |

编译器可以把局部变量保存在寄存器中，也可以删除不可观察的变量。因此“局部变量一定在栈上”只是常见实现，不是语言规则。

## 进程地址空间：先理解简化模型

传统教材常把进程地址空间画成下面这样：

```text
低地址
┌──────────────────────────┐
│ 代码与只读数据           │
├──────────────────────────┤
│ 已初始化/零初始化数据    │
├──────────────────────────┤
│ 动态分配区域             │
├──────────────────────────┤
│ 文件映射、共享库等       │
├──────────────────────────┤
│ 栈                       │
└──────────────────────────┘
高地址
```

这个图适合解释区域职责，但不能用来预测所有地址。现代系统还会映射动态库、线程栈、共享内存、文件和匿名内存；ASLR（地址空间布局随机化）和 PIE（位置无关可执行文件）也会改变映射地址。

下面的程序只观察当前系统本次运行的结果：

```c
#include <stdio.h>
#include <stdlib.h>

int global_init = 42;
int global_uninit;
static const char message[] = "read only";

int main(void) {
    int local = 1;
    int *allocated = malloc(sizeof *allocated);
    if (allocated == NULL) {
        perror("malloc");
        return 1;
    }

    printf("initialized global:   %p\n", (void *)&global_init);
    printf("uninitialized global: %p\n", (void *)&global_uninit);
    printf("string data:          %p\n", (const void *)message);
    printf("allocated object:     %p\n", (void *)allocated);
    printf("automatic object:     %p\n", (void *)&local);

    free(allocated);
    return 0;
}
```

连续运行几次，比较哪些地址会变化。不要根据一次输出推导所有 Linux 或 macOS 进程的固定排列顺序。

> 注意：ISO C 不保证函数指针能够转换成 `void *`，所以这个可移植示例没有使用 `%p` 打印函数地址。POSIX 系统通常支持这种转换，但它不是纯 C 的通用保证。

### 检查点

- `global_init` 和 `global_uninit` 地址接近，是否代表它们一定属于同一个映射？
- 为什么重新运行程序后地址可能变化，但同一次运行中变量仍能正常互相引用？

## 函数调用与栈帧

在常见 ABI 中，函数调用需要保存返回位置、部分寄存器、参数或局部数据。这些信息通常组成栈帧。下面的递归实验可以观察不同调用层级中局部对象的地址：

```c
#include <stdio.h>

static void show_calls(int depth) {
    volatile int local = depth;
    printf("depth %d: %p\n", depth, (const void *)&local);
    if (depth < 5) {
        show_calls(depth + 1);
    }
}

int main(void) {
    show_calls(0);
    return 0;
}
```

在常见的 x86-64 和 AArch64 环境中，递归加深时地址通常减小，但 C 标准没有规定栈是否存在或向哪个方向增长。

优化还会改变结果：编译器可以内联函数、把值保存在寄存器中、删除无用对象或复用栈空间。研究栈帧时应记录编译参数，例如先使用 `-O0 -g`，再和 `-O2` 的反汇编结果比较。

可以在 LLDB 中观察调用栈：

```bash
lldb build/examples/14_memory_layout
(lldb) breakpoint set --name inspect_call_frames
(lldb) run
(lldb) thread backtrace
(lldb) frame variable
```

### 栈溢出为什么发生

线程栈大小有限，栈边界附近通常有不可访问的保护页。递归持续创建栈帧并触及保护页时，进程通常会收到 `SIGSEGV`。

```bash
ulimit -s       # shell 支持时，查看当前栈限制，通常以 KB 为单位
```

不能简单使用“栈限制除以局部数组大小”精确预测递归深度：一个栈帧还可能保存返回地址、寄存器和对齐空间，编译优化也可能删除数组或改变调用方式。主线程和工作线程的默认栈大小也可能不同。

## `malloc` 与内存分配器

`malloc` 不是每次都直接请求一个物理内存块。通常存在三层：

```text
程序中的 malloc/free
        ↓
用户态内存分配器
        ↓
操作系统的虚拟内存映射
```

分配器会缓存和复用空闲块，并通过操作系统提供的机制扩充其管理区域。Linux 分配器可能使用 `brk`、`mmap` 等机制；macOS 分配器具有自己的 zone 和尺寸分类策略。具体阈值和算法属于实现细节，不能假定“大于某个固定大小必定使用 `mmap`”。

连续 `malloc` 返回的地址也不保证递增。地址受分配尺寸、对齐、空闲块复用、线程和分配器策略影响。

### 内部碎片与外部碎片

- 内部碎片：分配器实际保留的块比程序请求的空间大，多余空间位于已分配块内部。
- 外部碎片：空闲空间分散成多个小块，总量可能足够，却无法满足一个较大的连续请求。

仅打印几个指针不能证明碎片已经发生。它最多能展示某次运行中分配器是否复用了某个地址。分析真实内存占用需要使用分配器统计信息或系统分析工具。

## 虚拟内存如何工作

程序使用的是虚拟地址。CPU 的内存管理单元根据页表把虚拟页转换为物理页帧；TLB 会缓存近期的地址转换，减少重复查询页表的成本。

```text
虚拟地址
   ↓ 拆分为虚拟页号和页内偏移
TLB / 页表
   ↓
物理页帧 + 相同页内偏移
```

页面尚未建立有效映射时会发生缺页异常。内核可能为它分配零填充页面、从文件读取内容、恢复已换出的页面，或者在访问非法时终止进程。缺页异常不一定表示程序错误。

页大小常见为 4 KiB，但不能写死。POSIX 系统可以在运行时查询：

```c
#include <stdio.h>
#include <unistd.h>

int main(void) {
    long page_size = sysconf(_SC_PAGESIZE);
    if (page_size == -1) {
        perror("sysconf");
        return 1;
    }
    printf("page size: %ld bytes\n", page_size);
    return 0;
}
```

虚拟地址空间大小也不等于实际占用的物理内存：

- VSZ 或 VIRT 表示进程拥有的虚拟地址范围规模。
- RSS 表示当前驻留在物理内存中的页面规模。
- 分配一大段虚拟地址后，操作系统可能等到页面首次被访问时才真正提供物理页。

## `fork` 与写时复制

`fork` 后，父子进程拥有彼此独立的虚拟地址空间。为了避免立即复制全部内存，操作系统通常先让两边共享相同的只读物理页；任一进程写入时，再复制相关页面，这就是写时复制（COW）。

```c
#include <stdio.h>
#include <sys/wait.h>
#include <unistd.h>

int main(void) {
    int value = 100;
    pid_t pid = fork();
    if (pid == -1) {
        perror("fork");
        return 1;
    }

    if (pid == 0) {
        value = 200;
        printf("child: address=%p value=%d\n", (void *)&value, value);
        return 0;
    }

    int status;
    printf("parent: address=%p value=%d\n", (void *)&value, value);
    if (waitpid(pid, &status, 0) == -1) {
        perror("waitpid");
        return 1;
    }
    return 0;
}
```

父子进程通常打印相同的虚拟地址，但修改互不影响。这个程序能观察地址和值，不能直接观察物理页帧编号；COW 的物理映射过程由操作系统管理。

## 内存映射权限

一个映射通常具有读、写、执行权限的组合。常见安排是：

- 机器代码：可读、可执行
- 只读常量：只读
- 全局数据和动态内存：可读、可写
- 栈：可读、可写，通常不可执行

系统通常尽量避免同一页面同时可写和可执行，这类策略常称为 W^X。向只读页面写入或从不可执行页面执行代码会触发保护异常。

## 结构体对齐与尾部填充

ABI 会规定基本类型的大小和对齐要求。编译器可以在成员之间以及结构体末尾插入填充，使成员正确对齐，并确保结构体数组中的每个元素都满足相同要求。

```c
#include <stddef.h>
#include <stdalign.h>
#include <stdio.h>

struct Padded {
    char a;
    int b;
    char c;
};

struct Reordered {
    int b;
    char a;
    char c;
};

int main(void) {
    printf("Padded: size=%zu align=%zu offsets=(%zu, %zu, %zu)\n",
           sizeof(struct Padded), alignof(struct Padded),
           offsetof(struct Padded, a), offsetof(struct Padded, b),
           offsetof(struct Padded, c));
    printf("Reordered: size=%zu align=%zu offsets=(%zu, %zu, %zu)\n",
           sizeof(struct Reordered), alignof(struct Reordered),
           offsetof(struct Reordered, b), offsetof(struct Reordered, a),
           offsetof(struct Reordered, c));
    return 0;
}
```

在许多常见 ABI 中，两者分别为 12 和 8 字节，但这不是 C 标准规定的固定结果。重新排列成员有时能减少空间，但字段顺序还可能受二进制协议、持久化格式和公共 ABI 兼容性约束，不能只为节省几个字节随意修改。

## 观察真实进程

先编译并运行配套示例：

```bash
make build/examples/14_memory_layout
./build/examples/14_memory_layout
```

`vmmap` 和 `/proc/<PID>/maps` 需要目标进程仍在运行。由于这个示例很快就会退出，可以先在一个终端中用 LLDB 将它停在断点处：

```bash
lldb build/examples/14_memory_layout
(lldb) breakpoint set --name inspect_call_frames
(lldb) run
(lldb) process status   # 记下 PID
```

然后在另一个终端中观察该 PID。macOS 可以使用：

```bash
vmmap <PID>
size build/examples/14_memory_layout
otool -l build/examples/14_memory_layout
```

Linux 可以使用：

```bash
cat /proc/<PID>/maps
pmap <PID>
size build/examples/14_memory_layout
readelf -l build/examples/14_memory_layout
```

`vmmap`、`pmap` 和 `/proc/<PID>/maps` 展示运行时映射；`otool` 和 `readelf` 展示可执行文件及其装载信息。二者相关，但不是同一个视角。观察完成后，在 LLDB 中输入 `continue` 让程序结束。

## 与 Python/C 扩展的联系

Python 变量通常保存对象引用，而 CPython 对象本身由运行时在动态内存中管理。后续阅读 Python/C API 时，本章知识会帮助你理解：

- `PyObject *` 为什么是指向对象内存的指针
- 对象结构体布局为什么受 ABI 约束
- 引用计数归零后为什么可以释放对象
- 越界、悬空指针和错误类型转换为什么可能破坏整个 Python 进程
- 大量对象的逻辑大小为什么不等于进程 RSS 的即时变化

## 动手练习

1. 连续运行配套示例三次，记录哪些地址发生变化，并解释 ASLR 能说明什么、不能说明什么。
2. 分别使用 `-O0` 和 `-O2` 编译递归示例，比较地址输出或反汇编结果。说明优化为什么可能改变栈帧。
3. 使用 `vmmap` 或 `/proc/<PID>/maps` 找出可执行代码、可写数据、动态库和栈对应的映射及权限。
4. 使用 `sysconf(_SC_PAGESIZE)` 查询实际页大小，不要在程序中写死 4096。
5. 设计包含 `char`、`short`、`int`、`double` 的结构体，先预测布局，再用 `sizeof`、`alignof` 和 `offsetof` 验证。

完成后，你应该能够解释一次地址输出背后的多种实现因素，而不只是背诵“代码、数据、堆、栈”的固定排列图。
