# 05 数组与字符串

## 学习目标

理解连续存储、索引边界、数组退化和以空字符结尾的 C 字符串。

## 数组

```c
int scores[] = {90, 85, 78};
size_t count = sizeof scores / sizeof scores[0];
```

这个长度计算只在数组仍是数组的作用域有效。数组作为函数参数时会转换为指向首元素的指针，因此函数必须额外接收长度。

C 不做数组边界检查。读取 `scores[3]` 属于未定义行为，可能看似运行、输出垃圾值或崩溃。

## 字符串

C 字符串是以 `\0` 结束的字符序列。字符串 `"cat"` 实际占 4 字节。常用 `<string.h>` 函数包括 `strlen`、`strcmp`、`memcpy` 和 `strchr`。

```c
char name[20] = "Ada";
printf("%zu\n", strlen(name));
```

读取一行优先使用 `fgets`，因为它知道缓冲区大小。`fgets` 可能保留换行符，可以使用 `strcspn` 去除：

```c
name[strcspn(name, "\n")] = '\0';
```

不要把字符串字面量交给可修改的 `char *`。使用 `const char *message = "hello";` 表达只读意图。

## 动手练习

完成 `exercises/04_string_tools.c`，手动统计字母、数字和空白字符，并实现原地反转字符串。
