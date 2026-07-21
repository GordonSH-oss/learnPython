# 09 文件与错误处理

## 学习目标

完成本章后，你应该能够：

- 安全打开、读取、写入和关闭文本或二进制文件
- 区分 EOF、解析失败和 I/O 错误
- 设计调用者可以处理的错误返回值
- 在多条失败路径上正确释放已获得资源
- 处理部分读取、部分写入和关闭阶段错误

## 文件流生命周期

```text
fopen -> 检查 -> 读写 -> 检查流状态 -> fclose
```

```c
FILE *file = fopen(path, "r");
if (file == NULL) {
    perror(path);
    return 1;
}

/* 使用 file */

if (fclose(file) != 0) {
    perror("fclose");
    return 1;
}
```

写入可能先停留在用户态缓冲区，因此 `fprintf` 成功后，`fflush` 或 `fclose` 仍可能因磁盘空间、设备或网络文件系统错误而失败。

## 文本读取

`fgets` 适合逐行读取，但要区分正常结束和错误：

```c
char line[256];
while (fgets(line, sizeof line, file) != NULL) {
    /* 处理本次读取到的内容；一行过长时可能分成多次。 */
}

if (ferror(file)) {
    perror("read");
}
```

`fscanf` 返回成功转换的字段数量。返回 `EOF` 可能表示输入结束，也可能表示读取错误；格式不匹配时可能返回 `0`，并把不匹配输入留在流中。因此面向用户输入时，先读取整行再用 `strtol` 等函数解析通常更容易恢复。

## 二进制读写与部分完成

`fread` 和 `fwrite` 以“元素”为单位返回实际完成数量：

```c
size_t written = fwrite(values, sizeof values[0], count, file);
if (written != count) {
    if (ferror(file)) {
        perror("fwrite");
    }
    /* 文件现在可能只包含前 written 个元素。 */
}
```

一次调用没有完成全部请求时，程序必须决定重试、报告部分成功，还是删除不完整输出。不能把文件写入当作天然事务。

## 错误模型

C 没有标准异常机制。常见接口设计包括：

- 返回 `bool`，通过输出参数返回结果
- 返回枚举错误码，区分无效输入、内存不足和 I/O 错误
- 返回指针，以 `NULL` 表示失败
- 返回已处理数量，让调用者识别部分成功

`errno` 只应在某个 API 的文档明确说明“失败时设置 errno”且返回值已经表示失败后读取。并非所有标准库函数都会设置它，成功调用后也不能把旧 `errno` 当作新错误。

```c
errno = 0;
long value = strtol(text, &end, 10);
if (errno == ERANGE) {
    /* 超出 long 范围 */
}
```

## 资源清理

函数逐步获取多个资源时，可以使用单一清理区：

```c
int copy_file(const char *source_path, const char *target_path) {
    int result = -1;
    FILE *source = NULL;
    FILE *target = NULL;

    source = fopen(source_path, "rb");
    if (source == NULL) goto cleanup;

    target = fopen(target_path, "wb");
    if (target == NULL) goto cleanup;

    /* 复制并检查每一步；成功后 result = 0。 */

cleanup:
    if (target != NULL && fclose(target) != 0) result = -1;
    if (source != NULL && fclose(source) != 0) result = -1;
    return result;
}
```

`goto cleanup` 在这种局部资源回滚场景中可以减少重复代码。关键是所有跳转都只向前进入清理区，不形成难以跟踪的控制流。

## 安全替换文件

覆盖重要文件时，直接打开目标并截断可能在中途失败后丢失旧内容。常见策略是：

1. 在同一文件系统创建临时文件。
2. 写入并检查 `fflush`、`fsync`（需要时）和关闭结果。
3. 使用 `rename` 原子替换目标目录项。

这仍需根据持久性要求处理目录同步和崩溃一致性，但比直接覆盖更容易保留旧数据。

## 常见错误

- 只检查 `fopen`，忽略读取、写入和关闭错误
- 把 EOF 和读取错误混为一谈
- 假定一次写入必定完整
- 解析失败后继续使用未初始化结果
- 打印错误后仍按成功路径运行
- 所有函数都盲目读取 `errno`
- 多条失败路径遗漏关闭或释放

## 检查点

1. `fgets` 返回 `NULL` 是否一定表示错误？
2. 为什么写入函数成功后仍要检查 `fclose`？
3. 为什么 `errno` 必须与具体失败返回值一起解释？

## 动手练习

1. 完成 `exercises/07_word_count.c`，统计行、单词和字节数量。
2. 测试空文件、最后一行没有换行、文件不存在和无权限路径。
3. 修改程序，让读取错误与普通 EOF 返回不同状态。
4. 实现临时文件加 `rename` 的安全保存流程，并设计失败清理。
