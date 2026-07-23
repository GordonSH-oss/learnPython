# 06 数据库迁移与模式演进

## 学习目标

理解 schema 是有版本的生产资产，并能安全地设计可回滚、兼容滚动发布的变更。

安装依赖后初始化 Alembic：

```bash
alembic init migrations
alembic revision --autogenerate -m "create users"
alembic upgrade head
alembic downgrade -1
alembic current
alembic history
```

自动生成只负责比较 metadata 和数据库，必须人工审查。重命名列可能被误判成“删除旧列并新增列”，导致数据丢失。

## Expand and Contract

滚动发布中，新旧应用版本可能同时运行。安全重命名通常分阶段：

1. Expand：增加新列，保持旧列。
2. 双写或使用兼容逻辑。
3. 回填历史数据并验证。
4. 切换所有读取到新列。
5. Contract：确认旧版本下线后删除旧列。

大型表添加非空列、默认值或索引可能长时间锁表。PostgreSQL 可考虑并发创建索引；数据回填应分批并可恢复。

## 迁移原则

- 迁移脚本进入版本控制，并在 CI 中从空库升级到 head。
- schema 迁移和数据迁移尽量拆开。
- 向下迁移无法安全恢复数据时，应明确说明而不是伪造 rollback。
- 备份不是迁移策略，但破坏性变更前必须确认可恢复能力。

