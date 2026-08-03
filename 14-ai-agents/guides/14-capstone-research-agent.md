# 14 综合项目：可恢复的研究助手

## 学习目标

把检索、tool、memory、checkpoint、引用、审批与离线评测组合成一个边界清晰的研究助手。

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
3. Agent loop 把检索观察交回模型，生成带引用回答。
4. 用户偏好单独进入 `MemoryStore`，不混入知识库。
5. 每轮状态进入 checkpointer，恢复依赖稳定 call id。

## 验收标准

- 无资料时明确拒答。
- 最终回答引用实际检索 source。
- 未审批的写操作不能执行。
- 两个 session 的 memory 隔离。
- 相同副作用 call id 恢复后不重复执行。
- 离线测试能断言轨迹、停止原因和引用。

## 练习

加入 reviewer 节点，检查每个结论是否有证据；加入 JSON checkpoint 并手动中断恢复；再实现 OpenAI `ModelClient` 适配器，但保持测试仍使用 fake model。

## 常见错误与生产注意

- 研究助手被授予任意浏览器、文件和消息发送权限。
- 只保存回答，不保存证据版本和检索参数。
- 将“用户喜欢简短回答”与“Python 版本事实”写入同一 store。
- 没有数据授权、内容保留、费用预算和人工升级路径。
