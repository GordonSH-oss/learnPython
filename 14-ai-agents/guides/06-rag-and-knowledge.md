# 06 RAG 与外部知识

## 学习目标

能够追踪 document 到 citation 的数据流，设计无答案路径，并解释 RAG、上下文和 Agent memory 的不同职责。

## 要看的代码

- `rag_pipeline.py`：分词、评分、Top K 与引用构造。
- `examples/research_agent.py`：检索工具进入 Agent loop。

## 概念模型

```text
ingest -> normalize -> chunk -> metadata -> index
query -> retrieve -> filter/rerank -> context -> answer -> citations
```

RAG 的质量上限来自语料、切分、metadata、召回和引用，不只来自 embedding 模型。

## 执行路径

玩具实现用词项重合替代 embedding，便于离线测试检索语义。`retrieve()` 丢弃零分结果，`build_answer()` 在无匹配时拒答，在有匹配时保留 source。

## 底层机制

向量检索优化语义相似度，不保证事实支持。生产系统常组合关键词、向量、metadata filter 和 reranker。检索文档必须标记为不可信数据，文档中的“忽略之前指令”不能进入控制层。

## 检查点与练习

运行 `python 14-ai-agents/rag_pipeline.py`。增加行号 metadata、Top K 和最小阈值；构造一个没有答案的问题，确认系统拒答而非拼凑。

## 常见错误与生产注意

- 只评最终回答，不单独测 retrieval recall。
- 引用的是检索结果，但句子并未被该结果支持。
- 文档更新后索引与权限 metadata 没同步。
- 将不同租户文档放入同一无过滤检索空间。
