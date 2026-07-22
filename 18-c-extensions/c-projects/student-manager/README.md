# 学生成绩管理系统

## 学习目标

- 用 `Student` 实体保存学号、姓名和 0–100 分成绩
- 用动态数组实现增删查、排序和统计
- 用 TSV 文件保存数据
- 将 CLI、领域逻辑和存储代码分层

## 领域规则

- 学号必须为正整数且唯一。
- 姓名不能为空且必须装入固定容量。
- 成绩必须位于 0–100。
- 空集合没有平均值、最低分和最高分。

## 运行

```bash
make test
./build/student-manager students.tsv add 1 Ada 91.5
./build/student-manager students.tsv add 2 Grace 96
./build/student-manager students.tsv list
./build/student-manager students.tsv find 1
./build/student-manager students.tsv stats
./build/student-manager students.tsv remove 1
```

`list` 按成绩降序显示。数据格式为：

```text
ID<TAB>NAME<TAB>SCORE
```

## 阅读顺序

1. `include/student.h`：实体和校验。
2. `include/student_registry.h`：集合契约。
3. `src/student_registry.c`：扩容、删除、统计和排序。
4. `src/student_store.c`：文件边界。
5. `app/main.c`：命令解析和错误展示。

## 扩展练习

1. 增加 `update ID SCORE`，先写重复 ID 和非法成绩测试。
2. 增加按姓名查找和按姓名排序。
3. 增加课程字段，把单一成绩升级为多科成绩。
4. 保存时先写临时文件，再用 `rename` 替换，避免中途失败破坏旧文件。
5. 把固定姓名数组改为动态字符串，重新设计复制和释放规则。

