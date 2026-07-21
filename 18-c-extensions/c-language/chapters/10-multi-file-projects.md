# 10 多文件项目与构建

## 学习目标

完成本章后，你应能：

- 解释 C 的 `#include` 为什么不等同于 Python 的 `import`。
- 使用头文件定义模块接口，使用源文件隐藏实现。
- 理解翻译单元、目标文件、符号和链接之间的关系。
- 把多个模块逐层组装成可执行程序或静态库。
- 设计清晰的目录、依赖方向和公共接口。
- 使用 Makefile 描述依赖并进行增量构建。

本章回答一个工程问题：单个 `.c` 文件如何逐步发展成由几十、几百甚至更多模块组成的程序？

## 从 Python `import` 建立对照

Python 通常在运行时导入模块：

```python
from calculator import add

print(add(2, 3))
```

解释器找到 `calculator.py`，执行模块代码，创建模块对象，再把名称绑定到当前命名空间。

C 没有完全对应的单一机制。大型 C 工程通过几个阶段共同完成“导入和组装”：

```text
头文件声明接口
      ↓ #include
每个 .c 文件分别编译
      ↓
生成多个 .o 目标文件
      ↓
链接器解析符号并组装
      ↓
可执行文件或库
```

可以先用下面的近似对照建立直觉：

| Python | C 中接近的机制 |
| --- | --- |
| `.py` 模块 | 一组 `.h` 和 `.c` 文件 |
| `import` | `#include` 提供声明，链接器连接实现 |
| 模块公开名称 | 头文件中的公共声明 |
| `_private_name` 约定 | 不写进公共头文件，并用 `static` 限制可见性 |
| package | 目录、库和构建目标 |
| 解释器查找并加载模块 | 编译器搜索头文件，链接器搜索目标文件或库 |

这个对照不能机械套用。最重要的区别是：`#include` 只处理源代码层面的声明可见性，不会自动找到或载入函数实现。

## 一个模块由接口和实现组成

本章示例把计算器拆成三个文件：

```text
examples/
├── calculator.h       公共接口
├── calculator.c       接口实现
└── 10_multi_file.c    程序入口和调用者
```

`calculator.h` 告诉调用者可以使用什么：

```c
#ifndef CALCULATOR_H
#define CALCULATOR_H

#include <stdbool.h>

double calculator_add(double left, double right);
bool calculator_divide(double numerator, double denominator, double *result);

#endif
```

`calculator.c` 提供这些函数的定义：

```c
#include "calculator.h"

double calculator_add(double left, double right) {
    return left + right;
}

bool calculator_divide(double numerator, double denominator, double *result) {
    if (denominator == 0.0 || result == 0) return false;
    *result = numerator / denominator;
    return true;
}
```

调用者只依赖头文件中的契约：

```c
#include "calculator.h"
#include <stdio.h>

int main(void) {
    printf("2 + 3 = %.1f\n", calculator_add(2.0, 3.0));
    return 0;
}
```

模块边界的核心原则是：头文件描述调用者必须知道的内容，源文件保留实现细节。

## `#include` 实际做了什么

预处理器遇到：

```c
#include "calculator.h"
```

会把头文件内容展开到当前 `.c` 文件中。它更接近文本包含，而不是 Python 模块加载。

可以查看预处理结果：

```bash
clang -E examples/10_multi_file.c
```

两种包含形式的常见含义是：

- `#include <stdio.h>`：从实现配置的系统头文件路径中查找。
- `#include "calculator.h"`：通常先从当前文件附近或项目配置的路径中查找。

项目头文件不一定与源文件在同一目录。可以使用 `-I` 添加搜索路径：

```bash
clang -Iinclude -c src/main.c -o build/main.o
```

`#include` 让编译器看到 `calculator_add` 的声明，因此编译器可以检查参数和返回类型。但此时函数体仍可能不在当前翻译单元中。

## 翻译单元：C 的独立编译边界

一个 `.c` 文件经过预处理并展开所有头文件后，形成一个翻译单元。编译器通常逐个翻译单元独立编译：

```bash
clang -std=c17 -Wall -Wextra -Wpedantic \
  -c examples/calculator.c -o build/calculator.o

clang -std=c17 -Wall -Wextra -Wpedantic \
  -c examples/10_multi_file.c -o build/main.o
```

`-c` 表示只编译，不执行最终链接。生成的 `.o` 目标文件包含机器代码、数据以及尚待解析的符号信息。

```text
calculator.c + calculator.h -> calculator.o
main.c       + calculator.h -> main.o
```

每个调用者都从同一个头文件获得接口声明，模块实现则只编译一次。这是 C 工程能够增量构建的基础：修改一个 `.c` 文件时，通常只需重新生成对应的 `.o`，然后重新链接。

## 链接器负责组装实现

编译完成后，链接器把目标文件组合起来：

```bash
clang build/main.o build/calculator.o -o build/calculator_demo
```

`main.o` 中记录了“需要 `calculator_add`”，`calculator.o` 中记录了“这里定义了 `calculator_add`”。链接器解析这种引用并生成最终程序。

```text
main.o -------------------+
  需要 calculator_add     |
                           +--> calculator_demo
calculator.o -------------+
  定义 calculator_add
```

因此，多文件 C 程序必须同时满足两个条件：

1. 编译时，调用点能看到正确声明。
2. 链接时，链接器能找到且只能找到一个相应外部定义。

常见故障正好对应这两个阶段：

- 缺少声明或声明不匹配：编译错误或警告。
- 有声明但没有把实现加入链接：`undefined reference` 或 `symbol(s) not found`。
- 多个目标文件定义同一个外部符号：重复符号错误。

头文件不是实现的容器，链接器也不会根据头文件名称自动猜测要加入哪个 `.c` 文件。

## 声明、定义与链接属性

声明告诉编译器名称和类型，定义则真正提供函数体或对象存储：

```c
int parse_number(const char *text);  // 函数声明

int parse_number(const char *text) { // 函数定义
    /* ... */
}
```

普通非 `static` 函数默认具有外部链接，可以被其他翻译单元引用。只供当前 `.c` 文件使用的辅助函数应声明为 `static`：

```c
static bool denominator_is_valid(double value) {
    return value != 0.0;
}
```

这相当于建立真正的翻译单元私有边界，而不只是依赖命名约定。它还能避免不同模块的内部辅助函数发生符号冲突。

全局变量需要更谨慎。头文件若要声明一个由某个 `.c` 文件定义的全局对象，使用 `extern`：

```c
// metrics.h
extern unsigned long request_count;

// metrics.c
unsigned long request_count = 0;
```

不要在头文件中直接写普通全局变量定义，否则每个包含它的翻译单元都可能产生一份定义。更好的设计通常是隐藏状态，通过函数提供访问，而不是暴露可写全局变量。

## 头文件是模块契约

公共头文件通常可以包含：

- 公共类型和常量。
- 函数声明。
- 调用者必须知道的错误语义和所有权规则。
- 必要的依赖头文件。

公共头文件通常不应包含：

- 普通函数定义。
- 私有辅助函数声明。
- 仅实现需要的系统头文件。
- 可修改全局变量定义。
- 要求调用者了解的无关实现细节。

头文件应当自包含：使用者只包含这个头文件时，它仍能被正确编译。如果声明中使用 `bool`，头文件自己应包含 `<stdbool.h>`，而不是要求调用者提前包含。

每个实现文件应先包含自己的头文件：

```c
#include "calculator.h"
```

这样编译器能及时发现头文件声明与实现定义不一致，而不会因为其他头文件碰巧提供了所需类型而隐藏问题。

### Include guard

同一个头文件可能沿不同依赖路径被多次包含。Include guard 确保其内容在一个翻译单元中只展开一次：

```c
#ifndef PROJECT_CALCULATOR_H
#define PROJECT_CALCULATOR_H

/* declarations */

#endif
```

宏名应在项目范围内保持唯一。许多编译器也支持 `#pragma once`，但传统 include guard 是标准工具链中最可移植的写法。

## 从多个模块组装程序

真实项目不会只有一个计算器模块。可以把程序拆成职责明确的层：

```text
app/main.c
    ↓
service/report_service.c
    ↓
domain/statistics.c
    ↓
platform/file_store.c
```

箭头表示上层通过头文件依赖下层接口。各模块分别编译，最后统一链接：

```text
main.c ------------> main.o -----------+
report_service.c --> report_service.o -+
statistics.c ------> statistics.o -----+--> report_app
file_store.c ------> file_store.o -----+
```

大型工程并不是把所有代码互相 `#include`，而是让每个模块暴露小而稳定的接口，并控制依赖方向。

一个常见目录布局是：

```text
project/
├── include/project/       对外公共头文件
│   ├── calculator.h
│   └── report.h
├── src/                   实现文件
│   ├── calculator.c
│   ├── report.c
│   └── report_internal.h  仅 src 内部共享
├── app/
│   └── main.c             可执行程序入口
├── tests/
│   ├── test_calculator.c
│   └── test_report.c
├── third_party/           必要时存放外部依赖
├── Makefile
└── README.md
```

目录名称不是语言规则，可以根据项目调整。真正重要的是明确区分：

- 对外接口与内部实现。
- 产品代码与测试代码。
- 可复用模块与具体程序入口。
- 自己维护的代码与第三方依赖。

大型仓库还可能包含多个库和多个可执行程序，每个构建目标只链接自己需要的模块。

## 控制模块依赖

模块化的目标不是增加文件数量，而是降低修改一处时需要理解和重建的范围。

### 依赖公共接口，不依赖内部文件

调用者应包含公共头文件：

```c
#include <project/calculator.h>
```

不应跨模块包含对方的内部头文件或直接访问其私有状态。否则实现细节一变，许多不相关模块都需要修改。

### 避免循环依赖

如果模块 A 的头文件包含 B，B 的头文件又包含 A，通常说明边界需要重新设计。常见处理方法包括：

- 提取双方共同依赖的类型到更底层模块。
- 让上层负责协调，避免两个同层模块互相调用。
- 头文件只需要指针时使用结构体前置声明，把完整定义留到 `.c` 文件。
- 通过回调函数或接口对象反转依赖。

不要用 include guard 掩盖循环依赖。它只能防止重复展开，不能修复错误的架构方向。

### 减少头文件传播

公共头文件每增加一个 `#include`，都可能把依赖传播给大量翻译单元。只在接口确实需要完整类型时包含对应头文件；仅实现需要的依赖放在 `.c` 文件中。

这样既能降低耦合，也能减少头文件变化引发的大面积重新编译。

## 把模块打包为库

当多个程序共享一组模块时，可以先把目标文件打包为静态库：

```bash
clang -c src/calculator.c -Iinclude -o build/calculator.o
clang -c src/statistics.c -Iinclude -o build/statistics.o
ar rcs build/libproject.a build/calculator.o build/statistics.o

clang app/main.c -Iinclude -Lbuild -lproject -o build/project_app
```

静态库本质上是目标文件的归档。链接器从中取出程序需要的实现，组装进最终可执行文件。

```text
calculator.o --+
statistics.o --+--> libproject.a --+
                                      +--> project_app
main.o -------------------------------+
```

共享库允许多个程序在运行时加载同一库文件，并带来 ABI、版本和部署等额外问题。第 18 章会系统介绍 `.so`、`.dylib`、动态链接和插件加载。

## 构建系统描述组装规则

手动执行编译命令适合学习流程，但大型工程需要构建系统回答：

- 有哪些构建目标？
- 每个目标由哪些源文件和库组成？
- 头文件或源文件变化后，哪些目标需要重建？
- 编译选项、平台差异和外部依赖是什么？
- 测试、安装和打包如何执行？

本教程使用 Make。下面是计算器示例的简化规则：

```make
CC := clang
CFLAGS := -std=c17 -Wall -Wextra -Wpedantic

build/calculator.o: examples/calculator.c examples/calculator.h
	$(CC) $(CFLAGS) -c examples/calculator.c -o build/calculator.o

build/main.o: examples/10_multi_file.c examples/calculator.h
	$(CC) $(CFLAGS) -c examples/10_multi_file.c -o build/main.o

build/calculator_demo: build/main.o build/calculator.o
	$(CC) build/main.o build/calculator.o -o build/calculator_demo
```

每条规则由三部分组成：

```text
目标: 依赖
<Tab>生成目标的命令
```

如果只修改 `calculator.c`，Make 可以只重新编译 `calculator.o`，然后重新链接程序。如果修改 `calculator.h`，两个 `.c` 文件的编译结果都可能受影响，因此两个目标文件都应重建。

大型 Makefile 通常会使用模式规则、自动依赖生成和变量减少重复。更复杂的跨平台项目也常使用 CMake、Meson 或其他工具生成底层构建规则。工具可以变化，但“源文件独立编译成目标文件，再按依赖组装”的模型不变。

## 编译期依赖、链接期依赖和运行期依赖

排查大型项目问题时，要先判断依赖发生在哪个阶段：

| 阶段 | 需要找到什么 | 常见配置 | 常见错误 |
| --- | --- | --- | --- |
| 编译期 | 头文件和声明 | `-Iinclude` | 找不到头文件、未知类型 |
| 链接期 | 目标文件或库中的定义 | `.o`、`-L`、`-l` | 未定义符号、重复符号 |
| 运行期 | 共享库、配置和数据文件 | rpath、环境或安装路径 | 共享库无法加载 |

Python 的一次 `import` 经常替开发者同时处理名称查找和模块加载；C 把这些责任分散到了预处理器、编译器、链接器、动态加载器和构建系统。理解阶段边界后，错误信息会更容易定位。

## 模块设计检查表

新增一个模块时，检查以下问题：

1. 模块承担的单一职责是什么？
2. 调用者真正需要知道哪些类型和函数？
3. 哪些函数和状态应该留在 `.c` 文件并使用 `static`？
4. 失败如何返回，资源由谁创建和释放？
5. 头文件是否自包含，能否单独被调用者包含？
6. 依赖方向是否清晰，是否产生循环依赖？
7. 构建规则是否准确描述源文件和头文件依赖？
8. 模块能否通过公共接口独立测试？

文件拆分只是表面。真正可扩展的工程依靠稳定接口、受控依赖、隐藏状态以及可重复的构建过程。

## 常见错误

### 直接包含 `.c` 文件

```c
// 不要这样组织普通模块
#include "calculator.c"
```

这会把实现文本复制进调用者，容易产生重复定义，也破坏独立编译。普通模块应包含 `.h`，并把对应 `.c` 编译为独立目标文件。

### 把实现全部写进头文件

普通外部函数若在头文件中定义，多个翻译单元包含后通常会产生重复符号。只有确实理解 `static inline` 等规则时，才在头文件中放函数实现。

### 头文件依赖包含顺序

如果 `report.h` 使用 `size_t`，它自己就应包含提供 `size_t` 的标准头文件。不要要求调用者必须先包含另一个头文件。

### 所有模块共享全局状态

大量可写全局变量会让初始化顺序、并发访问和测试隔离变得困难。优先把状态封装进结构体，并通过明确接口传递上下文。

### 一个头文件暴露整个项目

“总头文件”使用方便，但也可能让所有模块依赖所有内容，导致耦合和编译时间持续增长。对外可以提供便利入口，同时仍应保留职责明确的小接口。

## 检查点

假设 `main.c` 包含 `calculator.h` 并成功编译，但最终链接时报找不到 `calculator_add`。这说明声明已经可见，最可能的问题是 `calculator.c` 没有编译，或生成的 `calculator.o`、对应库没有加入链接命令。

如果只修改 `calculator.c`，通常不需要重新编译 `main.c`；如果修改 `calculator.h` 中的函数声明，所有包含它的翻译单元都可能需要重新编译。

## 动手练习

基于 `calculator` 示例完成以下任务：

1. 增加 `calculator_multiply`，并分别修改头文件、实现文件和调用者。
2. 实现安全除法。除数为零或输出指针为空时返回 `false`，不要返回一个看似有效的计算结果。
3. 增加只在 `calculator.c` 中使用的 `static` 辅助函数，确认调用者无法直接使用它。
4. 分别执行预处理、独立编译和链接命令，观察 `.i`、`.o` 与最终可执行文件的角色。
5. 修改当前 Makefile，让 `calculator.c` 和 `10_multi_file.c` 先分别生成目标文件，再链接成示例程序。连续运行两次 `make`，观察第二次为何不重新编译。
6. 将计算器目标文件打包为 `libcalculator.a`，再让主程序通过 `-L` 和 `-lcalculator` 链接它。

完成后，尝试为一个“学生成绩程序”设计模块图。至少拆分输入解析、成绩统计、报告输出和程序入口，先写每个模块公开的 `.h` 契约，再考虑 `.c` 实现。
