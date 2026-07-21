# 07 结构体、枚举与联合体

## 学习目标

完成本章后，你应能：

- 使用结构体把多个不同类型的字段组织成一个数据模型。
- 区分结构体对象、结构体指针以及 `.`、`->` 两种成员访问方式。
- 使用枚举为有限状态命名，并通过 `switch` 处理所有状态。
- 解释联合体成员为什么共享存储，以及当前有效成员由谁负责记录。
- 使用“枚举标签 + 联合体载荷”表示多种可能的数据形态。
- 使用 `sizeof` 和 `_Alignof` 观察结构体、枚举与联合体的布局。

中文资料通常把 `union` 称为“联合体”或“联合”。“共同体”也偶尔出现，但本教程统一使用“联合体”。

## 从单个值到数据模型

基础类型只能直接表达一个值。一个学生同时具有姓名、成绩和学习等级，需要把多个字段组织成一个整体：

```c
typedef struct {
    char name[40];
    int score;
} Student;
```

结构体的每个成员拥有自己的存储空间。一个 `Student` 对象同时保存整个 `name` 数组和一个 `score`。

```text
Student
+-------------------------------+----------+
| name[40]                      | score    |
+-------------------------------+----------+
```

编译器还可能在成员之间或末尾插入填充，因此示意图不代表精确字节布局。

## 结构体的定义与初始化

`struct` 定义一种由多个成员组成的类型：

```c
struct Point {
    double x;
    double y;
};

struct Point origin = {0.0, 0.0};
```

在 C 中，只有结构体标签时必须写 `struct Point`。`typedef` 可以为类型提供更简洁的名称：

```c
typedef struct {
    double x;
    double y;
} Point;

Point origin = {0.0, 0.0};
```

指定初始化器直接写出成员名，更能抵抗成员顺序变化：

```c
Student learner = {
    .name = "Ada",
    .score = 95,
};
```

没有显式指定的成员会按静态初始化规则初始化为零值。指定初始化器适合字段较多的结构体，也让代码审查者更容易看出每个值的含义。

## 成员访问与结构体指针

结构体对象使用 `.` 访问成员：

```c
learner.score = 98;
printf("%s: %d\n", learner.name, learner.score);
```

结构体指针使用 `->`：

```c
static void add_bonus(Student *student, int bonus) {
    if (student == NULL) return;
    student->score += bonus;
}
```

`student->score` 等价于 `(*student).score`。因为 `.` 的优先级高于一元 `*`，后一种写法中的括号不可省略。

不需要修改对象的函数应接收指向 `const` 的指针：

```c
static void print_student(const Student *student) {
    if (student == NULL) return;
    printf("%s: %d\n", student->name, student->score);
}
```

结构体可以按值传递和赋值，所有成员都会被复制：

```c
Student copy = learner;
```

数组成员的内容也会随结构体复制，但指针成员只复制地址值，不会自动复制所指对象。大型结构体通常通过指针传参，既避免不必要的复制，也能用 `const` 表达只读意图。

## 枚举表示有限状态

枚举为一组整数常量命名：

```c
typedef enum {
    STATUS_OK,
    STATUS_INVALID,
    STATUS_IO_ERROR
} Status;
```

未指定数值时，第一个枚举常量通常从 `0` 开始，后续依次加一。也可以显式指定：

```c
typedef enum {
    PERMISSION_READ  = 1,
    PERMISSION_WRITE = 2,
    PERMISSION_ADMIN = 4
} Permission;
```

枚举适合表示状态、类别、模式和错误原因。它比散落的数字更能表达允许出现的状态空间：

```c
static const char *status_name(Status status) {
    switch (status) {
        case STATUS_OK:
            return "ok";
        case STATUS_INVALID:
            return "invalid";
        case STATUS_IO_ERROR:
            return "I/O error";
    }

    return "unknown";
}
```

C 的枚举不像某些语言中的封闭代数类型。编译器通常不能完全阻止其他整数值进入枚举变量，因此面对外部输入时仍应验证，并为意外值保留防御路径。

## 联合体：多个解释共享一块存储

结构体为每个成员分别分配空间；联合体的所有成员从同一地址开始，共享同一块存储：

```c
union Number {
    int integer;
    double real;
};
```

也可以通过 `typedef` 简化类型名：

```c
typedef union {
    int integer;
    double real;
} Number;
```

如果写入 `integer`，这块存储当前保存的是整数表示；随后写入 `real`，相同存储会被新的 `double` 表示覆盖：

```c
Number number;

number.integer = 42;
printf("%d\n", number.integer);

number.real = 3.5;
printf("%.1f\n", number.real);
```

可以用下面的模型理解结构体和联合体的差别：

```text
struct NumberPair             union Number
+----------+---------------+  +---------------+
| integer  | real          |  | integer       |
+----------+---------------+  | 或 real       |
                              +---------------+
```

结构体同时保存所有成员；联合体在同一位置保存其中一种成员表示。

### 大小与对齐

联合体必须足以容纳最大的成员，并满足所有成员的对齐要求：

```c
printf("int: %zu\n", sizeof(int));
printf("double: %zu\n", sizeof(double));
printf("Number: %zu\n", sizeof(Number));
```

`sizeof(Number)` 至少不小于最大成员的大小，还可能因为对齐要求包含额外填充。不要把联合体大小写死为某个数字，应在目标平台上使用 `sizeof`。

### 联合体不记录当前成员

联合体只提供共享存储，不会自动记住最后写入的是哪个成员：

```c
Number number = {.real = 3.5};
```

程序必须自己知道当前有效成员是 `real`。如果程序失去这个信息，就无法可靠判断应按 `int` 还是 `double` 解释存储内容。

初始化时可以使用指定初始化器选择成员：

```c
Number integer = {.integer = 42};
Number real = {.real = 3.5};
```

没有成员标签的裸联合体适合标签由上下文明确提供的情况，例如协议字段中的类型码、函数参数或状态机当前状态。一般业务数据更适合使用带标签联合体。

## 带标签联合体

带标签联合体把枚举和联合体放进同一个结构体：

```c
typedef enum {
    VALUE_INTEGER,
    VALUE_REAL,
    VALUE_TEXT
} ValueKind;

typedef struct {
    ValueKind kind;
    union {
        int integer;
        double real;
        const char *text;
    } as;
} Value;
```

这里两个部分承担不同职责：

- `kind` 是标签，记录联合体当前应按哪种类型解释。
- `as` 是载荷，保存与标签对应的值。

```text
Value
+---------------+-----------------------+
| kind          | as                    |
| VALUE_REAL    | union storage: 3.5    |
+---------------+-----------------------+
```

可以使用指定初始化器构造不同形态的值：

```c
Value count = {
    .kind = VALUE_INTEGER,
    .as.integer = 42,
};

Value price = {
    .kind = VALUE_REAL,
    .as.real = 12.5,
};

Value name = {
    .kind = VALUE_TEXT,
    .as.text = "Ada",
};
```

读取载荷前必须先检查标签：

```c
static void print_value(const Value *value) {
    if (value == NULL) return;

    switch (value->kind) {
        case VALUE_INTEGER:
            printf("%d\n", value->as.integer);
            break;
        case VALUE_REAL:
            printf("%.2f\n", value->as.real);
            break;
        case VALUE_TEXT:
            printf("%s\n", value->as.text);
            break;
        default:
            fputs("invalid value\n", stderr);
            break;
    }
}
```

标签和载荷必须作为一个不变量保持同步：

```text
VALUE_INTEGER -> as.integer 有效
VALUE_REAL    -> as.real 有效
VALUE_TEXT    -> as.text 有效
```

修改标签时必须写入对应载荷，读取载荷时必须先判断标签。把构造过程封装进函数可以降低出错概率：

```c
static Value value_from_integer(int integer) {
    return (Value) {
        .kind = VALUE_INTEGER,
        .as.integer = integer,
    };
}
```

## 联合体的典型用途

### 表示多种可能的值

解析器、配置系统、消息系统和解释器经常需要表示“整数、浮点数或文本之一”。带标签联合体能在不使用继承和运行时对象系统的情况下表达这种数据。

Python 变量可以在运行时引用不同类型的对象；C 必须显式保存类型标签和对应载荷。简化后的动态值模型可以理解为：

```text
Python 对象的运行时类型信息
            ↓ 在 C 中显式表达
枚举标签 + 联合体载荷
```

CPython 对象模型比这个示例复杂得多，但“先检查类型，再按对应布局解释数据”的思路相通。

### 节省互斥数据的存储空间

如果几种较大的数据形态永远不会同时存在，联合体可以让它们复用存储。这在嵌入式系统、协议消息和固定大小缓冲区中较常见。

不要为了节省几个字节就牺牲清晰度。先证明成员确实互斥，并通过 `sizeof` 和真实数据规模确认收益。

### 映射底层接口或文件格式

操作系统 API、硬件寄存器和二进制协议有时会定义联合体布局。此时应严格遵守接口规定，并同时考虑字节序、对齐、填充和 ABI。不要假定把任意文件字节直接读入联合体就一定可移植。

## 联合体不能解决什么

### 它不是自动类型转换

写入 `double` 后读取 `int` 不会执行数值转换。它是在用另一种成员类型解释共享存储，而不是把 `3.5` 转换为整数 `3`。

需要数值转换时应写普通强制转换或使用相应转换函数：

```c
int integer = (int)number.real;
```

### 它不是可移植的字节序列化方案

成员的表示、大小、对齐和字节序可能因平台而异。网络协议或文件格式应明确编码每个字段，而不是直接写出整个联合体的内存。

### 它不会管理指针所指资源

如果联合体成员是 `char *`、文件句柄或其他资源，联合体只保存指针或句柄值。程序仍必须根据标签执行正确的复制、释放和错误处理。

```c
typedef struct {
    ValueKind kind;
    union {
        int integer;
        char *owned_text;
    } as;
} OwnedValue;
```

当 `kind` 表示文本时，销毁函数必须释放 `owned_text`；整数形态则不能把同一存储误当作指针释放。

## 内存对齐与填充

结构体大小可能大于成员大小之和，因为编译器会插入填充，以让成员地址满足对齐要求：

```c
typedef struct {
    char flag;
    double value;
    int count;
} Record;
```

可以观察大小和对齐：

```c
printf("Record: size=%zu align=%zu\n",
       sizeof(Record), _Alignof(Record));
printf("Value: size=%zu align=%zu\n",
       sizeof(Value), _Alignof(Value));
```

成员顺序可能影响结构体大小，联合体大小通常由最大成员及对齐要求决定。但不要只为了减少填充而破坏数据模型，除非测量证明内存布局确实是瓶颈。

公开结构体或联合体布局还会形成 ABI 契约。库升级时改变成员、顺序或编译选项，可能让旧调用者对对象大小和偏移的理解失效。需要隐藏布局时，可以在公共头文件只声明结构体名称，在实现文件中保留完整定义；第 10 章会继续讨论模块接口。

## 常见错误

### 忘记更新联合体标签

```c
value.kind = VALUE_REAL;
// 忘记写 value.as.real
```

此时标签宣称实数载荷有效，但存储中可能仍是旧值或未初始化数据。优先使用构造函数同时设置标签和载荷。

### 不检查标签就读取成员

```c
printf("%d\n", value.as.integer);
```

只有 `value.kind == VALUE_INTEGER` 时，这段读取才符合该数据模型的契约。

### 混淆结构体和联合体

如果数据需要同时保存名称和成绩，应使用结构体；如果一个值在整数和浮点数两种形态中二选一，才可能使用联合体。

### 以为 `typedef` 创建了新运行时对象

`typedef` 只是为类型提供别名，不会分配存储，也不会自动生成构造、销毁或验证逻辑。

## 检查点

在运行前预测：

```c
typedef struct {
    int integer;
    double real;
} Pair;

typedef union {
    int integer;
    double real;
} Number;
```

- `Pair` 能否同时保存两个成员？可以。
- `Number` 能否可靠地同时保存两个成员？不能，它们共享存储。
- `sizeof(Number)` 是否等于两个成员大小之和？通常不是，它至少能容纳最大成员并满足对齐要求。
- 只看 `Number` 对象能否知道当前有效成员？不能，需要上下文或额外标签。

## 动手练习

1. 运行 `examples/07_structs.c`，观察结构体、枚举和带标签联合体的输出。
2. 为 `Value` 增加 `VALUE_BOOLEAN` 和对应的 `bool boolean` 成员，更新构造与打印逻辑。
3. 故意让标签为 `VALUE_INTEGER`，却写入 `as.real`。解释为什么程序的数据模型已经失效，即使运行时暂时没有崩溃。
4. 使用 `sizeof` 和 `_Alignof` 比较 `Pair`、`Number` 和 `Value`，画出你对布局的预测，再与实际结果比较。
5. 完成 `exercises/05_student_records.c`：定义学生结构体，按成绩降序排序，并按姓名查找。
6. 进阶：定义一条命令，其参数可以是整数、文本或无参数。使用枚举标签和联合体载荷建模，并实现安全的打印函数。
