# 09 Multi-agent 与 Handoff

## 学习目标

能够比较 router、manager-worker、handoff 和并行专家模式，定义清晰的共享状态与交接预算。

## 概念模型

| 模式 | 控制者 | 适用情况 |
| --- | --- | --- |
| Router | 分类器 | 请求类型明确、分支独立 |
| Manager-worker | manager | 需要分解、汇总多个子任务 |
| Handoff | 当前 agent | 专业角色接管后续对话 |
| Parallel experts | orchestrator | 子任务独立，可并行取证 |

多个 prompt 不等于多个 Agent。只有角色拥有独立状态、工具或控制权时，拆分才有意义。

## 执行路径

交接数据应包含任务、已知事实、证据引用、剩余预算与允许动作，不要无选择地转发完整上下文。manager 负责验收 worker 输出，而不是简单拼接。

## 底层机制

多 Agent 增加序列化、上下文复制、权限传播和故障组合。共享可变状态会引入竞争；并行 worker 应返回独立结果，由 reducer 确定性合并。

## 检查点与练习

为研究助手设计 researcher 与 reviewer 两个角色，规定 reviewer 只能读证据、不能新增来源。设置最多两次交接，并定义超限后的结果。

## 常见错误与生产注意

- 用角色扮演掩盖一个函数即可完成的流程。
- 子 Agent 自动继承 manager 的全部工具权限。
- handoff 循环没有次数上限。
- 多个 worker 同时写同一 memory key。
