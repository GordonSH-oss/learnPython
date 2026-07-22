# 10 多文件项目与构建

## 学习目标

完成本章后，你应能：

- 解释 C 的 `#include` 为什么不等同于 Python 的 `import`。
- 使用头文件定义模块接口，使用源文件实现并隐藏细节。
- 理解翻译单元、目标文件、符号、静态库和可执行文件的关系。
- 读懂 `examples/10-multi-file-project` 的模块和依赖方向。
- 使用 Makefile 维护编译、归档、链接、测试和增量构建链。
- 根据职责和依赖方向组织更大型的 C 工程。

本章以一个可持久化的任务管理器为案例。它不是把几个 `.c` 文件放在同一目录后一次性编译，而是把领域模型、集合操作、文件存储、命令行入口和测试拆成独立模块，再通过静态库和链接器逐步组装。

## 从 Python `import` 建立对照

Python 通常在运行时导入模块：

```python
from task_list import TaskList

tasks = TaskList()
```

解释器查找并执行模块，创建模块对象，再把名称绑定到当前命名空间。

C 没有一个完全对应 `import` 的单一机制。大型 C 工程通过几个阶段共同完成模块组合：

```text
头文件声明接口
      ↓ #include
每个 .c 文件独立编译
      ↓
生成多个 .o 目标文件
      ↓
目标文件归档为静态库，或直接参与链接
      ↓
链接器解析符号并生成程序
```

可以先用下面的近似对照建立直觉：

| Python | C 中接近的机制 |
| --- | --- |
| `.py` 模块 | 一组 `.h` 和 `.c` 文件 |
| `import` | `#include` 提供声明，链接器连接实现 |
| 模块公开名称 | 公共头文件中的声明 |
| `_private_name` 约定 | 不写入公共头文件，并用 `static` 限制符号可见性 |
| package | 目录、静态库、共享库和构建目标 |
| 测试导入业务模块 | 测试程序链接同一个业务库 |

最重要的区别是：`#include` 只让声明对当前翻译单元可见，不会自动编译或加载对应实现。

## 先运行案例

进入案例目录：

```bash
cd examples/10-multi-file-project
make
make test
```

构建后会得到：

```text
build/libtasker.a   由业务模块组成的静态库
build/tasker        命令行程序
build/test_tasker   测试程序
```

使用 `TASKER_FILE` 可以把测试数据写到指定位置，避免在源码目录生成 `tasks.tsv`：

```bash
TASKER_FILE=/tmp/tasks.tsv build/tasker add "learn headers"
TASKER_FILE=/tmp/tasks.tsv build/tasker add "learn linking"
TASKER_FILE=/tmp/tasks.tsv build/tasker list
TASKER_FILE=/tmp/tasks.tsv build/tasker done 1
TASKER_FILE=/tmp/tasks.tsv build/tasker remove 2
```

CLI 支持四条命令：

| 命令 | 行为 |
| --- | --- |
| `add <title>` | 创建任务并分配递增 ID |
| `list` | 输出所有任务及完成状态 |
| `done <id>` | 把指定任务标记为完成 |
| `remove <id>` | 删除指定任务 |

如果没有设置 `TASKER_FILE`，程序默认读写当前工作目录下的 `tasks.tsv`。

## 项目目录就是模块地图

案例的源码结构如下：

```text
examples/10-multi-file-project/
├── include/
│   ├── task.h
│   ├── task_list.h
│   └── task_store.h
├── src/
│   ├── task.c
│   ├── task_list.c
│   └── task_store.c
├── app/
│   └── main.c
├── tests/
│   └── test_task_list.c
├── Makefile
└── README.md
```

各目录承担不同职责：

- `include/`：调用者可依赖的公共契约。
- `src/`：契约的实现和内部辅助逻辑。
- `app/`：解析命令行并组装模块的程序入口。
- `tests/`：通过公共接口验证业务模块和存储模块。
- `Makefile`：描述从源码到目标文件、静态库、程序和测试的构建图。

这比“每个功能随便放一个文件”更重要：目录结构直接表达了公共接口、实现、应用入口和测试之间的边界。

## 三个业务模块

### `task`：领域实体

`include/task.h` 定义任务的数据结构和最基础操作：

```c
#define TASK_TITLE_CAPACITY 128

typedef struct {
    unsigned long id;
    bool completed;
    char title[TASK_TITLE_CAPACITY];
} Task;

bool task_create(Task *task, unsigned long id, const char *title);
void task_complete(Task *task);
```

`src/task.c` 实现创建和完成规则。`task_create` 会拒绝以下输入：

- 输出指针为 `NULL`。
- 标题指针为 `NULL`。
- 标题为空字符串。
- 标题长度达到或超过 `TASK_TITLE_CAPACITY`。

创建成功后，函数复制标题、保存 ID，并把完成状态初始化为 `false`。

这个模块不知道任务列表、文件格式或命令行参数。它只维护单个 `Task` 的不变量。

### `task_list`：集合和业务操作

`include/task_list.h` 包含 `task.h`，因为 `TaskList` 的公开布局直接使用了 `Task`：

```c
#define TASK_LIST_CAPACITY 100

typedef struct {
    Task items[TASK_LIST_CAPACITY];
    size_t count;
    unsigned long next_id;
} TaskList;
```

它公开初始化、增加、查找、完成和删除操作：

```c
void task_list_init(TaskList *list);
bool task_list_add(TaskList *list, const char *title, Task **added_task);
Task *task_list_find(TaskList *list, unsigned long id);
bool task_list_complete(TaskList *list, unsigned long id);
bool task_list_remove(TaskList *list, unsigned long id);
```

`src/task_list.c` 通过 `task_create` 创建元素，通过 `task_complete` 改变状态。它依赖 `task` 模块，而 `task` 不反向依赖任务列表：

```text
task_list -> task
```

`task_list_add` 的 `added_task` 是可选输出参数。调用者需要新任务时传入 `Task **`，不需要时传 `NULL`。列表容量固定为 100；达到容量后增加操作返回 `false`。

删除任务时，后续元素会向前移动一位，保持数组连续。任务 ID 不会因为删除而重新编号，`next_id` 也不会回退。

### `task_store`：文件持久化

`include/task_store.h` 公开加载和保存接口：

```c
bool task_store_load(const char *path, TaskList *list);
bool task_store_save(const char *path, const TaskList *list);
```

因为接口直接读写 `TaskList`，头文件包含 `task_list.h`：

```text
task_store -> task_list -> task
```

`src/task_store.c` 使用标准 I/O 把任务保存为制表符分隔文本：

```text
1<Tab>0<Tab>learn headers
2<Tab>1<Tab>learn linking
```

三列依次是任务 ID、完成状态和标题。加载时，模块还会根据现有最大 ID 恢复 `next_id`。

当前实现只要 `fopen(path, "r")` 失败，就把结果视为空任务列表并返回成功。这包括文件不存在，也包括部分权限或路径错误；因此它目前不能向调用者区分“首次运行没有数据文件”和“文件打开失败”。成功打开文件后，如果记录格式错误、标题过长、记录过多，或者读取、关闭失败，函数返回 `false`。保存时无法创建或写入文件也会返回 `false`。

`remove_line_ending` 只在 `task_store.c` 内部使用，因此声明为 `static`：

```c
static void remove_line_ending(char *text) {
    text[strcspn(text, "\r\n")] = '\0';
}
```

其他翻译单元无法引用这个符号。它属于存储模块的实现细节，不应出现在公共头文件中。

## `main.c` 是模块组装点

`app/main.c` 同时包含列表和存储接口：

```c
#include "task_list.h"
#include "task_store.h"
```

程序入口负责：

1. 解析 `TASKER_FILE` 和命令行参数。
2. 调用 `task_store_load` 恢复任务列表。
3. 根据 `add`、`list`、`done` 或 `remove` 调用对应业务函数。
4. 数据发生变化时调用 `task_store_save`。
5. 把错误转换成终端消息和进程退出状态。

```text
命令行参数
    ↓
app/main.c
    ├── task_list_add / complete / remove
    └── task_store_load / save
             ↓
          tasks.tsv
```

入口层只负责协调。任务标题是否合法由 `task` 判断，列表容量和 ID 由 `task_list` 管理，文件格式由 `task_store` 管理。这样，同一业务模块可以被另一个 CLI、图形界面或网络服务复用。

`main.c` 中的 `print_usage`、`parse_id` 和 `print_tasks` 都声明为 `static`。这些函数只服务于当前命令行入口，不属于 `libtasker.a` 的公共能力。

## `#include` 与翻译单元

预处理器遇到：

```c
#include "task_list.h"
```

会把头文件内容展开到当前 `.c` 文件中。它更接近文本包含，而不是 Python 模块加载。

案例通过 Makefile 设置：

```make
CPPFLAGS ?= -Iinclude
```

因此 `src/task_list.c`、`app/main.c` 和测试代码都可以直接写 `#include "task_list.h"`。可以查看某个源文件的预处理结果：

```bash
clang -Iinclude -E src/task_list.c
```

一个 `.c` 文件经过预处理并展开头文件后形成一个翻译单元。案例共有五个会被独立编译的翻译单元：

```text
src/task.c
src/task_list.c
src/task_store.c
app/main.c
tests/test_task_list.c
```

每个翻译单元只需看见它使用的声明，不需要看见其他模块的函数体。

## 从 `.c` 到 `.o`

Makefile 使用模式规则编译 `src/` 下的实现：

```make
$(BUILD)/src/%.o: src/%.c
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) $(CFLAGS) -MMD -MP -c $< -o $@
```

其中：

- `$@` 表示当前目标文件，例如 `build/src/task.o`。
- `$<` 表示第一个依赖文件，例如 `src/task.c`。
- `-Iinclude` 设置公共头文件搜索路径。
- `-c` 只编译，不执行最终链接。
- `-MMD -MP` 生成头文件依赖文件。

三份实现分别变成目标文件：

```text
src/task.c       -> build/src/task.o
src/task_list.c  -> build/src/task_list.o
src/task_store.c -> build/src/task_store.o
```

`app/main.c` 和测试也分别生成自己的目标文件：

```text
app/main.c             -> build/app/main.o
tests/test_task_list.c -> build/tests/test_task_list.o
```

目标文件包含机器代码、数据、已定义符号以及尚待链接器解析的外部符号。

## 把业务模块归档为静态库

Makefile 先收集业务源文件和目标文件：

```make
LIB_SOURCES := src/task.c src/task_list.c src/task_store.c
LIB_OBJECTS := $(patsubst src/%.c,$(BUILD)/src/%.o,$(LIB_SOURCES))
LIBRARY := $(BUILD)/libtasker.a
```

然后使用 `ar` 创建静态库：

```make
$(LIBRARY): $(LIB_OBJECTS)
	@mkdir -p $(@D)
	$(AR) $(ARFLAGS) $@ $^
```

`ARFLAGS := rcs` 表示替换或加入成员、必要时创建归档，并建立符号索引。`$^` 表示规则中的全部依赖目标文件。

```text
task.o -------+
task_list.o --+--> libtasker.a
task_store.o -+
```

静态库不是一个可独立运行的程序，而是一组目标文件的归档。它提供任务领域和存储能力，但没有 `main` 入口。

## 分别链接应用和测试

CLI 使用自己的入口目标文件链接静态库：

```make
$(APP): $(BUILD)/app/main.o $(LIBRARY)
	$(CC) $(CFLAGS) $< -L$(BUILD) -ltasker -o $@
```

`-L$(BUILD)` 添加库搜索目录，`-ltasker` 查找名为 `libtasker.a` 或相应共享库的文件。

```text
main.o + libtasker.a -> build/tasker
```

测试程序使用另一个入口链接同一静态库：

```make
$(TEST): $(BUILD)/tests/test_task_list.o $(LIBRARY)
	$(CC) $(CFLAGS) $< -L$(BUILD) -ltasker -o $@
```

```text
test_task_list.o + libtasker.a -> build/test_tasker
```

应用和测试共享完全相同的业务实现。测试不需要复制 `task_list.c` 或包含任何 `.c` 文件，只需调用公共接口并链接静态库。

## 链接器如何解析符号

例如，`main.o` 中包含对 `task_list_add` 和 `task_store_save` 的未解析引用；`libtasker.a` 中的 `task_list.o` 和 `task_store.o` 提供对应定义。链接器从静态库取出所需目标文件，生成最终程序。

多文件 C 程序必须同时满足：

1. 编译时，调用点能看到正确声明。
2. 链接时，链接器能找到且只能找到一个相应外部定义。

常见故障正好对应不同阶段：

- 缺少头文件或声明不可见：编译错误。
- 声明与定义签名不一致：编译错误、警告或未定义行为风险。
- 有声明但实现目标文件或库没有参与链接：未定义符号。
- 多个目标文件定义同一个外部符号：重复符号。

头文件不会告诉链接器应自动加入哪个 `.c` 文件；这个关系必须由 Makefile 等构建系统明确描述。

## 头文件是模块契约

案例中的头文件都使用 include guard：

```c
#ifndef TASKER_TASK_H
#define TASKER_TASK_H

/* declarations */

#endif
```

头文件还遵守自包含原则。例如 `task.h` 的接口使用 `bool`，因此自己包含 `<stdbool.h>`；`task_list.h` 的公开结构使用 `size_t`，因此包含 `<stddef.h>`。调用者不需要猜测包含顺序。

公共头文件适合包含：

- 调用者必须知道的结构体和类型。
- 容量等公共常量。
- 函数声明及其输入输出契约。
- 声明所必需的依赖头文件。

公共头文件通常不应包含：

- 普通函数定义。
- 仅实现使用的辅助函数声明。
- 仅 `.c` 文件需要的系统头文件。
- 可修改全局变量定义。

每个实现文件首先包含自己的公共头文件。例如 `src/task.c` 第一行是：

```c
#include "task.h"
```

这样编译器可以直接检查实现是否与公开声明一致。

## 公共依赖如何传播

案例的头文件依赖形成单向链：

```text
task_store.h -> task_list.h -> task.h
```

这是因为：

- `TaskList` 的公开结构中包含 `Task` 数组，所以 `task_list.h` 需要完整的 `Task` 定义。
- `task_store.h` 的函数签名使用 `TaskList *`，当前实现选择直接包含 `task_list.h`。

`app/main.c` 同时包含 `task_list.h` 和 `task_store.h`。其中前者从严格编译角度可能已被后者间接包含，但显式包含自己直接使用的接口可以让依赖意图更清楚。

项目中没有反向依赖：`task` 不知道 `task_list`，`task_list` 不知道文件存储，存储模块也不知道 CLI。单向依赖减少了循环包含和模块相互牵制。

## 自动维护头文件依赖

只写 `.o: .c` 规则并不充分。假设修改 `include/task.h`，那么直接或间接包含它的 `task.o`、`task_list.o`、`task_store.o`、`main.o` 和测试目标都可能需要重新编译。

案例在每条编译命令中使用：

```text
-MMD -MP
```

编译器会生成与目标文件对应的 `.d` 文件，其中记录真实头文件依赖。Makefile 最后加载它们：

```make
-include $(LIB_OBJECTS:.o=.d) \
         $(BUILD)/app/main.d \
         $(BUILD)/tests/test_task_list.d
```

- `-MMD` 生成用户头文件依赖，不把系统头文件全部写入依赖图。
- `-MP` 为头文件生成空规则，降低头文件删除或重命名时的构建错误干扰。
- `-include` 在依赖文件首次尚不存在时不会让 Make 失败。

因此：

- 修改 `src/task.c`：只重新生成 `task.o`，再更新静态库并重新链接。
- 修改 `app/main.c`：只重新生成 `main.o`，再重新链接 CLI。
- 修改 `include/task.h`：所有直接或间接依赖它的翻译单元都会重新编译。
- 什么都不修改再次执行 `make`：不会重复构建。

这就是大型 C 工程增量构建的基础。

## 测试也是构建图的一部分

`tests/test_task_list.c` 使用标准 `assert` 验证三组行为：

- 增加、完成和删除任务。
- 拒绝空标题和超长标题。
- 保存后重新加载，数据和 `next_id` 保持一致。

Makefile 的测试目标先构建测试程序，再运行它：

```make
test: $(TEST)
	$(TEST)
```

执行：

```bash
make test
```

测试文件包含公共头文件并链接 `libtasker.a`，因此能够从模块使用者的角度验证真实接口。测试入口与产品入口分离，但共用业务库。

## 完整构建链

案例的依赖图可以概括为：

```text
include/task.h
      ↓
src/task.c ---------> task.o -----------+
                                          |
include/task_list.h                       |
      ↓                                   |
src/task_list.c ----> task_list.o --------+--> libtasker.a
                                          |
include/task_store.h                      |
      ↓                                   |
src/task_store.c ---> task_store.o -------+
                                               |
                    +--------------------------+------------------+
                    |                                             |
app/main.c ------> main.o                              test_task_list.c
                    |                                             ↓
                    + libtasker.a                     test_task_list.o
                    ↓                                             |
               build/tasker                            + libtasker.a
                                                                  ↓
                                                       build/test_tasker
```

构建系统管理的是一张依赖图，而不只是顺序执行的一组 shell 命令。只有目标依赖发生变化时，对应规则才需要重新执行。

## 根 Makefile 如何调度多个项目

包含多个独立练习项目时，可以用一个根 Makefile 统一调用各项目自己的 Makefile：

```make
PROJECTS := student-manager expense-tracker text-analyzer

all:
	@for project in $(PROJECTS); do \
		$(MAKE) -C $$project all || exit 1; \
	done
```

这里不是 Make 自动扫描磁盘并猜测哪些目录是项目。`PROJECTS` 明确列出了项目及其顺序，shell 的 `for` 循环按顺序逐个调度：

```text
根 Makefile
    -> student-manager/Makefile 的 all
    -> expense-tracker/Makefile 的 all
    -> text-analyzer/Makefile 的 all
```

每一部分都有明确职责：

- `$(MAKE)` 调用当前 Make 实现，并把并行参数等构建上下文传给子 Make，比直接写 `make` 更可靠。
- `-C $$project` 让子 Make 先进入项目目录，再读取该目录中的 `Makefile`。
- Make 先把 `$$` 转义为一个 `$`，shell 最终看到 `$project` 并读取循环变量。
- 行首的 `@` 只隐藏命令本身，命令产生的输出仍然可见。
- `|| exit 1` 表示任一子项目失败后立即停止，避免根目标把部分成功误报为全部成功。

根 Makefile 只负责“有哪些项目、对每个项目执行什么目标”；子 Makefile 才负责“这个项目有哪些源文件、怎样编译和链接”。如果新增项目目录却没有加入 `PROJECTS`，根 Makefile 不会自动构建它。也可以用通配符发现目录，但显式列表更容易控制顺序、排除非项目目录并审查变更。

需要区分两种“顺序”：上面的 shell 循环确实顺序调用子项目，但每个子 Make 内部仍按依赖图决定规则。Makefile 的书写顺序不是普遍的执行顺序；前置依赖、时间戳和 `-j` 并行选项共同决定真正执行哪些命令。

## 一条编译命令与独立目标文件

小项目可以在一条命令中同时列出全部源文件：

```make
build/student-manager: app/main.c src/student.c src/student_registry.c
	$(CC) $(CFLAGS) -Iinclude $^ -o $@
```

编译器驱动会分别处理各个 `.c` 翻译单元，再调用链接器生成一个可执行文件。从工具链角度看仍然经历了编译和链接，但从这个 Makefile 的依赖图看只有一个最终目标：任何一个源文件变化，整条命令都会重新运行。

项目变大后，通常把每个 `.c` 独立编译成 `.o`：

```text
main.c -> main.o --------+
student.c -> student.o --+-> student-manager
registry.c -> registry.o +
```

这样修改 `student.c` 时只需重建 `student.o`，然后重新链接；互不依赖的目标文件还可以通过 `make -j` 并行编译。代价是 Makefile 规则和头文件依赖管理更复杂，因此小型学习项目使用单条命令并没有错，只是它的增量构建粒度较粗。

## 从案例扩展到大型工程

更大的项目仍然使用相同模型，只是会包含更多库和入口：

```text
project/
├── include/project/       对外公共头文件
├── src/domain/            领域模型
├── src/storage/           文件或数据库适配
├── src/service/           跨模块业务流程
├── app/cli/               CLI 入口
├── app/server/            服务端入口
├── tests/unit/
├── tests/integration/
├── third_party/
└── Makefile
```

CLI 和服务器可以链接同一批领域库；单元测试和集成测试可以使用不同入口，但不复制产品实现。

### 公共、内部与文件私有接口

大型项目的 `include/` 确实可能包含很多文件，但不应该把所有函数都暴露进去。可以按可见范围分成三层：

| 范围 | 常见位置或写法 | 谁可以使用 |
| --- | --- | --- |
| 公共接口 | `include/project/module.h` | 应用、测试、其他库和外部调用者 |
| 项目内部接口 | `src/module/module_internal.h` | 同一模块的多个实现文件 |
| 文件私有实现 | `.c` 中的 `static` 函数和对象 | 当前翻译单元 |

只有需要跨翻译单元调用的声明才需要放进头文件。某个 `.c` 文件如果只提供私有辅助逻辑，可以没有同名公共头文件；一个稳定的公共头文件也可以由多个 `.c` 文件共同实现。不要机械地要求每个 `.c` 必须对应一个 `.h`。

头文件数量多并不可怕，失控的依赖才可怕。公共头文件应按模块组织并保持小而自包含，避免一个“万能头文件”包含全项目接口，因为它会扩大耦合和重新编译范围。

### 用不透明类型隐藏结构布局

如果调用者只需要持有对象指针，而不应直接访问字段，可以在公共头文件中只做前向声明：

```c
typedef struct StudentRegistry StudentRegistry;

StudentRegistry *student_registry_create(void);
void student_registry_destroy(StudentRegistry *registry);
```

完整定义留在 `.c` 或内部头文件中：

```c
struct StudentRegistry {
    Student *items;
    size_t count;
    size_t capacity;
};
```

公共接口改变内部字段时，调用者不需要了解实现细节。不完整类型可以用于声明指针，但不能按值定义对象、访问成员或执行 `sizeof(StudentRegistry)`；这些操作需要编译器看到完整结构定义。

这种设计称为不透明类型或 opaque struct。它能加强模块边界，但对象通常需要通过创建和销毁函数管理，还要明确内存所有权和失败处理。

大型工程设计时应关注：

1. 每个模块承担什么单一职责？
2. 调用者真正需要知道哪些类型和函数？
3. 哪些函数应使用 `static` 留在当前翻译单元？
4. 依赖是否保持单向，是否出现循环依赖？
5. 状态和资源由谁创建、修改和释放？
6. 每个可执行程序需要链接哪些库？
7. 头文件变化后，构建系统能否准确重建受影响目标？
8. 模块能否通过公共接口独立测试？

文件数量不是模块化程度的指标。真正可扩展的工程依靠稳定接口、受控依赖、隐藏实现和可重复构建。

## 编译期、链接期和运行期依赖

排查问题时，先判断依赖发生在哪个阶段：

| 阶段 | 案例中需要找到什么 | 配置 | 常见错误 |
| --- | --- | --- | --- |
| 编译期 | `task.h` 等头文件 | `-Iinclude` | 找不到头文件、未知类型 |
| 归档期 | 三个业务目标文件 | `ar rcs` | 静态库缺少实现 |
| 链接期 | `libtasker.a` 中的符号 | `-Lbuild -ltasker` | 未定义符号、重复符号 |
| 运行期 | `tasks.tsv` 数据文件 | `TASKER_FILE` 或默认路径 | 无法读取、格式错误、无法保存 |

Python 的一次 `import` 往往替开发者处理名称查找和模块加载；C 把责任分散给预处理器、编译器、归档工具、链接器、运行库和构建系统。理解阶段边界后，错误更容易定位。

## 常见错误

### 直接包含 `.c` 文件

```c
// 不要这样组合普通模块
#include "task.c"
```

这会复制实现文本，破坏独立编译并可能产生重复定义。调用者应包含 `task.h`，构建系统负责把 `task.o` 或 `libtasker.a` 加入链接。

### 只声明接口，不链接实现

`main.c` 即使成功包含 `task_list.h`，如果链接命令没有加入 `libtasker.a`，仍会出现找不到 `task_list_add` 等符号的错误。

### 在头文件定义普通全局对象

多个翻译单元包含该头文件后可能产生多个定义。状态应尽量封装进 `TaskList` 等对象，通过函数参数明确传递。

### 忘记维护头文件依赖

如果构建规则只关注 `.c` 文件时间戳，修改结构体布局后可能留下使用旧布局的目标文件。案例使用 `-MMD -MP` 和 `.d` 文件解决这个问题。

### 让底层模块依赖应用入口

`task.c` 不应包含 CLI 的参数解析或终端输出逻辑。底层模块保持独立，才能同时服务应用、测试和未来的新入口。

## 检查点

1. `#include "task_list.h"` 是否会自动编译 `task_list.c`？不会。
2. `libtasker.a` 是否可以直接运行？不能，它没有程序入口。
3. 为什么 `task_list.c` 可以调用 `task_create`？编译时看到了声明，链接时从静态库成员中解析到定义。
4. 为什么测试不需要复制业务源码？测试目标链接了与应用相同的 `libtasker.a`。
5. 修改 `task.h` 后为什么多个 `.o` 会重建？生成的 `.d` 文件记录了直接和间接头文件依赖。

## 动手练习

基于 `examples/10-multi-file-project` 逐步完成：

1. 运行 `make clean && make && make test`，记录每一步生成的 `.o`、`.d`、`.a` 和可执行文件。
2. 连续执行两次 `make`，确认第二次不重新编译；然后只修改 `src/task.c`，观察最小重建范围。
3. 为 `Task` 增加优先级字段。同步修改公共头文件、创建逻辑、存储格式、CLI 输出和测试，观察哪些目标因头文件变化而重建。
4. 增加 `task_list_pending_count`，把声明放在 `task_list.h`、定义放在 `task_list.c`，并从测试调用它。
5. 增加 `clear-completed` 命令。列表删除规则留在 `task_list`，命令解析留在 `app/main.c`。
6. 故意从应用链接规则中删除 `-ltasker`，阅读未定义符号错误，然后恢复。
7. 使用 `ar -t build/libtasker.a` 查看静态库包含哪些目标文件；使用 `nm` 观察公共符号和 `static` 辅助函数的差别。
8. 新增第二个入口 `app/report.c`，只读取任务文件并输出完成数量，让它链接同一个 `libtasker.a`。

完成后，你应能从任意一个函数调用向两个方向追踪：编译器从哪个头文件获得声明，链接器又从哪个目标文件或库获得定义。

下一步的共享库与 Python 扩展仍沿用同一构建图，只是最终产物从普通可执行文件变成 `.so` 或 `.dylib`，并增加位置无关代码、导出符号、ABI 与运行时搜索路径。头文件仍是编译期契约，构建系统仍必须明确每个目标文件和库的依赖关系。
