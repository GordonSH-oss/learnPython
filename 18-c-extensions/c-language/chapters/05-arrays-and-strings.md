# 05 数组与字符串

## 学习目标

完成本章后，你应该能够：

- 解释数组的连续存储、长度和合法索引范围
- 区分数组对象、数组参数和指针
- 正确处理以空字符结尾的 C 字符串
- 使用容量和实际长度推理缓冲区安全
- 处理 `fgets` 截断、字符串字面量和重叠复制等边界
- 声明和使用多维数组，理解行优先（row-major）布局
- 区分 `const char *`、`char *const` 和 `const char *const`
- 使用 `snprintf` 安全构建字符串并检测截断
- 使用 `strtol`/`strtod` 进行健壮的数值解析
- 了解 VLA 的限制，知道何时改用动态分配

## 先运行示例

```bash
make build/examples/05_arrays_strings
./build/examples/05_arrays_strings
```

## 数组是固定数量的连续元素

```c
int scores[] = {90, 85, 78};
size_t count = sizeof scores / sizeof scores[0];
```

数组长度为 3，合法索引为 `0`、`1`、`2`。C 不进行边界检查，访问 `scores[3]` 属于未定义行为。

```text
scores
┌────┬────┬────┐
│ 90 │ 85 │ 78 │
└────┴────┴────┘
  0    1    2
```

`sizeof scores / sizeof scores[0]` 只在 `scores` 仍是数组对象的作用域有效。数组出现在大多数表达式中会转换为首元素指针，函数参数中的 `int values[]` 也会调整为 `int *values`：

```c
static void print_values(const int values[], size_t length);
```

函数必须额外接收元素数量，因为指针本身不保存数组长度。

## 数组初始化

C 提供多种初始化方式。部分初始化时，未指定的元素自动设为零：

```c
int a[5] = {1, 2};          /* a = {1, 2, 0, 0, 0} */
int b[5] = {0};             /* 全零初始化 */
int c[5];                   /* 局部变量：内容未定义；全局/static：全零 */
```

C99 引入了指定初始化器（designated initializer），可以按索引赋值：

```c
int table[8] = {
    [0] = 100,
    [3] = 42,
    [7] = -1,
};
/* table = {100, 0, 0, 42, 0, 0, 0, -1} */
```

指定初始化器在初始化稀疏查找表或枚举索引数组时非常有用。未指定的位置仍遵循零初始化规则。

Python 的 `[0] * n` 在 C 中的等价写法是 `int arr[n] = {0};`（仅当 `n` 为编译期常量时）。

## 多维数组

多维数组在 C 中是"数组的数组"。二维数组 `int grid[3][4]` 表示 3 行 4 列，共 12 个 `int` 按行优先连续存放：

```c
int grid[3][4] = {
    {1, 2, 3, 4},
    {5, 6, 7, 8},
    {9, 10, 11, 12},
};
```

内存布局：

```text
grid (3×4, row-major)
地址递增方向 →

┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │10 │11 │12 │
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
 [0][0]         [0][3] [1][0]         [1][3] [2][0]         [2][3]
 ─── row 0 ───  ─── row 1 ───  ─── row 2 ───
```

`grid[r][c]` 的地址等价于 `(char *)grid + (r * 4 + c) * sizeof(int)`。行优先意味着最右边的下标变化最快。遍历二维数组时，按行遍历对 CPU 缓存更友好：

```c
/* 缓存友好：逐行访问 */
for (int r = 0; r < 3; r++) {
    for (int c = 0; c < 4; c++) {
        process(grid[r][c]);
    }
}
```

### 多维数组作为函数参数

传递二维数组给函数时，除第一维外的尺寸必须在声明中给出：

```c
void print_grid(int grid[][4], size_t rows) {
    for (size_t r = 0; r < rows; r++) {
        for (size_t c = 0; c < 4; c++) {
            printf("%3d", grid[r][c]);
        }
        putchar('\n');
    }
}
```

编译器需要列数来计算每行的步长。第一维可以省略，因为参数退化为指向第一行的指针（`int (*)[4]`）。如果列数不固定，需要用指针和手动计算偏移：

```c
void print_matrix(const int *data, size_t rows, size_t cols) {
    for (size_t r = 0; r < rows; r++) {
        for (size_t c = 0; c < cols; c++) {
            printf("%3d", data[r * cols + c]);
        }
        putchar('\n');
    }
}
```

## VLA（变长数组）

C99 允许使用运行时值声明数组长度：

```c
void process(size_t n) {
    int buffer[n];  /* VLA：长度在运行时确定 */
    /* ... */
}
```

VLA 分配在栈上，不需要手动释放。但存在严重问题：

1. **栈溢出风险**：`n` 如果来自外部输入且很大，直接导致栈溢出崩溃，无法用 `if` 检测分配失败。
2. **C11 设为可选**：编译器不必支持，移植性下降。
3. **不能用于文件作用域或 `static`**：只能出现在块作用域。
4. **`sizeof` 变成运行时求值**：对 VLA 使用 `sizeof` 会在运行时计算，这与普通数组不同。

实践建议：小的、有上限的临时缓冲区可考虑 VLA，否则优先使用 `malloc`：

```c
void safe_process(size_t n) {
    if (n > 4096) {
        /* 拒绝不合理的大小 */
        return;
    }
    int buffer[n];
    /* ... */
}
```

更安全的替代方案是动态分配（第 08 章）：

```c
int *buffer = malloc(n * sizeof *buffer);
if (!buffer) { /* 处理失败 */ }
/* 使用 buffer */
free(buffer);
```

## 字符数组与 C 字符串

C 字符串是以空字符 `\0` 结束的字符序列：

```c
char name[20] = "Ada";
```

内存布局：

```text
name (容量 20 字节)
┌───┬───┬───┬───┬───┬───┬───┬───┬─── ─── ───┐
│'A'│'d'│'a'│\0 │ 0 │ 0 │ 0 │ 0 │ ...       │
└───┴───┴───┴───┴───┴───┴───┴───┴─── ─── ───┘
  0   1   2   3   4   5  ...          19
          ↑ strlen=3
```

前四个字节是 `'A'`、`'d'`、`'a'`、`'\0'`，剩余空间属于数组容量。`strlen(name)` 返回 3，不包含终止符。

不是所有字符数组都是字符串：

```c
char bytes[3] = {'A', 'B', 'C'}; /* 没有 \0，不能传给 strlen */
```

字符串函数会一直查找终止符。若容量内没有 `\0`，它们会越界读取。

## 容量、长度和剩余空间

处理字符串时始终区分：

- **容量**：数组总共能保存多少字节
- **长度**：第一个 `\0` 之前有多少字节（`strlen` 的返回值）
- **剩余空间**：容量减去当前内容以及终止符所需空间

一个容量为 20 的数组最多保存 19 字节字符串内容，因为至少要留一个字节给 `\0`。

```c
char buf[20] = "hello";
size_t cap    = sizeof buf;        /* 20 */
size_t len    = strlen(buf);       /* 5  */
size_t remain = cap - len - 1;     /* 14：还能追加 14 字节 */
```

Python 的 `str` 会自动扩容，C 中你必须在每次写入前自行检查剩余空间。

## `const` 与数组/字符串

`const` 和指针的组合在 C 中有三种含义：

```c
const char *p1 = "hello";       /* 指向的字符是只读的，指针可以改指别处 */
char *const p2 = buf;           /* 指针本身不能改指，但可以修改指向的内容 */
const char *const p3 = "world"; /* 都不能改 */
```

记忆方法：从变量名向左读，`const` 修饰它左边最近的东西。

```text
const char *p      →  *p 是 const char  →  不能通过 p 修改字符
char *const p      →  p 是 const        →  不能让 p 指向别处
const char *const p →  两者都是 const
```

在函数参数中，`const char *` 表示函数承诺不修改传入的字符串，是一种接口契约：

```c
size_t my_strlen(const char *s) {
    const char *p = s;
    while (*p) p++;
    return (size_t)(p - s);
}
```

## 复合字面量

C99 引入复合字面量（compound literal），可以创建临时的匿名数组或结构体：

```c
/* 传递临时数组给函数，无需先声明变量 */
print_values((int[]){10, 20, 30}, 3);

/* 等价于 */
int temp[] = {10, 20, 30};
print_values(temp, 3);
```

复合字面量的生命周期：

- 在块作用域中：与包含它的块同生命周期（类似局部变量）。
- 在文件作用域中：静态存储期。

注意不要返回指向局部复合字面量的指针——函数返回后该对象已失效：

```c
/* 错误：返回的指针指向已销毁的局部对象 */
int *bad(void) {
    return (int[]){1, 2, 3};
}
```

复合字面量配合 `const` 可以作为只读的临时配置表：

```c
const char *const keywords[] = {"if", "else", "while", "return", NULL};
```

## 使用 `fgets` 读取一行

```c
#include <stdio.h>
#include <string.h>

char line[128];
if (fgets(line, sizeof line, stdin) == NULL) {
    if (ferror(stdin)) {
        perror("stdin");
    }
    return 1;
}

size_t newline = strcspn(line, "\n");
if (line[newline] == '\n') {
    line[newline] = '\0';
} else if (!feof(stdin)) {
    /* 当前缓冲区只读到一部分行，需要决定丢弃余下内容还是继续拼接 */
}
```

`fgets` 知道缓冲区容量并保证成功读取时以 `\0` 结束，但一行过长时只返回前一部分。简单地去掉换行符不能区分"最后一行没有换行"和"输入被截断"。

与 Python 的 `input()` 对比：Python 自动处理内存分配和行分隔，C 需要你明确管理缓冲区大小和截断逻辑。

## 常用内存与字符串函数

| 函数 | 用途 | 关键边界 |
| --- | --- | --- |
| `strlen` | 查找字符串长度 | 输入必须在有效范围内包含 `\0` |
| `strcmp` | 按字节比较字符串 | 返回值只保证正、零或负 |
| `strncmp` | 比较前 n 个字节 | 可用于前缀匹配 |
| `strchr` | 查找字符首次出现 | 可能返回 `NULL` |
| `strrchr` | 查找字符最后出现 | 可能返回 `NULL` |
| `strstr` | 查找子串 | 可能返回 `NULL` |
| `memcpy` | 复制不重叠字节区间 | 重叠时行为未定义 |
| `memmove` | 复制可能重叠的区间 | 通常比 `memcpy` 更保守 |
| `memset` | 填充字节 | 按字节填充，对非零 int 数组无效 |

不要用 `strcpy` 向未知容量的目标写入。接口应同时知道目标容量，并在写入前验证需要的字节数。

## 字符串解析模式

### `strtol` / `strtod`：健壮的数值解析

Python 的 `int("42")` 会抛异常，C 中需要用 `strtol` 配合 `endptr` 检测解析结果：

```c
#include <stdlib.h>
#include <errno.h>

const char *input = "  123abc";
char *end;
errno = 0;
long value = strtol(input, &end, 10);

if (end == input) {
    /* 没有解析到任何数字 */
} else if (errno == ERANGE) {
    /* 溢出：值超出 long 范围 */
} else if (*end != '\0') {
    /* 部分解析成功：end 指向 'a'，value 是 123 */
} else {
    /* 完全解析成功 */
}
```

`endptr` 指向第一个未被消费的字符。通过检查 `*end` 是否为 `\0` 或空白，可以判断输入是否完全由数字组成。`strtod` 用法相同，返回 `double`。

### `strtok`：有状态的分词

```c
char line[] = "name,age,city";
char *token = strtok(line, ",");
while (token) {
    printf("token: [%s]\n", token);
    token = strtok(NULL, ",");
}
```

`strtok` 的问题：

1. **修改原字符串**：用 `\0` 替换分隔符。
2. **内部静态状态**：不可重入，多线程不安全。用 `strtok_r`（POSIX）替代。
3. **不能处理空字段**：连续分隔符 `"a,,b"` 中的空字段会被跳过。

### `sscanf` 与手动解析

`sscanf` 类似 Python 的格式化读取，可从字符串中按格式提取字段：

```c
int year, month, day;
if (sscanf("2024-03-15", "%d-%d-%d", &year, &month, &day) == 3) {
    /* 解析成功 */
}
```

`sscanf` 返回成功匹配的字段数，务必检查返回值。对于复杂格式，手动逐字符解析配合 `strtol` 通常更可控：

```c
/* 手动解析 "key=value" */
const char *eq = strchr(input, '=');
if (eq) {
    size_t key_len = (size_t)(eq - input);
    const char *val = eq + 1;
    /* 使用 key_len 和 val */
}
```

## 字符串构建：`snprintf`

`snprintf` 是 C 中安全构建字符串的首选方法。它保证不超出缓冲区容量，并返回"如果空间足够会写入的字符数"：

```c
char buf[64];
int n = snprintf(buf, sizeof buf, "user=%s id=%d", name, id);
if (n < 0) {
    /* 编码错误 */
} else if ((size_t)n >= sizeof buf) {
    /* 输出被截断：需要 n+1 字节才能完整写入 */
}
```

利用返回值检测截断，这是 `snprintf` 相比 `sprintf` 的核心优势。

### 增量构建字符串

当需要逐步拼接时，追踪已写入的偏移量：

```c
char result[256];
size_t cap = sizeof result;
size_t off = 0;

for (int i = 0; i < count && off < cap; i++) {
    int n = snprintf(result + off, cap - off, "%s%d",
                     (i > 0 ? "," : ""), values[i]);
    if (n < 0) break;
    if ((size_t)n >= cap - off) {
        off = cap;  /* 标记截断 */
        break;
    }
    off += (size_t)n;
}
/* result 包含类似 "1,2,3,4" 的内容 */
```

这种模式等价于 Python 的 `",".join(str(v) for v in values)`，但需要手动管理缓冲区边界。

## 字符串字面量与 UTF-8

字符串字面量存放在只读数据段，不能修改：

```c
const char *message = "hello";
/* message[0] = 'H';  错误：未定义行为 */
```

如果需要修改，应复制到数组：

```c
char message[] = "hello";
message[0] = 'H';  /* 合法：message 是局部数组 */
```

相邻的字符串字面量会自动拼接，这在拆分长字符串时很有用：

```c
const char *sql =
    "SELECT id, name "
    "FROM users "
    "WHERE active = 1";
```

### UTF-8 注意事项

在 UTF-8 中，一个用户看到的字符可能占多个字节：

```c
const char *hello = "你好";  /* 6 字节，2 个字符 */
strlen(hello);               /* 6，不是 2 */
```

因此：
- `strlen` 返回字节数，不是 Unicode 字符数
- 按字节反转 UTF-8 文本会破坏编码
- 按字节截断可能截在多字节字符中间
- 比较 UTF-8 字符串时 `strcmp` 按字节序比较，不是 Unicode 排序规则

## 内存布局可视化

理解数组和字符串在内存中的精确布局对于调试和写正确代码至关重要。

### 字符串数组

```c
const char *names[] = {"Alice", "Bob", "Charlie"};
```

```text
栈上的指针数组 names:
┌──────────┬──────────┬──────────┐
│ ptr → "A"│ ptr → "B"│ ptr → "C"│    (每个元素是一个指针)
└──────────┴──────────┴──────────┘

只读数据段:
... "Alice\0" ... "Bob\0" ... "Charlie\0" ...
```

每个元素是指针（8 字节，64 位系统），指向只读数据段中的字符串字面量。

对比 `char names[][8]`——这是真正的二维字符数组：

```c
char names[][8] = {"Alice", "Bob", "Charlie"};
```

```text
连续内存（3×8 = 24 字节）:
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬─── ...
│'A'│'l'│'i'│'c'│'e'│\0 │ 0 │ 0 │'B'│'o'│'b'│\0 │ 0  ...
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴─── ...
 ──── names[0] (8B) ────  ──── names[1] (8B) ────
```

### 结构体数组的对齐

```c
struct Record {
    char name[5];   /* 5 字节 */
    int id;         /* 4 字节，需要 4 字节对齐 */
};
struct Record records[2] = {{"Ada", 1}, {"Bob", 2}};
```

```text
records (含填充):
┌─────────────┬───┬───┬───┬───┬─────────────┬───┬───┬───┬───┐
│ A d a \0  0 │pad│pad│pad│ 1 │ B o b \0  0 │pad│pad│pad│ 2 │
└─────────────┴───┴───┴───┴───┴─────────────┴───┴───┴───┴───┘
  name (5B)    (3B pad) id(4B)   name (5B)    (3B pad) id(4B)
  ───── sizeof(struct Record) = 12 ─────
```

编译器在 `name` 后插入 3 字节填充，使 `id` 对齐到 4 字节边界。`sizeof(struct Record)` 是 12 而不是 9。

## 常见错误

- 使用 `<= length` 访问末尾后一元素（off-by-one）
- 在函数参数上用 `sizeof` 计算数组长度（参数已退化为指针）
- 忘记为字符串终止符保留空间
- 对没有 `\0` 的字节数组调用字符串函数
- 忽略 `fgets` 返回值和长行截断
- 使用 `memcpy` 复制重叠区域（应用 `memmove`）
- 修改字符串字面量（未定义行为）
- 把字节数量等同于用户看到的字符数量
- 忽略 `strtol` 的 `endptr` 和 `errno`，无法检测解析失败
- 在多线程中使用 `strtok` 而非 `strtok_r`
- 不检查 `snprintf` 返回值，静默截断输出
- 用 VLA 接收不受控的外部输入大小
- 返回指向局部复合字面量或局部数组的指针（悬空指针）
- 遍历二维数组时按列优先（cache miss 率高）
- 混淆 `const char *`（字符只读）和 `char *const`（指针只读）

## 检查点

1. `sizeof "cat"` 和 `strlen("cat")` 分别是多少？为什么不同？
2. 为什么函数无法从 `int *` 推导数组长度？
3. `fgets` 返回的内容没有换行符时，可能有哪些原因？
4. `int grid[3][4]` 中，`grid[1][2]` 在连续内存中是第几个元素？
5. `strtol("123abc", &end, 10)` 执行后 `*end` 是什么？
6. `snprintf` 返回值大于等于缓冲区大小时意味着什么？
7. `const char *p` 和 `char *const p` 哪个能修改字符内容？
8. 为什么 VLA 无法检测分配失败？

## 动手练习

1. **字符串工具**：完成 `exercises/04_string_tools.c`，实现以下功能：
   - 统计字母、数字和空白字符数量
   - 反转 ASCII 字符串（原地操作）
   - 用 `snprintf` 将统计结果格式化到一个固定大小的缓冲区中

2. **安全复制函数**：编写 `size_t safe_strcpy(char *dst, size_t cap, const char *src)`：
   - 保证以 `\0` 结尾
   - 返回源字符串长度（即使被截断）
   - 当 `cap == 0` 时不写入任何字节

3. **数值解析器**：编写函数 `int parse_int_list(const char *input, int *out, size_t max_count)`：
   - 解析逗号分隔的整数列表，如 `"1, 2, -3, 42"`
   - 使用 `strtol` + `endptr` 检测非法字符
   - 返回成功解析的整数个数，或 `-1` 表示格式错误

4. **矩阵转置**：编写 `void transpose(const int *src, int *dst, size_t rows, size_t cols)`：
   - 将 `rows×cols` 的行优先矩阵转置为 `cols×rows`
   - 使用手动偏移计算 `src[r * cols + c]`

5. **长行读取**：给读取逻辑增加长行检测：
   - 分别测试空行、恰好装满缓冲区和超过容量的输入
   - 当一行超过缓冲区时，丢弃剩余内容并报告截断

6. **CSV 简易解析器**：使用 `strtok_r` 实现一个按行、按字段拆分 CSV 的函数：
   - 处理行尾的 `\r\n` 和 `\n`
   - 注意 `strtok` 跳过空字段的行为，考虑手动查找分隔符的替代方案

