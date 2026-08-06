# Python AI Agent 系统课程

这一章不是教你把问题发给模型，而是教你构建一个能在约束内观察状态、选择动作、调用工具、保存记忆、恢复执行并接受评测的 Agent 系统。课程先用纯 Python 拆开机制，再把同一概念映射到 OpenAI Agents SDK 和 LangGraph。

## 学完后应能做到

- 解释 Agent、固定 workflow 和 chatbot 的边界，并判断何时不该使用 Agent。
- 手写有停止条件的 Agent loop，正确处理工具错误、重复动作和执行预算。
- 设计 tool schema、权限、审批、超时、重试与幂等边界。
- 区分上下文、短期记忆、长期记忆和 RAG 知识库。
- 用 checkpoint、人工介入和审计轨迹构建可恢复任务。
- 测试 Agent 的轨迹和状态转换，而不只测试最终自然语言。
- 比较纯 Python、OpenAI Agents SDK 与 LangGraph 的抽象和取舍。

## 系统模型

```text
user input
    -> context builder (instructions + history + recalled memory)
    -> model decision
        -> final answer
        -> tool call -> validation -> permission -> execution -> observation --+
        -> handoff / pause / approval                                     |
                    ^-----------------------------------------------------+

state -> checkpoint       trace -> evaluation       policy -> guardrails
```

模型只负责提出候选动作。应用负责验证参数、授予权限、执行副作用、保存状态和决定何时停止。

## 课程路线

| 课 | 主题 | 核心问题 |
| --- | --- | --- |
| 01 | [Agent 基础](guides/01-agent-fundamentals.md) | Agent 与 workflow 有什么区别？ |
| 02 | [Agent loop](guides/02-agent-loop.md) | 模型、工具和状态怎样形成闭环？ |
| 03 | [Prompt 与上下文](guides/03-prompts-and-context.md) | 如何控制模型实际看到的信息？ |
| 04 | [Tools 与 MCP](guides/04-tools.md) | 如何安全地把能力交给模型？ |
| 05 | [Memory](guides/05-memory.md) | 什么值得记住，在哪里记，何时遗忘？ |
| 06 | [RAG 与知识](guides/06-rag-and-knowledge.md) | 外部知识如何进入回答并可追溯？ |
| 07 | [规划与推理](guides/07-planning-and-reasoning.md) | 如何分解长任务并限制失控循环？ |
| 08 | [状态与持久执行](guides/08-state-and-durable-execution.md) | 进程失败后怎样继续而不重复副作用？ |
| 09 | [Multi-agent](guides/09-multi-agent.md) | 何时拆角色，怎样控制交接？ |
| 10 | [框架对比](guides/10-framework-comparison.md) | 三种实现分别隐藏了什么？ |
| 11 | [评测与测试](guides/11-evaluation-and-testing.md) | 如何稳定判断 Agent 是否变好了？ |
| 12 | [应用层安全与 Guardrails](guides/12-security-and-guardrails.md) | 不可信内容如何跨越工具边界？ |
| 13 | [Sandbox 与策略](guides/13-sandbox-and-policies.md) | 执行边界、请求和策略如何分层？ |
| 14 | [本机进程 Sandbox](guides/14-local-process-sandbox.md) | 如何限制本机代码执行的影响？ |
| 15 | [Docker Sandbox](guides/15-docker-sandbox.md) | 如何用可选容器加强执行隔离？ |
| 16 | [身份、数据与供应链](guides/16-identity-data-supply-chain.md) | 如何隔离租户、凭据和依赖风险？ |
| 17 | [可观测性与生产](guides/17-observability-and-production.md) | 如何定位成本、延迟和失败？ |
| 18 | [研究助手项目](guides/18-capstone-research-agent.md) | 如何把所有能力组合成完整系统？ |

建议按顺序完成 01-08。09-16 建议结合项目练习，17 用于上线前检查，最后完成 18。

## 目录

```text
14-ai-agents/
├── agent_core/       # 框架无关、可测试的教学核心
├── guides/           # 18 课正文
├── examples/         # 离线、OpenAI Agents SDK、LangGraph 示例
├── tests/            # 核心行为和课程结构测试
├── rag_pipeline.py   # 标准库玩具 RAG
└── README.md
```

## 运行

必修内容只需要 Python 3.10+ 与 pytest：

```bash
python 14-ai-agents/examples/offline_agent.py
python 14-ai-agents/rag_pipeline.py
python 14-ai-agents/examples/research_agent.py
pytest 14-ai-agents/tests
```

Docker sandbox 是可选集成能力。安装并运行 Docker 后，可单独执行 `pytest 14-ai-agents/tests/test_sandbox_docker.py -q`；没有 Docker 时，集成测试会明确 skip，命令构造测试仍会运行。生成的代码必须先经过工具授权和 sandbox 执行器，本机进程模式不是强安全边界。

选修框架示例：

```bash
python -m pip install -r requirements/ai.txt
OPENAI_API_KEY=... python 14-ai-agents/examples/framework_openai_agents.py
RUN_LANGGRAPH_EXAMPLE=1 python 14-ai-agents/examples/framework_langgraph.py
```

密钥只能通过环境变量或密钥管理服务注入，不写入代码、prompt、checkpoint 或日志。

## 学习方法

先预测每个示例会产生哪些消息和状态，再运行代码。修改模型脚本、工具返回值或停止预算，观察轨迹如何变化。生产系统优先使用确定性 workflow；只有当动作选择确实需要模型判断时，才引入 Agent loop。
