# 09 生产数据库、连接池与异步

## 学习目标

理解 SQLite 到 PostgreSQL 的边界、连接池生命周期，以及异步数据库代码何时真正有收益。

## PostgreSQL 常用能力

生产 Web 服务常选择 PostgreSQL，因为它提供成熟的并发事务、丰富类型、JSONB、窗口函数、全文搜索、UPSERT、物化视图和扩展生态。

Python 常用驱动：同步 `psycopg`，异步 `asyncpg` 或 SQLAlchemy async 配合驱动。MySQL、MariaDB 和其他数据库也有对应驱动与 SQLAlchemy 方言。

## 连接池

建立数据库连接有成本，Engine 通常管理连接池。Session 关闭后通常是把连接归还池，而不是关闭底层网络连接。

关键参数包括池大小、额外连接数、等待超时、连接回收和健康检查。最大连接数不是越大越好：数据库能有效处理的并发有限，过大的池会把应用排队变成数据库过载。

进程 fork 后不要复用父进程创建的连接池。应用关闭时调用 `engine.dispose()`；async engine 使用 `await engine.dispose()`。

## 同步还是异步

异步适用于整个调用链已经基于 asyncio，并且任务的大部分时间在等待数据库或网络 I/O。它不会让单条 SQL 更快，也不能改善数据库内部的慢查询。

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

engine = create_async_engine("sqlite+aiosqlite:///app.db")
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)

async with SessionFactory.begin() as session:
    session.add(user)
```

AsyncSession 不能在多个并发任务中共享。每个请求或并发任务应有自己的 Session。

## 可靠性

- 设置连接、语句和事务超时。
- 只对临时故障进行有限重试。
- 写入操作使用幂等键避免重试造成重复数据。
- 应用启动先确认迁移版本，不要静默创建缺失表。
- 设计优雅停机：停止接收请求，等待事务结束，释放连接池。

