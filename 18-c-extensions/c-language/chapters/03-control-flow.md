# 03 分支与循环

## 学习目标

完成本章后，你应该能够：

- 使用 `if`、`else if` 和 `switch` 表达互斥规则
- 根据循环状态选择 `for`、`while` 或 `do ... while`
- 通过循环不变量和边界条件判断循环是否正确
- 识别赋值误写、越界、无限循环和意外贯穿等问题

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

开启警告通常能发现这种错误。若确实需要在条件中赋值，应使用括号明确意图并检查结果。

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

没有 `break` 时会继续执行后续 case，这称为贯穿。只有确实需要时才这样做，并用注释说明意图。外部输入可能包含未列出的值，因此通常保留 `default` 防御路径。

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

## 用状态推理循环

写循环前回答：

1. 初始状态是什么？
2. 循环继续时必须满足什么条件？
3. 每轮怎样改变状态并接近终止？
4. 退出后能确认什么事实？

例如求数组和时，一个有用的不变量是：“进入第 `i` 轮前，`sum` 等于前 `i` 个元素之和。”这个描述能帮助发现漏加、重复和边界错误。

## `break` 与 `continue`

`break` 只退出最内层循环；`continue` 跳过本轮剩余部分并进入下一轮。它们适合提前结束搜索或跳过无效元素，但过多使用会增加执行路径数量。

```c
for (size_t i = 0; i < length; ++i) {
    if (values[i] < 0) {
        continue;
    }
    if (values[i] == target) {
        found = true;
        break;
    }
}
```

## 常见错误

- 使用 `<= length` 访问数组末尾后一项
- 忘记更新循环状态导致无限循环
- 在无符号变量为 `0` 时执行 `--i`，产生回绕
- `switch` 中漏写 `break`
- 修改循环索引的同时又在循环头更新它
- 只测试普通输入，没有测试零次、一次和最后一次迭代

## 检查点

1. `for (size_t i = length - 1; i >= 0; --i)` 为什么可能永不结束？
2. `break` 会不会同时退出两层嵌套循环？
3. FizzBuzz 为什么必须先判断同时被 3 和 5 整除？

## 动手练习

1. 完成 `exercises/02_fizzbuzz.c`，输出 1 到 100。验收时确认 15 输出 `FizzBuzz`，而不是只输出 `Fizz`。
2. 编写函数查找数组中第一个负数，分别测试空数组、首元素命中、末元素命中和没有命中。
3. 用表格手工跟踪一个循环的 `i`、条件和累计值，再运行程序核对。
