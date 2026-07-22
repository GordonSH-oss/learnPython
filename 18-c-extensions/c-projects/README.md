# C 语言综合项目

本目录面向已经完成 [`../c-language`](../c-language/README.md) 的学习者。每个项目都可以独立编译、运行和测试，重点是把类型、指针、动态内存、文件、错误处理和多文件构建组合成真实程序。

## 项目列表

| 项目 | 核心能力 | 难度 |
| --- | --- | --- |
| [学生成绩管理系统](student-manager/README.md) | CRUD、排序、统计、TSV 持久化 | 基础综合 |
| [个人记账系统](expense-tracker/README.md) | 金额模型、分类汇总、CSV 持久化 | 中级 |
| [文本分析器](text-analyzer/README.md) | 流式 I/O、哈希词频、Top N | 中级 |

## 统一命令

```bash
make all
make test
make sanitize
make clean
```

也可以进入任意子项目单独运行。

## 推荐学习方式

1. 先阅读项目 README 中的领域模型和验收场景。
2. 运行测试，确认基线通过。
3. 从 `include/` 的公共接口开始阅读。
4. 沿 `app/main.c -> src/` 跟踪一次完整命令。
5. 完成 README 中的扩展练习，并先添加测试。

项目统一遵循：CLI 不直接操作内部数组，领域模块不打印终端文案，存储模块只处理序列化和文件错误。

