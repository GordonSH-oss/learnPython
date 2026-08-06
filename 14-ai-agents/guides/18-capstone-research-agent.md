# 18 综合项目：可恢复的研究助手

## 学习目标

把检索、tool、memory、checkpoint、引用、审批与离线 sandbox 组合成一个边界清晰的研究助手。

## 要看的代码

- `examples/research_agent.py`
- `agent_core/`
- `rag_pipeline.py`

## 架构

```text
question -> recall preference -> research Agent
             |                    -> search_documents tool
             |                    -> evidence with sources
             +-> answer style     -> cited final answer
state -> checkpoint     write action -> approval     trace -> evaluation
```

示例使用 `ScriptedModel`，因此无需网络。真实模型适配器只需实现 `ModelClient.complete()`，不应改动工具、memory 和测试边界。

## 执行路径

1. 资料以 `Chunk(source, text)` 建立本地知识库。
2. `search_documents` 返回结构化匹配和 source。
3. 任何生成的 Python 代码都先转换成 `PythonCode`，只能通过 `LocalProcessSandbox` 执行；本机 sandbox 不是强安全边界。
4. `tenant_id`、`session_id` 同时作用于 memory scope 和 workspace 路径，两个租户或会话不会共享执行目录。
5. Agent loop 把检索观察交回模型，生成带引用回答。
6. 用户偏好单独进入 `MemoryStore`，不混入知识库。
7. 每轮状态进入 checkpointer，恢复依赖稳定 call id。

## 验收标准

- 无资料时明确拒答。
- 最终回答引用实际检索 source。
- 未审批的写操作不能执行。
- 两个 tenant/session 的 memory 与 workspace 隔离。
- 生成代码无法读取宿主环境变量、通过路径遍历逃逸或执行未 allowlist 的命令。
- timeout 和 output limit 返回结构化停止原因；完整代码、环境变量和凭据不进入 trace。

## 练习

加入 reviewer 节点，检查每个结论是否有证据；为 `execute_code` 增加人工审批测试；设计两个 tenant 的离线任务，验证 memory、workspace 和执行结果不交叉；再实现 JSON checkpoint 并手动中断恢复，但保持测试仍使用 fake model。

## 常见错误与生产注意

- 研究助手被授予任意浏览器、文件和消息发送权限。
- 只保存回答，不保存证据版本和检索参数。
- 将“用户喜欢简短回答”与“Python 版本事实”写入同一 store。
- 没有数据授权、内容保留、费用预算和人工升级路径。
