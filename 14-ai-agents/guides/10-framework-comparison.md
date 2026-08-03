# 10 纯 Python、OpenAI Agents SDK 与 LangGraph

## 学习目标

能够把同一 Agent 概念映射到三种实现，并根据控制、持久化、生态和维护成本选择工具。

## 要看的代码

- `examples/offline_agent.py`
- `examples/framework_openai_agents.py`
- `examples/framework_langgraph.py`

## 对照

| 能力 | 纯 Python | OpenAI Agents SDK | LangGraph |
| --- | --- | --- | --- |
| Loop | 完全显式 | Runner 管理 | graph 节点与边 |
| Tool | 自定义 schema/registry | `function_tool` 等 | tool node 或自定义节点 |
| State | 自定义 dataclass | session/context 抽象 | typed graph state |
| Handoff | 自行路由 | agent handoff | 条件边或子图 |
| Durable | 自行实现 | 取决于 session/integration | checkpointer 是核心能力 |
| 调试 | 自己记录 trace | SDK tracing | graph execution trace |

## 执行路径

先运行离线版本理解两次模型调用。OpenAI Agents SDK 示例用装饰器把函数转换为 tool，并由 Runner 驱动 loop。LangGraph 示例把状态更新写成节点，用边显式表达控制流。

## 底层机制

框架减少样板代码，也固定了状态和生命周期模型。选择前先确认是否需要 provider-independent 模型、持久图、复杂人机协作或快速 handoff。不要在同一核心流程混用多个 runner。

## 检查点与练习

画出三个示例的调用图，标记谁拥有 loop、state 和 tool execution。把审批节点映射到三种实现，比较改动范围。

## 常见错误与生产注意

- 直接从框架 quickstart 推导生产架构。
- 未锁定版本却依赖实验性 API。
- 把业务状态存进框架内部消息对象。
- 迁移框架时同时改 prompt、模型和测试，无法定位回归来源。
