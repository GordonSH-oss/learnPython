# C 语言系统学习教程

这套材料面向 C 语言零基础学习者，也适合已经会 Python、希望理解内存、编译和 CPython 底层机制的开发者。课程基于 C17，前 20 章主要使用标准库和 POSIX API；第 21 章使用 libcurl 演示第三方 C 库的集成。可以使用 Clang 或 GCC 编译。

## 学完以后你能做什么

- 独立编译、运行和调试多文件 C 程序。
- 正确使用变量、控制流、函数、数组、字符串、指针和结构体。
- 理解栈、堆、地址、生命周期、越界和内存泄漏。
- 使用文件、动态内存和常见数据结构解决实际问题。
- 编写有清晰接口、错误处理和自动测试的小型 C 项目。
- 理解进程、线程、系统调用、文件描述符和虚拟内存等操作系统核心概念。
- 使用 socket 编写网络程序，使用 dlopen 实现插件系统。
- 使用头文件、回调和链接参数集成 libcurl 等第三方库。
- 为后续学习 Python/C API 和 CPython 源码建立基础。

## 环境准备

macOS 检查 Clang：

```bash
clang --version
```

如果没有编译器，安装 Command Line Tools：

```bash
xcode-select --install
```

Linux 可以安装 GCC 或 Clang。进入本目录后运行：

```bash
make examples
make test
```

单独编译一个文件：

```bash
clang -std=c17 -Wall -Wextra -Wpedantic examples/01_hello.c -o build/01_hello
./build/01_hello
```

## 学习路线

| 阶段 | 章节 | 核心问题 | 配套示例 |
| --- | --- | --- | --- |
| 入门 | [01 编译与程序结构](chapters/01-build-and-program.md) | 源代码如何变成程序？ | `01_hello.c` |
| 入门 | [02 类型、变量与运算](chapters/02-types-and-operators.md) | 数据在 C 中如何表示？ | `02_types.c` |
| 入门 | [03 分支与循环](chapters/03-control-flow.md) | 程序如何作出选择和重复工作？ | `03_control_flow.c` |
| 基础 | [04 函数与作用域](chapters/04-functions.md) | 如何拆分逻辑并传递数据？ | `04_functions.c` |
| 基础 | [05 数组与字符串](chapters/05-arrays-and-strings.md) | 连续数据和文本如何存储？ | `05_arrays_strings.c` |
| 核心 | [06 指针](chapters/06-pointers.md) | 地址、解引用和参数修改是什么？ | `06_pointers.c` |
| 核心 | [07 结构体、枚举与联合体](chapters/07-structs-enums.md) | 如何建立固定字段和多形态数据模型？ | `07_structs.c` |
| 核心 | [08 动态内存](chapters/08-dynamic-memory.md) | 运行时大小未知的数据放在哪里？ | `08_dynamic_memory.c` |
| 工程 | [09 文件与错误处理](chapters/09-files-and-errors.md) | 如何处理外部数据和失败？ | `09_files.c` |
| 工程 | [10 多文件项目与构建](chapters/10-multi-file-projects.md) | 模块如何逐层组装成大型工程？ | `10-multi-file-project/` |
| 进阶 | [11 数据结构与函数指针](chapters/11-data-structures.md) | 如何实现可扩展的数据处理？ | `11_linked_list.c` |
| 进阶 | [12 调试、测试与安全](chapters/12-debugging-testing.md) | 如何发现未定义行为并建立质量保障？ | 全部示例 |
| 系统 | [13 预处理器与位操作](chapters/13-preprocessor-and-bits.md) | 宏、条件编译和位级运算如何工作？ | `13_preprocessor_bits.c` |
| 系统 | [14 内存布局与虚拟内存](chapters/14-memory-layout.md) | 进程地址空间的结构是什么样的？ | `14_memory_layout.c` |
| 系统 | [15 进程与 fork/exec](chapters/15-processes.md) | 如何创建和管理子进程？ | `15_processes.c` |
| 系统 | [16 线程与并发](chapters/16-threads.md) | 如何实现多线程和同步？ | `16_threads.c` |
| 系统 | [17 系统调用与文件描述符](chapters/17-syscalls-and-fd.md) | stdio 之下发生了什么？ | `17_syscalls_fd.c` |
| 系统 | [18 共享库与动态链接](chapters/18-shared-libraries.md) | .so/.dylib 如何加载和链接？ | `18_shared_libs.c` |
| 系统 | [19 Socket 网络编程](chapters/19-socket-programming.md) | 如何用 C 进行网络通信？ | `19_socket.c` |
| 系统 | [20 Unix/POSIX API 实战](chapters/20-unix-posix-api-practice.md) | 如何在 Apple Silicon Mac 上查询和操作 Unix 系统资源？ | `20_unix_api.c` |
| 工程 | [21 第三方库与 libcurl HTTP 客户端](chapters/21-external-libraries-http.md) | 如何引入第三方 C 库并处理 HTTP？ | `21_http_client.c` |
| 进阶 | [22 用 C 模拟面向对象](chapters/22-object-oriented-programming-in-c.md) | 数据和逻辑分离时，如何实现封装、继承与多态？ | `22_oop_in_c.c` |

建议每章按这个顺序学习：读章节、手敲示例、先预测输出、编译运行、完成练习、查看答案、修改输入再次验证。

## 练习

练习位于 [`exercises`](exercises)，参考答案位于 [`solutions`](solutions)。不要一开始就看答案。

| 练习 | 训练内容 | 难度 |
| --- | --- | --- |
| `01_temperature.c` | 输入、浮点数、公式 | 入门 |
| `02_fizzbuzz.c` | 分支、循环、取模 | 入门 |
| `03_statistics.c` | 数组、函数、返回值 | 基础 |
| `04_string_tools.c` | 字符串、指针、字符分类 | 基础 |
| `05_student_records.c` | 结构体、排序、查找 | 核心 |
| `06_dynamic_vector.c` | 动态内存、容量扩展 | 进阶 |
| `07_word_count.c` | 文件、错误处理、文本统计 | 综合 |
| `08_bitflags.c` | 位运算、掩码、标志位操作 | 系统 |
| `09_memexplorer.c` | 内存段地址、栈堆增长方向验证 | 系统 |
| `10_minishell.c` | fork/exec/wait 实现迷你 shell | 系统 |
| `11_thread_pool.c` | 线程池、互斥锁、条件变量 | 系统 |
| `12_file_copy.c` | 纯系统调用复制文件 | 系统 |
| `13_plugin_loader.c` | dlopen/dlsym 动态插件加载 | 系统 |
| `14_chat_server.c` | fork 并发 TCP 聊天服务器 | 综合 |

验证参考答案：

```bash
make test
```

## 编译警告是课程的一部分

本课程始终开启：

```text
-std=c17 -Wall -Wextra -Wpedantic
```

警告通常意味着类型转换、未初始化变量、格式化参数或接口设计存在风险。不要通过关闭警告来“修复”代码。

## 快速命令

```bash
make help        # 查看命令
make examples    # 编译全部示例
make exercises   # 编译练习起始文件
make solutions   # 编译参考答案
make test        # 编译并运行自动检查
make sanitize    # 使用 AddressSanitizer/UBSan 检查示例
make clean       # 删除构建产物
```

批量运行默认跳过需要创建本地监听端口的 Socket 集成示例，以适应受限 CI 或沙箱环境。在允许本地网络的环境中显式运行：

```bash
RUN_NETWORK_EXAMPLES=1 bash scripts/run_examples.sh
```

## C 与 Python 的关键差异

| Python | C |
| --- | --- |
| 变量引用对象，类型通常在运行时确定 | 变量有固定类型和存储大小 |
| 自动管理对象内存 | 程序员必须管理动态内存 |
| 列表会自动扩容并保存对象引用 | 数组长度固定并连续存储元素 |
| 异常传播错误 | 常用返回值、`errno` 或输出参数表示错误 |
| 运行 `.py` 文件 | 源文件先预处理、编译、汇编、链接 |

不要把 C 当作“语法更少的 Python”。C 的核心是明确的数据布局、所有权、生命周期和机器级执行成本。
