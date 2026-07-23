# Python 数据库学习路径

本目录是一套面向已有 Python 基础学习者的数据库课程。重点不是背 API，而是理解数据如何从 Python 对象经过驱动、连接、事务和 SQL，最终可靠地写入数据库。

## 先建立整体模型

```text
Python 业务代码
    │
    ├── DB-API 驱动：sqlite3 / psycopg / asyncpg
    │       └── 直接执行 SQL，控制连接和事务
    │
    └── SQLAlchemy
            ├── Core：SQL 表达式与连接抽象
            └── ORM：Python 对象、关系和 Unit of Work
                    │
                    └── 数据库：SQLite / PostgreSQL / MySQL
```

数据库负责持久化、并发控制、约束和查询。Python 驱动负责协议通信。SQLAlchemy 是驱动之上的抽象层，不会替你消除 SQL、事务或索引知识。

## 课程路线

| 阶段 | 教程 | 学完后能够 |
| --- | --- | --- |
| 1 | [数据库与 SQL 基础](guides/01-database-and-sql.md) | 解释表、键、约束、JOIN、规范化和索引 |
| 2 | [sqlite3 与 DB-API](guides/02-sqlite-dbapi.md) | 使用标准库完成安全 CRUD 和事务 |
| 3 | [事务与并发](guides/03-transactions-concurrency.md) | 解释 ACID、隔离级别、锁和重试 |
| 4 | [SQLAlchemy Core](guides/04-sqlalchemy-core.md) | 用 SQLAlchemy 2.x 表达式执行 SQL |
| 5 | [SQLAlchemy ORM](guides/05-sqlalchemy-orm.md) | 建模关系并理解 Session 生命周期 |
| 6 | [迁移与模式演进](guides/06-migrations.md) | 使用 Alembic 管理 schema 版本 |
| 7 | [测试与架构](guides/07-testing-and-architecture.md) | 设计 repository 边界和数据库测试 |
| 8 | [性能与安全](guides/08-performance-security.md) | 分析慢查询、索引、注入和凭据风险 |
| 9 | [生产数据库与异步](guides/09-production-and-async.md) | 理解 PostgreSQL、连接池和 async |
| 10 | [数据库类型地图](guides/10-database-landscape.md) | 判断关系型、文档、缓存和向量数据库的适用边界 |

按顺序学习前 5 课。后面的课可以按项目需求选择，但生产项目至少要掌握迁移、测试、安全和连接池。

## 可运行示例

```bash
python 02-database/examples/sqlite/01_crud.py
python 02-database/examples/sqlite/02_transactions.py

python -m pip install -r 02-database/requirements.txt
python 02-database/examples/sqlalchemy/01_core.py
python 02-database/examples/sqlalchemy/02_orm.py

pytest 02-database/tests
```

示例默认把临时数据库放在系统临时目录，不污染源码目录。

## 目录说明

```text
02-database/
├── guides/                       # 主课程
├── examples/
│   ├── sqlite/                   # 仅使用 Python 标准库
│   ├── sqlalchemy/               # SQLAlchemy 2.x 示例
│   └── async_database/           # 异步数据库说明与示例
├── tests/                        # 可重复运行的测试
├── vector-databases/milvus/      # 独立的 Milvus 专题
├── legacy/translation-example/  # 原有翻译项目数据库示例
├── data/                         # 本地运行生成的数据，Git 忽略
└── requirements.txt
```

`legacy/` 中的代码保留用于阅读已有项目，但部分写法基于 SQLAlchemy 1.x。新代码以主课程中的 SQLAlchemy 2.x 风格为准。

## 调试顺序

1. 确认数据库 URL、驱动和服务是否正确。
2. 打印实际 SQL 和绑定参数，不要只看 ORM 对象。
3. 明确当前连接或 Session 是否处于事务中。
4. 检查是否执行了 `commit()`，异常后是否执行了 `rollback()`。
5. 检查约束、字段类型、时区和 `NULL` 语义。
6. 对慢查询运行 `EXPLAIN`，确认是否使用了预期索引。
7. 排查连接泄漏、连接池耗尽、锁等待和死锁。

## 核心原则

- 参数始终通过占位符绑定，不拼接用户输入生成 SQL。
- 一个业务操作需要原子性时，必须放在同一事务中。
- 用数据库约束守住最终数据一致性，不只依赖 Python 校验。
- ORM 解决对象映射问题，不替代 SQL 和关系模型知识。
- schema 变化必须使用迁移工具并进入版本控制。
- 生产环境不要在应用启动时调用 `create_all()` 代替迁移。
- 异步数据库只在调用链本身是异步且并发 I/O 明显时使用。
