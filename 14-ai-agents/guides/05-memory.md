# 05 Memory：记什么、何时记、如何忘

## 学习目标

区分 working、conversation、episodic、semantic 与 procedural memory，并实现作用域、召回、更新、持久化和删除。

## 要看的代码

- `agent_core/memory.py`：内存与 JSON store、裁剪和摘要。

## 概念模型

| 类型 | 内容 | 生命周期 |
| --- | --- | --- |
| Working | 当前任务中间状态 | 一次运行 |
| Conversation | 最近消息与摘要 | 一个会话 |
| Episodic | 某次任务发生了什么 | 跨会话、可过期 |
| Semantic | 用户事实与偏好 | 跨会话、需更新删除 |
| Procedural | 系统流程与策略 | 通常由开发者版本化 |

RAG 文档是外部知识，不应自动当作用户记忆。checkpoint 是执行快照，也不等于 memory。

## 执行路径

`MemoryRecord` 用 `session_id + key` 建立作用域和更新语义。`InMemoryStore.search()` 只返回有词项重合的记录；`JsonMemoryStore` 展示持久化边界。`trim_messages()` 保留 system 与最近消息，摘要则把旧历史压缩成有损表示。

## 底层机制

长期 memory 是一次写入决策：先判断是否稳定、是否有价值、是否获得授权，再抽取结构化事实。召回需要相关性、时效性和作用域过滤，不能简单把全部记录塞回 prompt。

## 检查点与练习

写入“用户暂时在上海出差”和“用户偏好 Python”，为两者设计不同过期策略。测试两个 session 不能互相召回，并实现冲突更新与用户删除。

## 常见错误与生产注意

- 每句话都写长期 memory，积累噪声和隐私风险。
- 摘要覆盖原始证据且不可追溯。
- 用户更正事实后保留冲突旧值。
- 没有租户隔离、加密、保留期限和删除接口。
