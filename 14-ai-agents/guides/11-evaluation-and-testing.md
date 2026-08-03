# 11 Agent 评测与测试

## 学习目标

能够分层测试确定性逻辑、轨迹、检索和最终回答，建立可重复的回归数据集。

## 概念模型

```text
unit: schema, policy, state reducer, memory
trajectory: selected tools, arguments, order, stop reason
component: retrieval recall, citation support
end-to-end: task success, latency, cost, safety
```

## 执行路径

`ScriptedModel` 把概率模型替换为固定响应，使测试只验证 runner。轨迹断言关注工具是否正确、是否越权、是否停止，而非要求自然语言逐字相同。

回归数据集每项应包含输入、环境 fixture、允许/禁止动作、必要事实和评分器。模型裁判适合处理语义质量，但必须校准偏差，并与规则或人工样本组合。

## 底层机制

一次通过率不能描述 Agent。还应记录 pass@k、工具错误率、无效循环率、检索 recall、引用支持率、token、费用和延迟分位数。评测模型、被测模型和 prompt 都要版本化。

## 检查点与练习

运行 `pytest 14-ai-agents/tests`。新增一个用例，断言未知工具不会执行任何 handler。为 RAG 构造 5 个问题并分别标注期待 source。

## 常见错误与生产注意

- 只保存成功案例，没有困难与对抗样本。
- 用同一个宽松模型既生成又评分。
- 断言完整回答字符串，导致无意义脆弱测试。
- 上线前没有 shadow/canary 数据和回滚基线。
