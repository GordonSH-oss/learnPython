# 22 用 C 模拟面向对象

## 学习目标

完成本章后，你应该能够：

- 理解“对象”在机器层面可以拆成状态、行为和生命周期
- 使用结构体保存对象状态，使用接收对象指针的函数实现方法
- 使用头文件、不透明指针和命名约定实现封装
- 使用结构体嵌入模拟继承，使用函数指针表实现动态多态
- 识别手动模拟面向对象时的类型、内存和所有权风险

## 先运行示例

```bash
make build/examples/22_oop_in_c
./build/examples/22_oop_in_c
```

## C 真的不能把数据和逻辑放在一起吗

C 的结构体只能直接保存数据，不能像 C++、Java 或 Python 那样在类型定义中声明方法：

```c
typedef struct {
    double x;
    double y;
} Point;

void point_move(Point *self, double dx, double dy) {
    self->x += dx;
    self->y += dy;
}
```

从语法上看，`Point` 和 `point_move` 确实是分开的。但是面向对象的关键不在于函数必须写进结构体，而在于程序是否建立了下面三个关系：

```text
对象 = 状态 + 可作用于该状态的行为 + 生命周期约定
```

这里：

- `Point` 保存状态。
- `point_move` 保存行为。
- `Point *self` 指出该行为作用于哪个对象。
- `point_` 前缀把类型及其操作组织成一个逻辑模块。

面向对象语言中的 `this` 或 `self` 通常也是一个隐式传入的对象指针。C 只是要求程序员显式写出来。

下面两段代码表达的是同一个核心操作：

```cpp
point.move(2, 3);        // C++：编译器隐式传入 &point
```

```c
point_move(&point, 2, 3); // C：调用者显式传入 &point
```

## 第一步：结构体加普通函数就是最小对象模型

```c
typedef struct {
    const char *name;
    int balance;
} Account;

void account_init(Account *self, const char *name, int balance) {
    self->name = name;
    self->balance = balance;
}

bool account_deposit(Account *self, int amount) {
    if (self == NULL || amount <= 0) {
        return false;
    }
    self->balance += amount;
    return true;
}
```

这已经具备面向对象的几个基本特征：

| 面向对象概念 | C 中的实现 |
| --- | --- |
| 类或对象类型 | `struct Account` |
| 字段 | 结构体成员 |
| 方法 | 接收 `Account *self` 的函数 |
| 构造 | `account_init` 或 `account_create` |
| 析构 | `account_destroy` |
| 方法调用 | `account_deposit(&account, 100)` |

`self` 不是 C 关键字，只是常用命名。也可以写成 `account`，但统一使用 `self` 能突出“这是当前对象”。

## 第二步：用模块边界实现封装

仅靠结构体不能阻止调用者直接修改字段：

```c
Account account;
account.balance = -1000000;
```

如果需要真正隐藏数据，可以在头文件中只声明类型，不公开结构体布局。这称为不透明类型或不透明指针。

`account.h`：

```c
typedef struct Account Account;

Account *account_create(const char *name, int balance);
bool account_deposit(Account *self, int amount);
int account_balance(const Account *self);
void account_destroy(Account *self);
```

`account.c`：

```c
struct Account {
    char *name;
    int balance;
};
```

调用者只知道 `Account *`，不知道 `struct Account` 有哪些字段，因此不能绕过接口直接改余额。封装来自三个部分：

- 头文件公开稳定接口。
- `.c` 文件保存私有布局和实现。
- `static` 函数和变量只在当前源文件内可见。

C 没有 `public`、`private` 关键字，但链接边界和不透明类型可以提供实际的信息隐藏。

## 第三步：用结构体嵌入模拟继承

C 没有语言级继承，但可以把“基类”结构体放在“派生类”结构体的第一个成员：

```c
typedef struct {
    const char *name;
} Animal;

typedef struct {
    Animal base;
    int remaining_tricks;
} Dog;
```

内存布局可以理解为：

```text
Dog
+--------------------------+
| Animal base              |  <- Dog 地址也是首成员 base 的地址
|   const char *name       |
+--------------------------+
| int remaining_tricks     |
+--------------------------+
```

因为 `base` 是第一个成员，`Dog *` 和 `&dog->base` 指向同一个起始地址。向上转换时应明确写出：

```c
Animal *animal = &dog->base;
```

这种方式模拟的是“派生对象包含一个基类子对象”。它不是 C 编译器提供的继承，类型关系和转换规则都必须由接口约定维护。

如果基类不是第一个成员，直接把派生类指针强制转换成基类指针会得到错误地址。更稳妥的做法始终是使用 `&derived->base`。

## 第四步：用函数指针表实现动态多态

仅有结构体嵌入还不能根据对象的实际类型选择不同实现。动态多态需要在运行时找到正确的函数。常见做法是为基类对象保存一个虚函数表指针：

```c
typedef struct Animal Animal;

typedef struct {
    void (*speak)(const Animal *self);
    void (*destroy)(Animal *self);
} AnimalVTable;

struct Animal {
    const AnimalVTable *vtable;
    const char *name;
};
```

对象不直接保存函数实现，只保存一个指向函数表的指针：

```text
Dog object                         DOG_VTABLE
+----------------------+          +----------------------+
| base.vtable ----------+--------> | speak: dog_speak     |
| base.name            |          | destroy: dog_destroy |
| remaining_tricks     |          +----------------------+
+----------------------+
```

统一的基类接口负责分派：

```c
void animal_speak(const Animal *self) {
    if (self != NULL && self->vtable != NULL && self->vtable->speak != NULL) {
        self->vtable->speak(self);
    }
}
```

不同类型安装不同函数表：

```c
static const AnimalVTable DOG_VTABLE = {
    .speak = dog_speak,
    .destroy = dog_destroy,
};

static const AnimalVTable CAT_VTABLE = {
    .speak = cat_speak,
    .destroy = cat_destroy,
};
```

调用者只持有 `Animal *`，却能获得不同结果：

```c
Animal *animals[] = {dog_as_animal(dog), cat_as_animal(cat)};

for (size_t i = 0; i < 2; ++i) {
    animal_speak(animals[i]);
}
```

`animal_speak` 相当于虚方法调用。执行哪个 `speak` 不是编译时写死的，而由对象中的 `vtable` 在运行时决定。

## 派生方法如何找回完整对象

虚函数接收的是 `Animal *`，但 `dog_speak` 可能需要访问 `Dog` 独有的字段：

```c
static void dog_speak(const Animal *animal) {
    const Dog *self = (const Dog *)animal;
    printf("%s says woof; tricks=%d\n",
           self->base.name, self->remaining_tricks);
}
```

这个向下转换成立的前提是：

- `Animal base` 是 `Dog` 的第一个成员。
- 当前对象确实是一个 `Dog`。
- 对象在整个调用期间仍然有效。

C 不会自动检查这些条件。大型项目常加入类型标签或运行时断言：

```c
typedef enum {
    ANIMAL_DOG,
    ANIMAL_CAT
} AnimalKind;

struct Animal {
    const AnimalVTable *vtable;
    AnimalKind kind;
    const char *name;
};
```

如果只是需要表示少量固定类型，`enum + union + switch` 往往比虚函数表更简单、更容易检查。函数指针表更适合类型会扩展、调用者不应依赖具体类型的场景。

## 生命周期：构造、析构与所有权

C 不会自动调用构造函数或析构函数，必须明确约定生命周期：

```c
Dog *dog_create(const char *name, int remaining_tricks);
void animal_destroy(Animal *self);
```

常见规则是：

- `*_init` 初始化调用者提供的内存，不负责 `free`。
- `*_deinit` 清理 `*_init` 创建的内部资源，不释放对象本身。
- `*_create` 在堆上创建对象并返回所有权。
- `*_destroy` 清理内部资源并释放对象。
- `const Type *` 表示方法不应修改对象的可观察状态。

如果通过 `Animal *` 销毁派生对象，析构函数也必须是多态的。否则基类代码不知道对象真实大小，也不知道派生类持有哪些额外资源。

```c
void animal_destroy(Animal *self) {
    if (self != NULL && self->vtable != NULL && self->vtable->destroy != NULL) {
        self->vtable->destroy(self);
    }
}
```

## 数据和逻辑究竟在哪里“合到一起”

C 通常有三种组织层次：

```text
编译期组织
  类型名 + 函数名前缀 + 头文件接口

调用时绑定
  普通函数 + 显式 self 指针

运行时绑定
  对象中的 vtable 指针 + 函数指针表
```

所以 C 并不是把函数代码复制进每个对象。面向对象语言通常也不会这样做。函数代码一般只存在一份；对象保存自己的数据，调用方法时传入对象地址。需要动态多态时，对象再额外保存一个能定位方法实现的指针。

## 与原生面向对象语言相比

| 能力 | C 的模拟方式 | 代价 |
| --- | --- | --- |
| 对象状态 | 结构体 | 直接、无额外成本 |
| 实例方法 | 普通函数 + `self` | 调用语法较长 |
| 封装 | 不透明类型 + `.c` 文件 | 需要规划模块接口 |
| 继承 | 首成员嵌入 | 编译器不检查继承关系 |
| 虚方法 | 函数指针表 | 间接调用和手动初始化 |
| 构造与析构 | `init/create/deinit/destroy` | 容易漏掉清理 |
| 接口 | 约定统一的函数表 | 缺少语言级类型检查 |
| 泛型行为 | `void *`、宏或函数指针 | 类型安全较弱 |

C 的优势是布局和调用成本完全可见，适合操作系统、嵌入式、驱动和 ABI 稳定的库。代价是编译器提供的保护较少，正确性更依赖接口设计和测试。

## 什么时候值得这样做

适合使用对象式设计的场景：

- 多种实现需要共享统一接口，例如文件、内存和网络输出流。
- 库需要隐藏内部结构，避免调用者依赖字段布局。
- 状态与一组操作必须始终遵守同一套不变量。
- 框架需要通过回调或插件注册扩展行为。

不适合为了“看起来像类”而机械套用。简单数据可以直接使用结构体，固定的少量分支可以使用 `enum + switch`，无状态计算可以保留为普通函数。C 中好的抽象通常比完整复刻 C++ 类系统更重要。

## 常见错误

- 忘记初始化 `vtable`，调用空指针或垃圾地址
- 把并非某派生类型的基类指针强制向下转换
- 假设任意成员位置都能进行基类、派生类指针转换
- 用基类析构逻辑释放派生对象，导致资源泄漏
- 同时混用栈对象和堆对象，却没有区分 `deinit` 与 `destroy`
- 将借用的字符串当作拥有的内存释放，或忘记复制需要长期保存的字符串
- 暴露私有结构体后仍声称字段不可修改
- 设计过深的继承层次，使手动类型约定难以维护

## 检查点

1. 为什么 `point_move(&point, 2, 3)` 可以看作方法调用？
2. 不透明类型如何阻止调用者直接访问结构体字段？
3. 为什么派生结构体通常把基类结构体放在第一个成员？
4. `vtable` 如何让同一个 `animal_speak` 调用不同实现？
5. 为什么通过基类指针销毁对象时，析构函数也需要多态？

## 动手练习

1. 为示例增加 `Bird` 类型，实现自己的 `speak` 和 `destroy`。
2. 给 `Animal` 增加 `move` 虚方法，让不同动物以不同方式输出移动行为。
3. 增加 `AnimalKind`，在向下转换前使用 `assert` 检查实际类型。
4. 把示例拆成 `animal.h`、`animal.c`、`dog.c`、`cat.c` 和 `main.c`，并隐藏具体结构体。
5. 用 `enum + union + switch` 重写示例，比较它与虚函数表方案的扩展性和类型安全。
