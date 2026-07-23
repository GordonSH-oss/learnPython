# Milvus 向量数据库专题

本专题保留原有 Milvus 学习资料。建议先完成主课程中的关系数据库基础，再学习向量数据库。

## 心智模型

Milvus 保存向量并执行近似最近邻搜索。典型流程是：

```text
文本/图片 -> embedding 模型 -> 向量 -> Milvus 索引
查询内容 -> embedding 模型 -> 查询向量 -> 相似度搜索 -> 候选 ID
候选 ID -> PostgreSQL 等权威数据库 -> 完整业务数据
```

向量距离表示数学空间中的接近程度，不等同于事实正确性。关系数据库通常仍然负责事务、权限、状态和权威元数据。

## 内容

- `examples/milvus_use.py`：基础创建、插入和搜索。
- `examples/use_milvus_with_schema.py`：显式 schema 和索引。
- `examples/milvus_add_new_data.py`：增量插入。
- `examples/milvus_search.py`：复用已有集合查询。
- `docs/MILVUS_SETUP.md`：服务启动。
- `docs/MILVUS_SCHEMA_EXPLANATION.md`：schema 选择。
- `docs/MILVUS_PERSISTENCE.md`：持久化机制。
- `docs/DUPLICATE_INSERT_EXPLANATION.md`：重复写入与 ID。

这些示例需要单独安装 `pymilvus` 并运行 Milvus 服务。原文包含特定版本和本机路径经验，执行前应按当前 pymilvus 与 Milvus 官方文档核对 API 版本。

## 生产关注点

- embedding 模型与向量维度必须稳定并纳入版本管理。
- 明确使用 L2、IP 或 cosine 等距离度量及其分数含义。
- ID 要能关联权威数据源，并支持幂等 upsert 和删除同步。
- 索引类型和搜索参数需要以召回率、延迟和内存实测决定。
- 设计重建索引、模型升级、备份恢复和数据删除流程。

