# 08 动态内存

## 学习目标

使用 `malloc`、`calloc`、`realloc` 和 `free` 管理运行时内存，并建立所有权规则。

## 栈与堆

普通局部变量通常具有自动存储期，离开作用域后失效。动态分配的对象会一直存在，直到显式 `free`。

```c
int *values = malloc(count * sizeof *values);
if (values == NULL) {
    return 1;
}
/* 使用 values */
free(values);
values = NULL;
```

使用 `sizeof *values` 可避免类型修改后大小表达式不同步。分配可能失败，必须检查结果。

## `realloc` 的安全写法

```c
int *new_values = realloc(values, new_count * sizeof *values);
if (new_values == NULL) {
    free(values);
    return 1;
}
values = new_values;
```

不要直接写 `values = realloc(...)`，失败时会丢失原地址，造成泄漏。

## 所有权

每一块动态内存都应有明确所有者。接口文档要说明函数是借用指针、接管所有权，还是返回需要调用者释放的内存。一次分配对应一次释放。

## 动手练习

完成 `exercises/06_dynamic_vector.c`：实现动态整数数组，长度达到容量时扩大到原来的两倍。用 sanitizer 验证无越界和泄漏。
