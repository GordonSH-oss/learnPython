# 01 Agent 基础：先判断是否真的需要 Agent

## 学习目标

能够区分 chatbot、workflow 与 Agent，并把 Agent 描述为“模型驱动的受约束状态机”，而不是一个会自主完成一切的模型。

## 要看的代码

- `agent_core/types.py`：消息、动作、状态和结果。
- `examples/offline_agent.py`：最小可运行闭环。

## 概念模型

| 系统 | 下一步由谁决定 | 适合任务 |
| --- | --- | --- |
| Chatbot | 用户与固定对话逻辑 | 问答、改写、分类 |
| Workflow | 程序代码 | 流程稳定、可枚举的任务 |
| Agent | 模型在程序约束内选择动作 | 路径未知、需要动态取证或工具组合的任务 |

一个 Agent 至少包含目标、状态、可用动作、环境反馈和停止条件。模型不是系统本身；权限、执行和持久化属于宿主程序。

## 执行路径

`offline_agent.py` 把用户问题放入 `AgentState.messages`，`ScriptedModel` 返回一个 `ToolCall`，`ToolRegistry` 执行后把观察结果送回模型，第二次模型调用才返回答案。

## 底层机制

模型输出是概率性的动作建议。宿主必须把它解析为受类型约束的数据，并在信任边界外重新校验。即使框架把 loop 隐藏起来，这个责任也不会消失。

## 检查点与练习

运行 `python 14-ai-agents/examples/offline_agent.py`，预测 `step` 的值。然后把任务改成固定的“先检索、再总结”，思考为什么普通函数可能比 Agent 更合适。

## 常见错误与生产注意

- 把长 system prompt 当作架构。
- 没有最大步数、超时或成本预算。
- 对确定性任务使用 Agent，增加成本与故障面。
- 让模型直接拥有数据库、Shell 或转账权限。
