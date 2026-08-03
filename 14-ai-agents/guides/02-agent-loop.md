# 02 手写 Agent Loop

## 学习目标

能够追踪 observe-think-act 循环，解释工具结果如何变成下一轮 observation，并实现停止、失败和循环保护。

## 要看的代码

- `agent_core/runner.py`：`ModelClient` 与 `AgentRunner`。
- `agent_core/fakes.py`：确定性的 `ScriptedModel`。
- `tests/test_agent_core.py`：成功、未知工具、重复与最大步数。

## 概念模型

```text
messages -> model -> final answer -> stop
                  -> tool calls -> execute -> tool messages -> model
```

状态要记录输入、动作、观察、步数与状态。只保存最终答案会失去调试和恢复所需的证据。

## 执行路径

`AgentRunner.run()` 加入用户消息，调用模型；有工具调用时先生成稳定签名检测重复，再逐个执行并保存 checkpoint；没有工具调用时写入最终 assistant 消息并结束。

## 底层机制

tool result 使用 `role="tool"` 进入上下文。它是外部环境的观察，不是可信指令。同步教学 runner 会拒绝 awaitable 工具，生产系统应提供 async runner，并为整个任务与单个工具分别设置 deadline。

## 检查点与练习

让 `ScriptedModel` 连续返回相同调用，确认停止原因是 `repeated_tool_calls`。再修改为不同 call id 但相同参数，解释为何仍应视为循环。

## 常见错误与生产注意

- 只按 call id 检测循环，模型每轮换 id 就可绕过。
- 工具异常直接中断进程，而不是作为观察反馈。
- checkpoint 只在最终成功时保存。
- 重试整个 loop，导致已完成的副作用重复发生。
