# 04 Tools、权限与 MCP

## 学习目标

能够设计清晰的工具契约，理解 schema、校验、执行、错误、审批、超时、重试、并发和幂等性的责任边界。

## 要看的代码

- `agent_core/tools.py`：`ToolDefinition`、`ToolRegistry`、计算器与受控读取。
- `tests/test_agent_core.py`：参数、审批、sandbox 和幂等测试。

## 概念模型

```text
model proposal -> schema validation -> authorization -> approval
               -> execution deadline -> normalized result -> audit
```

工具名应表达业务能力，如 `search_orders`，而不是暴露任意 SQL 或 Shell。参数使用最小权限和封闭 schema。

## 执行路径

`ToolRegistry.execute()` 先按 call id 查缓存，再检查工具存在、必填/额外参数与类型，然后执行审批策略，捕获异常并返回 `ToolResult`。受控文件读取用解析后的真实路径确认没有逃逸允许目录。

## MCP 在哪里

MCP 是工具与资源互操作协议：client 发现 server 暴露的 capabilities，再发起受 schema 约束的调用。MCP 不负责 Agent 的目标、loop、memory 或权限决策。远程 MCP server 仍是不可信依赖，需要认证、allowlist、超时和结果过滤。

## 检查点与练习

为 `send_email` 标记 `requires_approval=True`，设计 preview 与 commit 两阶段。思考读取工具能否并行，以及写工具为什么通常需要顺序和幂等键。

## 常见错误与生产注意

- 工具描述含糊，导致模型选错能力。
- 对写操作盲目重试。
- 认为参数来自模型就已验证。
- 给 MCP server 继承宿主进程的全部环境变量和文件权限。
