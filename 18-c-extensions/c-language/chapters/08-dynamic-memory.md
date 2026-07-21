# 08 动态内存

## 学习目标

完成本章后，你应该能够：

- 使用 `malloc`、`calloc`、`realloc` 和 `free` 管理动态对象
- 在分配前检查大小计算溢出
- 为指针和资源建立明确所有权
- 识别泄漏、重复释放、释放后使用和错误的 `realloc` 写法
- 实现具有失败回滚能力的动态数组

## 为什么需要动态内存

编译时无法确定元素数量，或对象需要在创建函数返回后继续存在时，可以动态分配。动态对象从成功分配开始存在，直到被 `free`；离开创建它的代码块不会自动释放。

```c
#include <stdint.h>
#include <stdlib.h>

if (count > SIZE_MAX / sizeof(int)) {
    return NULL;
}

int *values = malloc(count * sizeof *values);
if (values == NULL && count != 0) {
    return NULL;
}
```

使用 `sizeof *values` 可避免元素类型变化后大小表达式不同步。乘法必须在调用 `malloc` 前检查溢出，否则较大的请求可能回绕成较小分配，随后写入会越界。

## `malloc` 与 `calloc`

`malloc` 返回的字节内容未初始化，读取其中尚未写入的对象值可能产生未定义行为。

```c
int *values = calloc(count, sizeof *values);
```

`calloc` 会把分配区域的所有字节置零，并负责处理元素数量与大小的乘法检查。全零字节通常对应整数零，但不能把这个结论推广到所有可能的 C 类型表示。

## 所有权与生命周期

每块动态内存都应有一个明确的释放责任。接口应说明：

- 借用：函数临时使用指针，不保存也不释放
- 接管：函数成功后负责释放对象
- 返回所有权：调用者获得对象并必须释放
- 共享：多个使用者通过额外协议协调生命周期

```c
free(values);
values = NULL;
```

设为 `NULL` 只能避免通过这个变量再次使用；其他保存了同一地址的指针仍然会悬空。

## 安全使用 `realloc`

`realloc` 可能原地扩展，也可能分配新区域、复制内容并释放旧区域：

```c
if (new_count > SIZE_MAX / sizeof *values) {
    return false;
}

int *new_values = realloc(values, new_count * sizeof *values);
if (new_values == NULL) {
    /* values 仍然有效，由原所有者决定继续使用还是释放。 */
    return false;
}
values = new_values;
```

不要直接写 `values = realloc(values, ...)`，否则失败时会丢失旧地址。也不要依赖 `realloc(ptr, 0)` 的平台差异；需要释放时直接调用 `free(ptr)`。

## 动态数组扩容

扩容通常分为四步：

1. 判断是否需要扩容。
2. 计算新容量并检查加倍和字节乘法溢出。
3. 用临时指针调用 `realloc`。
4. 只有成功后才提交新指针和新容量。

```text
旧状态 --分配失败--> 旧状态保持有效
   |
   +----分配成功--> 同时更新 data 和 capacity
```

这是一种事务式更新：失败不能留下“指针已改变但容量没改变”的半成品状态。

## 常见错误

- 未检查 `count * sizeof element` 溢出
- 读取 `malloc` 返回的未初始化内容
- 忘记释放导致泄漏
- 同一块内存释放两次
- `free` 后继续读写
- 丢失唯一指针导致无法释放
- `realloc` 失败后覆盖旧指针
- 不清楚任务参数或容器元素由谁释放

## 使用 sanitizer

```bash
clang -std=c17 -Wall -Wextra -Wpedantic \
  -fsanitize=address,undefined -fno-omit-frame-pointer -g \
  examples/08_dynamic_memory.c -o /tmp/dynamic-memory
/tmp/dynamic-memory
```

AddressSanitizer 能发现许多越界、重复释放和释放后使用问题，但仍不能替代所有权设计和分配失败测试。

## 检查点

1. `free(NULL)` 是否安全？是，什么也不做。
2. `realloc` 失败后旧指针是否仍然有效？在非零大小请求下是。
3. 把一个指针设为 `NULL` 是否会修复其他别名的悬空问题？不会。

## 动手练习

完成 `exercises/06_dynamic_vector.c`：

1. 实现动态整数数组，容量不足时扩为原来的两倍。
2. 检查容量加倍和字节数乘法溢出。
3. 让扩容失败保持原数组完全可用。
4. 用 sanitizer 验证无越界、重复释放和释放后使用。
