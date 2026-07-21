# 06 指针

## 学习目标

学完本章后，你应能：

- 用“对象、地址、指针值”解释 `&` 和 `*`。
- 判断一个指针是否可以安全解引用。
- 使用指针遍历数组，并说明合法边界。
- 使用输出参数修改调用者的数据。
- 通过结构体指针访问成员，并读懂 `PyObject *` 这类声明。
- 读懂 `const` 指针、`void *` 和二级指针。
- 识别空指针、未初始化指针、悬空指针和越界指针。

动态内存的分配与释放将在第 08 章展开，函数指针将在第 11 章介绍。本章先建立后续内容依赖的指针模型。

## 对象、地址和指针

C 程序中的变量对应一块可存放值的内存区域。可以把这块区域称为对象。对象有类型、值和生命周期，在其生命周期内还可以取得地址。

```c
int value = 42;
int *p = &value;
```

这两行代码中：

```text
对象                 对象中保存的值
value                42
p                    value 的地址

表达式               结果
&value               value 的地址
*p                   p 所指对象的值，即 42
```

`p` 本身也是一个对象。它的类型是 `int *`，保存的值是另一个对象的地址；`&p` 则是指针对象 `p` 自己的地址。

“指针是带类型的地址”是实用的入门模型。更准确地说，指针是一个值，它可以指向某种类型的对象或函数。指针类型决定：

- 解引用后按什么类型访问对象。
- 指针加减时一步跨过多少个元素。
- 编译器允许通过该指针执行哪些操作。

类型正确并不自动代表地址有效。`int *` 只有在确实指向仍然存活且允许访问的 `int` 对象时，才能安全解引用。

## 取地址与解引用

一元运算符 `&` 取得对象地址，一元运算符 `*` 访问指针所指的对象：

```c
#include <stdio.h>

int main(void) {
    int value = 42;
    int *p = &value;

    printf("before: value=%d, *p=%d\n", value, *p);
    *p = 100;
    printf("after:  value=%d, *p=%d\n", value, *p);
    return 0;
}
```

`*p = 100` 没有修改 `p` 保存的地址，而是沿着这个地址找到 `value` 并修改它。因此最后 `value` 和 `*p` 都是 `100`。

声明中的 `*` 表示变量是指针，表达式中的 `*` 表示解引用。它们使用相同符号，但所处语境不同：

```c
int *p;       // 声明：p 是指向 int 的指针
int n = *p;   // 表达式：读取 p 所指的 int
```

不要在未赋予有效地址时读取 `*p`。更清晰的声明方式是一行声明一个变量：

```c
int *first = NULL;
int *second = NULL;
```

下面的写法容易误读，因为只有 `first` 是指针：

```c
int *first, second;
```

## 空指针

空指针表示“不指向任何对象”。初始化时还没有合理目标的指针，可以设为 `NULL`：

```c
int *p = NULL;

if (p != NULL) {
    printf("%d\n", *p);
}
```

判断空指针是合法的，解引用空指针是未定义行为。未定义行为不保证产生固定错误：程序可能崩溃、输出垃圾值，也可能暂时看似正常。

检查 `p != NULL` 只能排除空指针，不能证明 `p` 一定有效。它仍可能未初始化、已经悬空、指向数组边界之外，或指向不允许通过它访问的对象。

## 用指针修改调用者数据

C 的参数按值传递。函数接收到的是实参值的副本，因此直接修改参数不会改变调用者变量：

```c
void ineffective(int value) {
    value = 100;
}
```

如果传入地址，函数虽然仍然只收到地址值的副本，但该副本和调用者的指针指向同一个对象。函数便可以通过解引用修改调用者对象。

```c
#include <stdbool.h>
#include <stdio.h>

bool divide(int a, int b, int *result) {
    if (b == 0 || result == NULL) {
        return false;
    }

    *result = a / b;
    return true;
}

int main(void) {
    int quotient;

    if (divide(10, 2, &quotient)) {
        printf("quotient=%d\n", quotient);
    }
    return 0;
}
```

数据流如下：

```text
main 中的 quotient
        |
        | &quotient
        v
divide 的 result 参数（地址值的副本）
        |
        | *result = 5
        v
main 中的 quotient 变为 5
```

这里返回值表达操作是否成功，输出参数携带计算结果。这是常见的 C 接口模式。接口应明确说明输出指针能否为 `NULL`、成功时写入什么，以及失败时输出对象是否保持不变。

另一个典型例子是交换两个整数：

```c
void swap(int *a, int *b) {
    int temporary = *a;
    *a = *b;
    *b = temporary;
}

int x = 10;
int y = 20;
swap(&x, &y);
```

调用后 `x` 为 `20`，`y` 为 `10`。实际接口中，如果不允许传入 `NULL`，应在函数契约中明确这一前置条件。

## 结构体指针

指针不仅能指向 `int` 等基础类型，也能指向自定义的结构体类型。下面先用一个简化对象说明语法；结构体的定义、布局和 `typedef` 将在第 07 章继续展开。

```c
typedef struct {
    long reference_count;
    const char *type_name;
} Object;

Object value = {1, "integer"};
Object *object = &value;
```

`object` 的类型是 `Object *`，即“指向 `Object` 的指针”。通过对象访问成员使用 `.`，通过结构体指针访问成员使用 `->`：

这里的 `typedef` 把结构体类型命名为 `Object`。如果结构体只定义了标签 `struct Object`，对应的指针声明应写成 `struct Object *object`；使用 `typedef` 后才可以省略 `struct` 写成 `Object *object`。

```c
printf("%ld\n", value.reference_count);
printf("%ld\n", object->reference_count);

object->reference_count += 1;
printf("%ld\n", value.reference_count); // 2
```

箭头运算符只是更易读的成员访问写法，以下两个表达式等价：

```c
object->reference_count
(*object).reference_count
```

第二种写法中的括号不可省略，因为 `.` 的优先级高于一元 `*`。`*object.reference_count` 会被解释为 `*(object.reference_count)`，但 `object` 是指针，不能直接使用 `.` 访问成员。

结构体指针也常作为函数参数。函数收到的仍然是地址值的副本，但可以通过它修改原结构体：

```c
void retain(Object *object) {
    if (object != NULL) {
        object->reference_count += 1;
    }
}

void print_object(const Object *object) {
    if (object != NULL) {
        printf("%s: %ld\n", object->type_name, object->reference_count);
    }
}
```

`retain` 接收 `Object *`，允许修改所指对象；`print_object` 接收 `const Object *`，不能通过该指针修改结构体成员。两者都必须继续遵守普通指针的有效性规则：指针非空并不充分，对象还必须存活、类型匹配且允许访问。

### 从自定义结构体到 `PyObject *`

Python/C API 中经常出现：

```c
PyObject *object;
```

从 C 语法看，它和 `Object *object` 没有区别：`PyObject` 是一种对象类型，`object` 保存该类型对象的地址。函数也经常接收或返回这种指针：

```c
PyObject *result = PyLong_FromLong(42); // 失败时为 NULL
```

调用成功时，`result` 指向一个 Python 对象。与前面的局部 `Object value` 不同，Python/C API 管理这类对象的创建、类型规则和生命周期；调用者还必须检查错误并遵守“借用引用”与“强引用”等引用所有权约定。因此，理解 `PyObject *` 需要分成两层：

1. C 层：它是一个带类型的结构体指针，适用本章的解引用、`const`、空指针和生命周期规则。
2. Python/C API 层：应使用 `Py_TYPE`、`Py_INCREF`、`Py_DECREF` 等公开 API，并遵守每个函数的引用约定。

前面的 `Object` 只是帮助理解指针语法的教学模型，并不是 CPython 中 `PyObject` 的真实定义。不要根据这个示例猜测 `PyObject` 的字段或内存布局，也不要直接访问未由公开 API 承诺的内部成员。

## 指针与数组

数组元素连续存储。在大多数表达式中，数组名会转换为指向首元素的指针：

```c
int values[] = {10, 20, 30};
int *p = values;  // 等价于 &values[0]
```

数组下标和指针运算紧密相关：

```c
values[2] == *(values + 2)
p[2]      == *(p + 2)
```

数组和指针仍然不是同一种类型。数组包含所有元素；指针只保存一个地址。例如，在数组仍是数组的作用域中，`sizeof values` 是整个数组的字节数，而 `sizeof p` 是指针本身的字节数。

### 用指针遍历数组

```c
#include <stddef.h>
#include <stdio.h>

int main(void) {
    int values[] = {10, 20, 30};
    size_t count = sizeof values / sizeof values[0];
    int *end = values + count;

    for (int *current = values; current < end; ++current) {
        printf("%d\n", *current);
    }
    return 0;
}
```

若 `current` 指向一个 `int` 数组元素，`current + 1` 指向下一个元素。地址跨过多少字节由 `sizeof *current` 决定，而不是固定增加一个字节。

`end` 是末尾后一指针。可以构造它并用它控制循环，但不能解引用：

```text
values      values + 1   values + 2   values + 3
   |             |            |            |
 [10]          [20]          [30]       末尾后一位置
   可解引用      可解引用       可解引用       不可解引用
```

### 指针运算的边界

指针算术不是对任意数字地址做计算。对于数组对象，只能在该数组元素及其末尾后一位置的范围内形成指针。超出这个范围，即使没有立即解引用，也可能已经产生未定义行为。

两个指向同一数组的指针可以相减，结果是相隔的元素数，而不是字节数：

```c
#include <stddef.h>

ptrdiff_t distance = &values[2] - &values[0]; // 结果为 2
```

用 `<`、`<=`、`>`、`>=` 比较元素先后位置时，也应保证两个指针指向同一数组。不要依赖无关对象的地址高低关系。

函数参数中的数组声明会调整为指针，因此函数无法从参数本身推导数组长度：

```c
int sum(const int values[], size_t length) {
    int total = 0;
    for (size_t i = 0; i < length; ++i) {
        total += values[i];
    }
    return total;
}
```

这里的 `const int values[]` 在参数位置等价于 `const int *values`。调用者必须同时提供正确的元素数量。

## 指针与对象生命周期

指针不会延长对象的生命周期。安全解引用前，应同时满足：

1. 指针已经初始化。
2. 指针指向一个仍在生命周期内的对象。
3. 访问没有超出该对象或数组的边界。
4. 指针类型和访问方式适合该对象。
5. 当前操作具有所需的读写权限。

返回局部变量地址会产生悬空指针：

```c
int *invalid_result(void) {
    int value = 42;
    return &value;
} // value 的生命周期在这里结束
```

函数返回后，保存过的地址数值可能仍然存在，但它不再指向一个存活的 `int` 对象。解引用返回的指针属于未定义行为。

指向数组元素的指针也依赖整个数组的生命周期：

```c
int *element;

{
    int values[] = {10, 20, 30};
    element = &values[1];
    printf("%d\n", *element); // 合法，values 仍然存活
}

// 此处 element 已悬空，不能解引用
```

第 08 章会继续讨论动态分配对象的生命周期，以及释放后悬空、重复释放和所有权规则。

## `const` 的方向

`const` 可以约束所指对象，也可以约束指针本身：

- `const int *p`：不能通过 `p` 修改所指的整数，但 `p` 可以改指向。
- `int *const p`：`p` 不能改指向，但可以通过 `p` 修改所指整数。
- `const int *const p`：既不能通过 `p` 修改整数，也不能改变 `p` 的指向。

可以从变量名开始向外读声明：

```c
const int *read_only;             // read_only 是指针，指向 const int
int *const fixed = &value;        // fixed 是 const 指针，指向 int
const int *const both = &value;   // both 是 const 指针，指向 const int
```

将不会修改输入的函数参数声明为指向 `const` 的指针，可以表达接口意图并阻止误写：

```c
int sum(const int *values, size_t length);
```

`const int *` 并不保证底层对象永远不变；它只限制不能通过这个指针修改对象。

## 通用对象指针 `void *`

`void *` 可以保存任意对象指针，常用于通用库接口：

```c
int value = 42;
void *raw = &value;
int *typed = raw;
printf("%d\n", *typed);
```

在 C 中，对象指针可以隐式转换为 `void *`，也可以从 `void *` 转回对象指针。转换回去后必须使用与原对象相符的类型。

`void` 没有大小，因此标准 C 不允许直接解引用 `void *`，也不允许对它做指针算术：

```c
// *raw;      // 错误：不知道应读取什么类型
// raw + 1;   // 非标准 C：不知道一步应跨过多少字节
```

强制类型转换只改变编译器解释表达式的方式，不会验证地址，也不会让无效地址变得有效。函数指针与对象指针是不同类别，不应假定它们都能通过 `void *` 无损转换。

## 二级指针

指针本身也是对象，所以也可以取得指针的地址：

```c
int value = 42;
int *p = &value;
int **pp = &p;

printf("%d\n", **pp);
```

`pp` 的类型是 `int **`：

```text
pp  --指向-->  p  --指向-->  value
*pp            得到 p
**pp           得到 value
```

当函数需要修改调用者的指针变量本身时，需要传入二级指针：

```c
void redirect(int **target, int *replacement) {
    if (target != NULL) {
        *target = replacement;
    }
}

int first = 10;
int second = 20;
int *selected = &first;

redirect(&selected, &second);
printf("%d\n", *selected); // 20
```

`int **` 表示“指向 `int *` 的指针”，并不自动表示二维数组。二维数组的元素布局和指针数组不同，后续遇到相关接口时必须根据真实类型分析。

## 打印和调试指针

使用 `%p` 打印对象指针，并转换为 `void *`：

```c
printf("&value=%p, p=%p\n", (void *)&value, (void *)p);
```

调试指针问题时，按顺序检查：

1. 指针在哪里初始化？
2. 它应指向哪个对象？
3. 该对象何时结束生命周期？
4. 合法范围包含多少个元素？
5. 当前代码是在修改指针，还是修改所指对象？
6. 动态内存由谁释放？

编译器警告和 sanitizer 能帮助发现问题。使用 Clang 或 GCC 时，可以采用：

```bash
cc -std=c17 -Wall -Wextra -Wpedantic \
  -fsanitize=address,undefined -g example.c -o example
./example
```

工具不能替代生命周期和边界推理，但通常能让越界、释放后使用和部分未定义行为更快暴露。

## 常见错误

### 解引用未初始化指针

```c
int *p;
*p = 10; // p 保存的是不确定值
```

### 只检查 `NULL`，忽略生命周期

```c
int *p = invalid_result();
if (p != NULL) {
    printf("%d\n", *p); // p 非空也仍然悬空
}
```

### 解引用末尾后一指针

```c
int values[] = {10, 20, 30};
int *end = values + 3;
printf("%d\n", *end); // 越界访问
```

### 混淆指针和所指对象

```c
p = NULL;  // 修改 p 的指向，不修改原对象
*p = 0;    // 修改所指对象；只有 p 有效时才合法
```

### 假定指针包含数组长度

```c
void inspect(int *values) {
    // sizeof values 只得到指针大小，得不到原数组长度
}
```

## 理解检查

阅读以下代码，不运行程序，先回答每个表达式的结果或合法性：

```c
int values[] = {3, 6, 9};
int *p = &values[1];
int *end = values + 3;

typedef struct {
    int x;
    int y;
} Point;

Point point = {4, 5};
Point *point_ptr = &point;
```

1. `*p` 的值是什么？
2. `p - values` 的结果是什么？
3. `p + 1` 能否解引用？
4. `end` 能否用于比较？
5. `*end` 是否合法？
6. `point_ptr->x` 的值是什么？
7. `(*point_ptr).y` 与 `point_ptr->y` 是否等价？

预期答案：依次为 `6`、`1`、可以且结果为 `9`、可以、不合法、`4`、等价。

## 动手练习

1. 实现 `int sum(const int *values, size_t length)`，分别使用下标和指针遍历，并验证结果一致。
2. 实现 `bool min_max(const int *values, size_t length, int *minimum, int *maximum)`。为空数组或输出指针为 `NULL` 时返回 `false`。
3. 编写 `swap` 并画出调用前后两个指针与两个整数对象的关系。
4. 故意解引用数组的末尾后一指针，使用 AddressSanitizer 运行并阅读报告；随后修复循环边界。
5. 修改 `redirect`，让 `replacement == NULL` 表示清空调用者的指针，并解释为什么仍然需要检查 `target`。
6. 定义一个包含名称和计数值的结构体，分别编写接收 `StructName *` 的修改函数和接收 `const StructName *` 的打印函数，并使用 `->` 访问成员。

完成后，你应能在解引用任意指针前回答四个核心问题：它指向什么、对象是否仍然存活、可以访问多少个元素、当前代码是否有权修改它。
