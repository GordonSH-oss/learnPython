# 08 状态、Checkpoint 与持久执行

## 学习目标

能够保存和恢复 Agent 状态，设计人工审批与取消点，并避免恢复时重复执行副作用。

## 要看的代码

- `agent_core/checkpoint.py`：内存与 JSON checkpointer。
- `agent_core/runner.py`：每轮工具执行后的保存位置。

## 概念模型

状态机使用 `ready -> running -> waiting_approval/completed/stopped/failed`。checkpoint 至少包含消息、步骤、工具结果、预算、待处理动作和版本。

## 执行路径

runner 在工具结果进入状态后保存 checkpoint。恢复时加载同一 `session_id`，工具注册表用稳定 call id 返回缓存结果，防止重复副作用。

## 底层机制

精确一次执行通常无法由 Agent 单独保证。实际依赖幂等键、数据库事务、outbox 或下游去重。checkpoint schema 需要版本，部署新代码时要考虑旧任务迁移。

## 检查点与练习

让任务在一次工具调用后达到 `max_steps`，读取 checkpoint，再提供下一条模型响应继续。为 `send_email` 设计 `prepared -> approved -> committed` 状态。

## 常见错误与生产注意

- 工具成功后、checkpoint 前进程崩溃造成模糊状态。
- 把不可序列化客户端对象放进 state。
- 恢复时使用了不同版本的 prompt 或工具 schema。
- 没有取消、过期和人工拒绝路径。
