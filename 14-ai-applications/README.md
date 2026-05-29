# AI 应用工程

AI 应用工程不是只会调用模型 API。核心是把用户问题、业务数据、检索、模型调用、结构化输出、评测和成本控制组成稳定链路。

## 学习目标

- 理解 prompt、message、model、token、temperature 的作用。
- 会区分 completion、embedding、RAG、tool calling 和 structured output。
- 会设计不依赖真实网络的本地检索测试。
- 知道如何记录成本、延迟和失败原因。

## 本目录文件

- `rag_pipeline.py`：不用外部依赖实现一个玩具 RAG，帮助理解“切分、检索、拼上下文、生成答案”的数据流。

## RAG 数据流

```text
documents
  -> chunk
  -> embed/index
  -> retrieve relevant chunks
  -> build prompt with citations
  -> call model
  -> validate answer
```

本目录的示例用词频检索代替 embedding。等理解链路后，再把检索器替换成 OpenAI embedding + Milvus。

## 练习

1. 给每个 chunk 加来源文件名和行号。
2. 把检索 Top K 从 2 改成 3，观察答案上下文变化。
3. 增加一个“无答案”判断：检索分数为 0 时不要生成答案。
