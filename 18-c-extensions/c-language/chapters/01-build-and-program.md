# 01 编译与程序结构

## 学习目标

理解 C 程序从源代码到可执行文件的过程，并能读懂最小程序的入口、语句和返回值。

## 最小程序

查看 `examples/01_hello.c`。操作系统加载可执行文件后，C 运行时先完成必要的进程初始化，再调用 `main`。花括号形成函数体，分号结束一条语句，`return 0` 表示程序成功结束。

```c
#include <stdio.h>

int main(void) {
    printf("Hello, C!\n");
    return 0;
}
```

`#include` 由预处理器处理，它把 `stdio.h` 中与标准输入输出有关的声明提供给当前源文件。`printf` 的实现位于 C 标准库中，链接阶段把调用与实现连接起来。

## 从源文件到程序

```text
hello.c -> 预处理 -> 编译 -> 汇编 -> hello.o -> 链接 -> hello
```

观察中间结果：

```bash
clang -E examples/01_hello.c -o build/01_hello.i
clang -S examples/01_hello.c -o build/01_hello.s
clang -c examples/01_hello.c -o build/01_hello.o
clang build/01_hello.o -o build/01_hello
```

四条命令观察的是不同阶段：

| 阶段 | 输入 | 输出 | 主要工作 |
| --- | --- | --- | --- |
| 预处理 | `.c` | `.i` | 展开头文件、宏和条件编译 |
| 编译 | 预处理后的 C | `.s` | 类型检查、优化并生成汇编 |
| 汇编 | `.s` | `.o` | 生成包含机器码和符号的目标文件 |
| 链接 | `.o` 和库 | 可执行文件 | 解析跨文件符号并生成程序映像 |

运行程序后查看退出状态：

```bash
./build/01_hello
echo $?
```

shell 中 `0` 通常表示成功，非零值表示某种失败。输出内容和退出状态是两个独立的程序接口。

## 编译器诊断

本课程统一启用：

```bash
clang -std=c17 -Wall -Wextra -Wpedantic examples/01_hello.c -o build/01_hello
```

警告不一定阻止生成程序，但经常暴露类型、格式参数或控制流错误。学习阶段应保持零警告，而不是通过删除警告选项隐藏问题。

## 用 Make 管理构建生命周期

真实项目通常不会要求开发者反复手写完整的 `clang` 命令，而是把编译规则记录在 `Makefile` 中。运行 `make 目标名`，就是要求 Make 构建或执行这个目标。

常见目标的职责如下：

| 命令 | 主要作用 | 是否通常生成或删除文件 |
| --- | --- | --- |
| `make all` 或 `make` | 构建项目的默认程序 | 生成目标文件、库或可执行文件 |
| `make test` | 先构建测试程序，再运行测试 | 可能生成测试可执行文件 |
| `make sanitize` | 使用 AddressSanitizer、UndefinedBehaviorSanitizer 等检测器重新构建并运行测试 | 生成带检测代码的程序 |
| `make clean` | 删除构建产物，让下次构建从干净状态开始 | 删除 `build/`、`.o` 等生成文件 |

`clean` 不是编译的反向操作，也不会删除源代码。它只删除可以根据源代码重新生成的文件。

如果连续两次执行 `make all`，第二次可能显示：

```text
make: Nothing to be done for `all'.
```

这表示 `all` 所依赖的目标都存在，而且没有依赖比目标更新，因此不需要重复编译。这是增量构建正常工作的结果，不是错误。

`make test` 没有打印失败信息并返回 shell 提示符，通常表示测试成功。可以继续检查退出状态：

```bash
make test
echo $?
```

退出状态为 `0` 表示 Make 的整个执行链成功；任意编译命令、测试程序或子 Make 返回非零值，目标通常都会失败。

切换普通构建和 sanitizer 构建时，编译选项发生了变化。简单 Makefile 未必能根据选项变化自动判断旧目标文件已经过期，因此常用的完整检查流程是：

```bash
make clean
make test
make sanitize
make clean
make all
```

最后两步用于移除带 sanitizer 插桩的构建产物，并恢复普通版本。更大型的工程通常为不同配置使用不同构建目录，例如 `build/debug/`、`build/release/` 和 `build/sanitize/`，避免配置互相污染。

## 常见错误

- `expected ';'`：上一条语句可能缺少分号。
- `implicit declaration`：函数声明不可见，通常是缺少头文件。
- `undefined reference` 或 `symbol(s) not found`：链接器找不到函数定义。
- `No such file or directory`：当前目录或路径不正确。

## 检查点

编译器错误和程序运行错误有什么区别？前者发生在生成可执行文件之前；后者发生在程序已经启动之后。

链接错误又处于哪一阶段？编译器已经生成目标文件，但链接器无法为某个外部符号找到定义。

## 动手练习

1. 修改示例，让它输出姓名和两行学习目标。观察删除 `\n` 后终端输出的变化。
2. 分别删除 `stdio.h`、把 `printf` 拼错、删除右花括号，记录每种错误出现在哪个阶段。
3. 把 `return 0` 改成 `return 7`，运行后用 `echo $?` 验证退出状态。
