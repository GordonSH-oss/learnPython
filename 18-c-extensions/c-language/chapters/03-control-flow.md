# 03 分支与循环

## 学习目标

完成本章后，你应该能够：

- 使用 `if`、`else if` 和 `switch` 表达互斥规则
- 解释 `&&` 和 `||` 的短路求值顺序，并利用它做安全的指针检查
- 正确使用三元运算符，并判断何时它会降低可读性
- 用提前返回和守卫子句减少条件嵌套
- 根据循环状态选择 `for`、`while` 或 `do ... while`
- 使用逗号运算符在 `for` 头部维护多个变量
- 识别哨兵循环、标志控制循环和双重循环搜索等常见循环模式
- 理解 `goto` 的唯一合法场景：多步骤初始化的资源清理
- 识别并修复死代码，理解编译器对不可达路径的警告
- 识别赋值误写、越界、无限循环、无符号回绕和意外贯穿等问题

## 先运行示例

```bash
make build/examples/03_control_flow
./build/examples/03_control_flow
```

运行前先预测每个分支和循环会输出什么，再和结果比较。控制流学习的重点不是背语法，而是能够沿着状态变化预测执行路径。

## `if`：根据布尔条件选择路径

C 中整数 `0` 表示假，非 `0` 表示真。关系和逻辑运算通常产生 `0` 或 `1`：

```c
if (score < 0 || score > 100) {
    puts("invalid score");
} else if (score >= 60) {
    puts("pass");
} else {
    puts("fail");
}
```

条件按从上到下的顺序判断，第一个为真的分支执行后，其余分支不会执行。因此范围更窄或优先级更高的规则通常放在前面。

不要误写成：

```c
if (score = 60) { /* 赋值结果为 60，因此条件为真 */ }
```

开启 `-Wall` 通常能发现这种错误。若确实需要在条件中赋值，应使用括号明确意图：

```c
if ((c = getchar()) != EOF) { /* 此写法意图明确 */ }
```

## 短路求值：`&&` 与 `||` 的求值顺序

C 标准保证逻辑运算符从左到右求值，且一旦结果确定就停止：

- `&&`：左操作数为假时，右操作数**不求值**。
- `||`：左操作数为真时，右操作数**不求值**。

这不是优化细节，而是可以依赖的行为。CPython 源码中随处可见利用短路做安全检查的模式：

```c
/* 先确认指针非空，再访问成员 */
if (obj != NULL && obj->ob_type == &PyLong_Type) {
    /* 安全地使用 obj */
}
```

如果去掉 `obj != NULL`，当 `obj` 为空指针时解引用会导致段错误。短路求值保证左边为假时右边不会执行。

反过来，`||` 常用于提供默认值或后备操作：

```c
/* 先尝试从缓存读取，失败再从磁盘读取 */
if (read_cache(key, &value) || read_disk(key, &value)) {
    use(value);
}
```

Python 的 `and` / `or` 同样短路，但 C 的短路仅适用于 `&&` 和 `||`，**不适用于按位运算 `&` 和 `|`**。混淆二者是常见错误。

```c
/* 错误：& 不短路，右边总会求值 */
if (ptr != NULL & ptr->field > 0) { /* 危险 */ }
```

## 三元运算符

三元运算符 `condition ? a : b` 是表达式，而不是语句。它在需要根据条件产生一个值时很简洁：

```c
int abs_val = (x >= 0) ? x : -x;
const char *label = (score >= 60) ? "pass" : "fail";
```

与 Python 的 `x if cond else y` 相比，C 的语法将条件放在前面，更接近自然语言的"取这个或那个"。

适合使用三元运算符的场景：

- 两个分支都是简单表达式，且结果立刻使用。
- 初始化 `const` 变量（`if` 语句无法初始化 `const`）。

不适合的场景：

```c
/* 不推荐：三元运算符嵌套，可读性差 */
int category = (x < 0) ? -1 : (x == 0) ? 0 : (x < 10) ? 1 : 2;
```

嵌套三元是合法的，但应该用 `if / else if` 替代。每个分支含有副作用（函数调用、赋值）时也应改用 `if`：

```c
/* 不推荐：副作用在三元里不直观 */
result = (flag) ? compute_heavy() : fallback();

/* 推荐 */
if (flag) {
    result = compute_heavy();
} else {
    result = fallback();
}
```

## 嵌套条件与扁平化

深层嵌套让代码向右漂移，执行路径难以追踪。函数中常见的扁平化手段是**提前返回**：

```c
/* 嵌套版本 */
int process(const char *buf, size_t len) {
    if (buf != NULL) {
        if (len > 0) {
            if (len <= MAX_SIZE) {
                do_work(buf, len);
                return 0;
            }
        }
    }
    return -1;
}
```

```c
/* 提前返回版本（守卫子句） */
int process(const char *buf, size_t len) {
    if (buf == NULL)   return -1;
    if (len == 0)      return -1;
    if (len > MAX_SIZE) return -1;

    do_work(buf, len);
    return 0;
}
```

守卫子句将异常情况排除在前，让"正常路径"占据函数主体。读代码时只要通过了守卫，就知道当前数据是有效的。CPython 中大量函数采用这种风格：

```c
/* CPython 风格：入口校验后直接进入主逻辑 */
static PyObject *
list_append(PyListObject *self, PyObject *value) {
    if (value == NULL) {
        PyErr_BadInternalCall();
        return NULL;
    }
    /* 主逻辑不需要再检查 value */
    ...
}
```

## `switch`：处理离散状态

`switch` 适合整数、字符或枚举状态：

```c
switch (command) {
case 'a':
    puts("add");
    break;
case 'd':
    puts("delete");
    break;
case 'q':
    puts("quit");
    break;
default:
    puts("unknown command");
    break;
}
```

没有 `break` 时会继续执行后续 case，这称为贯穿（fall-through）。只有确实需要时才利用贯穿，并用注释说明意图：

```c
case 'Y':
case 'y':
    /* 两个 case 合并处理 */
    confirm = true;
    break;
```

## `switch` 进阶：枚举穷举与 `-Wswitch`

当 `switch` 的对象是枚举类型时，编译器可以检查是否覆盖了所有枚举值。使用 `-Wswitch`（包含在 `-Wall` 中）：

```c
typedef enum { STATE_INIT, STATE_RUN, STATE_DONE } State;

void handle(State s) {
    switch (s) {
    case STATE_INIT: setup();  break;
    case STATE_RUN:  run();    break;
    /* 没有 STATE_DONE => 编译器警告 */
    }
}
```

编译时会得到：`warning: enumeration value 'STATE_DONE' not handled in switch`。

这里有一个权衡：如果你加了 `default`，编译器就不再警告缺少的枚举值，因为 `default` 覆盖了所有未列出的情况。因此对枚举的 `switch`，**故意省略 `default`** 让编译器帮你捕获遗漏是更安全的做法：

```c
switch (s) {
case STATE_INIT: setup();  break;
case STATE_RUN:  run();    break;
case STATE_DONE: cleanup(); break;
/* 不写 default：新增枚举值时编译器会提醒 */
}
```

如果后续有人加了 `STATE_ERROR` 但忘了更新 `switch`，编译器会立刻报警。这种"让编译器替你抓 bug"的思路在 CPython 代码中广泛使用。

对于接收外部输入的场景（命令行参数、网络数据），`default` 仍然必要——外部数据不受枚举限制。

## 三种循环

### `for`：计数或索引明确

```c
for (size_t i = 0; i < length; ++i) {
    printf("%d\n", values[i]);
}
```

数组合法索引是 `0` 到 `length - 1`，所以条件是 `i < length`，不是 `i <= length`。

### `while`：先检查是否还能继续

```c
while (remaining > 0) {
    process_one();
    --remaining;
}
```

### `do ... while`：循环体至少执行一次

```c
do {
    read_command();
} while (!should_quit);
```

## `for` 循环中的逗号运算符

`for` 头部的初始化和更新表达式可以用逗号运算符同时操作多个变量。逗号运算符从左到右依次求值，整体结果是最右边的值：

```c
/* 同时维护左右两个索引 */
for (size_t lo = 0, hi = length - 1; lo < hi; ++lo, --hi) {
    int tmp = arr[lo];
    arr[lo] = arr[hi];
    arr[hi] = tmp;
}
```

这里 `++lo, --hi` 是一个逗号表达式，两个操作都会执行。

逗号运算符**只应该**出现在 `for` 的初始化和更新部分，不要在普通表达式中使用它——读者很难察觉它的存在：

```c
/* 不推荐：普通语句中的逗号运算符 */
result = (a = 1, b = 2, a + b);  /* 容易误解 */
```

如果在 `for` 里需要操作的变量类型不同，必须在 `for` 之前声明它们：

```c
size_t i;
int total;
for (i = 0, total = 0; i < length; ++i, total += arr[i]) {
    /* ... */
}
```

因为 `for` 的初始化部分只能有一个声明语句，且所有声明变量的类型必须相同。

## 循环模式

### 哨兵循环（Sentinel Loop）

哨兵是数据流中表示"结束"的特殊值。C 标准库广泛使用这一模式：

```c
/* getchar() 返回 EOF（通常是 -1）作为哨兵 */
int c;
while ((c = getchar()) != EOF) {
    putchar(c);
}
```

```c
/* C 字符串以 '\0' 作为哨兵 */
size_t my_strlen(const char *s) {
    size_t len = 0;
    while (s[len] != '\0') {
        ++len;
    }
    return len;
}
```

哨兵循环不需要预先知道数据长度，只要能识别终止值即可。注意哨兵值本身不属于有效数据。

### 标志控制循环（Flag-controlled Loop）

使用布尔变量控制循环退出，适用于退出条件分散在循环体多处的场景：

```c
bool running = true;
while (running) {
    int cmd = read_command();
    switch (cmd) {
    case CMD_QUIT:
        running = false;
        break;
    case CMD_ERROR:
        if (++error_count > MAX_ERRORS) {
            running = false;
        }
        break;
    default:
        execute(cmd);
        break;
    }
}
```

相比在循环内部使用 `break` + `goto`，标志变量让"循环在什么条件下结束"一目了然。

### 双重循环搜索（Double-loop Search）

在二维结构或需要组合查找时，嵌套循环很常见。关键问题是如何在内层找到结果后退出外层：

```c
/* 在二维数组中查找目标值 */
bool found = false;
size_t row = 0, col = 0;
for (size_t r = 0; r < rows && !found; ++r) {
    for (size_t c = 0; c < cols; ++c) {
        if (matrix[r][c] == target) {
            row = r;
            col = c;
            found = true;
            break;  /* 退出内层 */
        }
    }
}
/* 外层通过 !found 条件自然退出 */
```

另一种方法是将搜索封装为函数，用 `return` 直接退出：

```c
static bool find_in_matrix(int matrix[][COLS], size_t rows,
                           int target, size_t *out_r, size_t *out_c) {
    for (size_t r = 0; r < rows; ++r) {
        for (size_t c = 0; c < COLS; ++c) {
            if (matrix[r][c] == target) {
                *out_r = r;
                *out_c = c;
                return true;
            }
        }
    }
    return false;
}
```

封装为函数是更清晰的做法，也避免了 `goto` 或标志变量的开销。

## 用状态推理循环

写循环前回答：

1. 初始状态是什么？
2. 循环继续时必须满足什么条件？
3. 每轮怎样改变状态并接近终止？
4. 退出后能确认什么事实？

例如求数组和时，一个有用的不变量是："进入第 `i` 轮前，`sum` 等于前 `i` 个元素之和。"这个描述能帮助发现漏加、重复和边界错误。

```c
int sum = 0;
/* 不变量：sum == arr[0] + ... + arr[i-1] */
for (size_t i = 0; i < length; ++i) {
    sum += arr[i];
}
/* 退出后：sum == arr[0] + ... + arr[length-1] */
```

在调试时，可以在循环体开头加 `assert` 验证不变量是否成立：

```c
#include <assert.h>
/* ...（验证代码，发布前可用 NDEBUG 禁用）*/
```

## `break` 与 `continue`

`break` 只退出最内层循环；`continue` 跳过本轮剩余部分并进入下一轮。它们适合提前结束搜索或跳过无效元素，但过多使用会增加执行路径数量。

```c
for (size_t i = 0; i < length; ++i) {
    if (values[i] < 0) {
        continue;  /* 跳过负数 */
    }
    if (values[i] == target) {
        found = true;
        break;     /* 找到后立即停止 */
    }
}
```

`break` 不会跨越多层循环。如果需要从内层退出多层循环，可以使用标志变量或将循环封装为函数后用 `return`。

在 `switch` 内部的 `break` 只退出 `switch`，不影响外层循环：

```c
for (size_t i = 0; i < length; ++i) {
    switch (values[i]) {
    case 0:
        break;  /* 只退出 switch，循环继续 */
    case -1:
        goto done;  /* 这种场景是 goto 少数合理用法之一 */
    }
}
done:;
```

## `goto` 的合法场景：多步骤资源清理

`goto` 在现代 C 中有且只有一个广泛认可的用途：**在函数末尾集中释放资源**。当函数需要依次获取多个资源，且任何一步都可能失败时，`goto` 能避免深层嵌套或重复的清理代码：

```c
int init_system(void) {
    FILE *config = fopen("config.txt", "r");
    if (config == NULL) goto fail_config;

    char *buffer = malloc(BUF_SIZE);
    if (buffer == NULL) goto fail_buffer;

    int fd = open_device("/dev/hw0");
    if (fd < 0) goto fail_device;

    /* 全部成功，正常使用 */
    process(config, buffer, fd);

    /* 正常清理 */
    close(fd);
    free(buffer);
    fclose(config);
    return 0;

fail_device:
    free(buffer);
fail_buffer:
    fclose(config);
fail_config:
    return -1;
}
```

这个模式在 Linux 内核和 CPython 中极其常见。注意 `goto` 只向前跳转到函数内的标签，不跨越函数。第 09 章会详细展开错误处理策略。

除此之外，避免使用 `goto`。跳出多层循环优先用函数封装+`return`。Python 没有 `goto`，所以对 Python 开发者来说，将它限制在资源清理场景就足够了。

## 死代码与不可达路径

死代码（dead code）是永远不会执行的代码。编译器通过静态分析能发现部分不可达路径：

```c
int compute(int x) {
    if (x > 0) {
        return x * 2;
    } else {
        return -x;
    }
    printf("done\n");  /* 警告：永远不会执行 */
}
```

使用 `-Wunreachable-code`（某些编译器）或 `-Wall` 配合 `-O2` 可以发现更多此类问题。

死代码不仅浪费阅读者的时间，还可能隐藏 bug——也许原本需要执行但因为早期的 `return` 而被跳过：

```c
/* 真实 bug：free 永远不会执行 */
char *format_message(const char *msg) {
    char *buf = malloc(256);
    if (buf == NULL) return NULL;
    snprintf(buf, 256, "[LOG] %s", msg);
    return buf;
    free(buf);  /* 死代码，内存泄漏已经由 return buf 处理 */
}
```

另一个常见情况是 `switch` 中 `break` 后面的代码：

```c
switch (op) {
case OP_ADD:
    result = a + b;
    break;
    validate(result);  /* 死代码 */
case OP_SUB:
    ...
}
```

应对策略：

- 编译时开启 `-Wall -Wextra`，认真对待每一条警告。
- 使用静态分析工具（如 `cppcheck`、`clang-tidy`）扫描不可达代码。
- 定期清理注释掉的代码——版本控制系统已保留历史，不需要注释来"保存"旧代码。

## 常见错误

- **赋值代替比较**：`if (x = 0)` 永远为假。开启 `-Wall` 或将常量放左边 `if (0 == x)` 可以防范。
- **使用 `<= length` 访问数组**：合法索引是 `0` 到 `length - 1`，`arr[length]` 是越界。
- **忘记更新循环状态**：导致无限循环。检查每条路径是否都推进了状态。
- **无符号变量为 `0` 时执行 `--i`**：`size_t` 减到 `0` 后再减会回绕到极大值，循环永不结束。
- **`switch` 中漏写 `break`**：意外贯穿。使用 `[[fallthrough]]`（C23）或注释标记有意贯穿。
- **修改循环索引的同时在循环头更新**：索引可能跳过元素或重复处理。
- **只测试正常输入**：应覆盖零次迭代、一次迭代、边界值和空输入。
- **混用 `&`/`&&` 或 `|`/`||`**：按位运算不短路，用于条件判断时行为不同且不安全。
- **三元嵌套**：超过一层就应改用 `if`。
- **`goto` 向后跳转或跨作用域**：会跳过变量初始化，造成未定义行为。
- **不可达代码后面有清理逻辑**：如 `return` 后面的 `free()` 永不执行，造成资源泄漏。
- **`for` 中逗号表达式的副作用顺序理解错误**：逗号左侧先求值，但不要让表达式之间有依赖。

## 检查点

1. `for (size_t i = length - 1; i >= 0; --i)` 为什么可能永不结束？（提示：`size_t` 是无符号类型。）
2. `break` 会不会同时退出两层嵌套循环？如果不会，有什么替代方案？
3. FizzBuzz 为什么必须先判断同时被 3 和 5 整除？
4. `if (ptr && ptr->next)` 中，如果 `ptr` 为 `NULL`，`ptr->next` 会被执行吗？为什么？
5. 对枚举类型的 `switch` 加 `default` 有什么副作用？什么时候该加，什么时候不该加？
6. 下面的代码有什么问题？

```c
int x = 10;
int result = (x > 5) ? x-- : x++;
printf("x=%d, result=%d\n", x, result);
```

7. 为什么 `goto` 只能向前跳转到清理标签，不应该向后跳转？
8. 在什么情况下 `while (1)` 配合 `break` 比标志控制循环更清晰？

## 动手练习

1. **FizzBuzz 升级版**：完成 `exercises/02_fizzbuzz.c`，输出 1 到 100。验收时确认 15 输出 `FizzBuzz`，而不是只输出 `Fizz`。额外要求：用 `switch` + 对 15 取模的余数实现另一个版本，比较两种写法的可读性。

2. **数组搜索**：编写函数查找数组中第一个负数的索引。分别测试空数组、首元素命中、末元素命中和没有命中。使用提前返回风格。

3. **循环不变量追踪**：用表格手工跟踪一个循环的 `i`、条件和累计值，再运行程序核对。

4. **资源清理模式**：编写一个函数，依次打开文件、分配缓冲区、创建临时文件。任何一步失败都用 `goto` 清理已获取的资源并返回错误码。验证每种失败路径都不会泄漏资源。

5. **短路安全**：编写一个函数 `safe_get_length(const char *s)`，当 `s` 为 `NULL` 时返回 `0`，否则返回 `strlen(s)`。要求用一行 `return` 加短路运算实现（不用 `if`）。

6. **消除嵌套**：找到下面代码中的三层嵌套，用守卫子句重写：

```c
int parse_and_process(const char *input, Config *cfg) {
    if (input != NULL) {
        if (strlen(input) > 0) {
            if (cfg != NULL && cfg->enabled) {
                return do_parse(input, cfg);
            }
        }
    }
    return -1;
}
```

7. **双重循环退出**：在 10x10 的二维数组中搜索某个值，分别用（a）标志变量、（b）封装为函数两种方式实现。比较代码行数和清晰度。
