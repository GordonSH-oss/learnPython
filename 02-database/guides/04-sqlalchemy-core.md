# 04 SQLAlchemy 2.x Core

## 学习目标

理解 Engine、Connection、MetaData 和 SQL 表达式，并使用 SQLAlchemy 2.x 的执行模型。

## 核心对象

```text
Engine：数据库 URL、方言和连接池
Connection：一次连接及其事务状态
MetaData：表结构集合
Table/Column：schema 的 Python 表达
select/insert/update/delete：生成带参数的 SQL 表达式
```

```python
from sqlalchemy import create_engine, select

engine = create_engine("sqlite+pysqlite:///app.db", echo=True)

with engine.connect() as connection:
    rows = connection.execute(select(users).where(users.c.active.is_(True))).all()
```

写事务推荐 `engine.begin()`：正常退出提交，异常退出回滚。

```python
with engine.begin() as connection:
    connection.execute(users.insert(), [{"email": "a@example.com"}])
```

## 方言与驱动

数据库 URL 同时说明数据库方言和 Python 驱动：

```text
sqlite+pysqlite:///app.db
postgresql+psycopg://user:password@host/dbname
mysql+pymysql://user:password@host/dbname
```

SQLAlchemy 统一常见操作，但数据库类型、锁、JSON、UPSERT 和全文搜索仍有方言差异。

## 为什么先学 Core

ORM 最终仍会生成 Core 表达式。会读 `select()`、JOIN 和事务，才能理解 ORM 的性能与错误。运行 `examples/sqlalchemy/01_core.py` 并打开 `echo=True`，对照 Python 表达式和实际 SQL。

