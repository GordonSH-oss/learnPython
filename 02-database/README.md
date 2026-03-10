# 数据库学习

包含 SQLAlchemy ORM 和 Milvus 向量数据库的学习材料。

## SQLAlchemy

### 核心文件
- `sqlalchemy_tutorial.py` - 完整教程，从基础到高级
- `sqlalchemy_example.py` - 实用示例
- `database.py` - 数据库基础操作
- `SQLALCHEMY_QUICK_REFERENCE.md` - 快速参考手册

### 主要内容
1. 数据库连接和会话管理
2. ORM 模型定义
3. CRUD 操作（增删改查）
4. 关系映射（一对多、多对多）
5. 查询优化
6. 事务处理

## Milvus 向量数据库

### 核心文件
- `milvus_use.py` - 基础使用入门
- `use_milvus_with_schema.py` - 使用 Schema 定义集合
- `milvus_search.py` - 向量搜索示例
- `milvus_add_new_data.py` - 添加新数据

### 文档
- `MILVUS_SETUP.md` - 环境搭建指南
- `MILVUS_SCHEMA_EXPLANATION.md` - Schema 详解
- `MILVUS_PERSISTENCE.md` - 数据持久化
- `PERSISTENCE_COMPARISON.md` - 持久化方案对比
- `ADD_DATA_GUIDE.md` - 数据添加指南
- `DUPLICATE_INSERT_EXPLANATION.md` - 处理重复数据
- `VOLUMES_EXPLANATION.md` - Docker 卷挂载说明

### 主要内容
1. Milvus 连接和集合创建
2. 向量数据的插入和索引
3. 相似度搜索
4. 数据持久化策略
5. 处理重复插入问题

### 测试文件
- `test_persistence.py` - 持久化功能测试
- `test_duplicate_insert.py` - 重复插入测试

## 学习路径

### SQLAlchemy 路径
1. `database.py` - 了解基础概念
2. `sqlalchemy_tutorial.py` - 跟随教程学习
3. `sqlalchemy_example.py` - 查看实用示例
4. `SQLALCHEMY_QUICK_REFERENCE.md` - 作为日常参考

### Milvus 路径
1. `MILVUS_SETUP.md` - 搭建环境
2. `milvus_use.py` - 基础操作
3. `MILVUS_SCHEMA_EXPLANATION.md` - 理解 Schema
4. `use_milvus_with_schema.py` - 使用 Schema
5. `milvus_search.py` - 搜索功能
6. `MILVUS_PERSISTENCE.md` - 持久化方案
7. `milvus_add_new_data.py` - 数据管理

## 环境要求

```bash
# SQLAlchemy
pip install sqlalchemy

# Milvus
pip install pymilvus

# 可选：数据库驱动
pip install psycopg2-binary  # PostgreSQL
pip install mysqlclient      # MySQL
```

## Docker 支持

Milvus 需要 Docker 环境，相关配置在 `../05-devops/` 目录。
