# 练习说明

每个文件都包含任务和验收条件，并提供一个能编译的起始框架。先删除 `TODO` 附近的占位逻辑再实现。

## 指针专项练习（配合 Chapter 06）

这三个文件需要单独编译，专注于指针概念的理解：

```bash
# 基础：取地址、解引用、输出参数、const 方向
gcc -Wall -Wextra -g -fsanitize=address 06_pointer_basics.c -o 06_basics
./06_basics

# 进阶：结构体指针、void*、二级指针、函数指针
gcc -Wall -Wextra -g -fsanitize=address 06_pointer_advanced.c -o 06_advanced
./06_advanced

# 陷阱：悬垂指针、越界、内存泄漏、use-after-free
gcc -Wall -Wextra -g -fsanitize=address 06_pointer_pitfalls.c -o 06_pitfalls
./06_pitfalls  # 观察 AddressSanitizer 报错，修复后重新编译
```

**学习建议**：
1. 先阅读 `chapters/06-pointers.md` 理解概念
2. 依次完成 basics → advanced → pitfalls
3. pitfalls 文件故意包含 bug，先预判错误位置再运行观察报错
4. 使用 `%p` 格式打印指针地址辅助调试

## 综合练习（使用 make）

其他编号练习整合多个章节知识，使用统一构建系统：

```bash
make exercises
./build/exercises/01_temperature
```

完成后准备正常输入、边界输入和无效输入。最后对比 `solutions`，重点比较错误处理、边界和所有权，不必追求逐行相同。
