# 指针练习索引

配合 `chapters/06-pointers.md` 的三个专项练习，按难度递进。

## 练习列表

### 06_pointer_basics.c — 指针基础

**对应章节**: 06-pointers.md § 2-5, 12

**学习目标**:
- 理解取地址 `&` 和解引用 `*` 的含义
- 掌握输出参数模式（通过指针修改调用者变量）
- 使用指针遍历数组（past-the-end 模式）
- 辨析 `const` 的三种方向

**练习内容**:
1. `swap`: 交换两个整数
2. `safe_divide`: 安全除法，用输出参数返回结果
3. `array_sum`: 用指针而非下标遍历数组求和
4. `find_min_max`: 通过两个输出参数返回最小/最大值
5. `const_quiz`: 通过编译错误理解 const 语义

**编译运行**:
```bash
gcc -Wall -Wextra -g 06_pointer_basics.c -o 06_basics
./06_basics
```

---

### 06_pointer_advanced.c — 指针进阶

**对应章节**: 06-pointers.md § 6-7, 13-14

**学习目标**:
- 熟练使用 `->` 操作结构体指针
- 理解 `void *` 的通用性和限制
- 掌握二级指针修改调用者指针变量
- 理解指针数组与字符串操作
- 使用函数指针实现回调

**练习内容**:
1. `student_set/print`: 结构体指针的读写
2. `generic_swap`: 用 `void *` 实现类型无关的交换
3. `create_array`: 用 `int **` 让调用者获得 malloc 的地址
4. `sort_strings`: 对字符串指针数组排序（只交换指针）
5. `sort_ints`: 用函数指针实现升序/降序排序

**编译运行**:
```bash
gcc -Wall -Wextra -g 06_pointer_advanced.c -o 06_advanced
./06_advanced
```

---

### 06_pointer_pitfalls.c — 指针陷阱

**对应章节**: 06-pointers.md § 11, 15-16

**学习目标**:
- 识别悬垂指针、未初始化指针、use-after-free
- 发现越界访问和内存泄漏
- 学会使用 AddressSanitizer 定位内存错误
- 理解指针类型与字节序的关系

**练习内容**:
1. `dangling_example`: 返回局部变量地址
2. `oob_example`: 数组越界
3. `uninit_example`: 未初始化指针
4. `leak_example`: 提前返回导致内存泄漏
5. `uaf_example`: free 后继续使用
6. `type_confusion`: 观察小端序的字节排列

**使用方法**:
```bash
# 编译时启用 AddressSanitizer
gcc -Wall -Wextra -g -fsanitize=address 06_pointer_pitfalls.c -o 06_pitfalls

# 运行观察报错
./06_pitfalls

# 修复 bug 后重新编译验证
```

**学习流程**:
1. 先阅读源码，在纸上标注哪里有 bug
2. 编译运行，对比 AddressSanitizer 的报错和你的预判
3. 修复每个 TODO 标记的问题
4. 重新编译，直到程序正常输出期望结果
5. 对照 `solutions/` 目录下的答案，理解修复方法

---

## 与综合练习的区别

| 类别 | 编译方式 | 特点 |
|------|----------|------|
| 指针专项 (06_pointer_*.c) | 单文件独立编译 | 聚焦单一概念，快速反馈 |
| 综合练习 (01-14.c) | `make exercises` 统一构建 | 整合多章节知识 |

完成指针专项后，可继续做 `06_dynamic_vector.c`（综合练习），它结合了指针（ch06）和动态内存（ch08）。

---

## 答案位置

所有参考答案在 `solutions/` 目录:
- `solutions/06_pointer_basics.c`
- `solutions/06_pointer_advanced.c`
- `solutions/06_pointer_pitfalls.c`

**建议**: 独立完成后再查看答案，重点对比：
- 边界条件处理（空数组、NULL 指针）
- 内存所有权（谁分配谁释放）
- const 的使用位置
