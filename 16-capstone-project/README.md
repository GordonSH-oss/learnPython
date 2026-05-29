# 综合项目：AI 知识库服务

综合项目用于把前面模块串起来：Web API 接收问题，数据库保存文档元数据，向量检索找上下文，模型 API 生成答案，测试保证核心逻辑不依赖真实网络。

## 目标形态

```text
client
  -> FastAPI endpoint
  -> request validation
  -> document repository
  -> retriever
  -> LLM client
  -> structured response
  -> logs and metrics
```

## 本目录文件

- `app_skeleton.py`：用标准库模拟完整调用链，先学模块边界，再替换成真实 FastAPI、Milvus 和模型 API。

## 分阶段实现

1. 本地版本：用内存列表保存文档，用词频检索。
2. API 版本：用 FastAPI 暴露 `/ask`。
3. 数据库版本：用 SQLAlchemy 保存文档和问答记录。
4. 向量版本：用 embedding + Milvus 替换词频检索。
5. 生产版本：加鉴权、日志脱敏、超时、重试、评测集和 Docker。

## 验收标准

- 没有 API key 时，本地测试仍可运行。
- 检索、prompt 构造、模型调用分别可单元测试。
- 错误响应包含稳定错误码，不暴露密钥和底层堆栈。
