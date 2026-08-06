# 17 可观测性与生产工程

## 学习目标

能够用 trace 重建一次 Agent 运行，定位模型、工具、检索和队列造成的延迟、成本与失败。

## 概念模型

一个 task trace 包含多个 span：context build、model call、tool call、retrieval、checkpoint、approval。每个 span 记录耗时、状态、重试、模型/工具版本和脱敏后的计量信息。

## 执行路径

为每次运行生成 `trace_id`，把 `session_id`、step 与 tool call id 关联。指标至少包括成功率、停止原因、循环率、工具错误率、token、估算费用、端到端及分段延迟。日志用于具体事件，metrics 用于趋势，trace 用于因果链。

## 底层机制

流式输出改善首 token 延迟，不缩短工具执行。并发只适合无依赖且权限允许的读取动作。缓存要包含模型、prompt、工具和知识版本，不能缓存带个人状态或副作用的调用。

## 检查点与练习

为 `offline_agent.py` 设计一条 JSON trace，计算 model 与 tool 两类耗时。模拟工具超时，决定是重试、降级、等待还是结束。

## 常见错误与生产注意

- 只记录最终错误，无法知道失败发生在哪一步。
- 无限重试放大下游故障和费用。
- 没有并发上限、背压和取消传播。
- 部署新 prompt/模型时没有版本标签、canary 和回滚。
