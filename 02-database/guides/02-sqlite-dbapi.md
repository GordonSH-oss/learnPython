# 02 sqlite3 与 Python DB-API

## 学习目标

不依赖第三方包，完成连接、参数化查询、CRUD、事务和资源清理。

## DB-API 的共同接口

Python 数据库驱动通常遵循 PEP 249：

```text
connect() -> Connection -> Cursor -> execute() -> fetch*()
                    └── commit() / rollback() / close()
```

`sqlite3` 是标准库驱动，SQLite 是嵌入式数据库，数据库就是一个文件，适合学习、测试、桌面应用和中小型单机服务。

```python
import sqlite3

with sqlite3.connect("app.db") as connection:
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    rows = connection.execute(
        "SELECT id, email FROM users WHERE email LIKE ?",
        ("%@example.com",),
    ).fetchall()
```

不同驱动的占位符可能是 `?`、`%s` 或命名参数。不要自己加引号，更不要用 f-string 拼接用户输入。

## 写入与返回结果

```python
cursor = connection.execute(
    "INSERT INTO users(email) VALUES (?)",
    ("learner@example.com",),
)
user_id = cursor.lastrowid
```

批量写入用 `executemany()`。数据量很大时分批提交，不要一次构造无限大的列表。

## SQLite 的重要特性

- 单文件、零运维、跨平台。
- 动态类型，但推荐使用严格、清晰的列类型。
- 默认必须显式开启外键检查：`PRAGMA foreign_keys = ON`。
- 并发读取良好，但同一时间写入能力有限。
- `:memory:` 数据库通常只在当前连接生命周期内存在。
- 可使用 WAL 模式改善读写并发：`PRAGMA journal_mode = WAL`。

## 日期、Decimal 和 JSON

数据库不会自动理解所有 Python 类型。生产代码要明确序列化边界：

- 时间建议保存为带时区的 UTC 时间，并在显示时转换。
- 金额不要使用二进制浮点；使用最小货币单位整数或 `Decimal` 对应的精确数值类型。
- SQLite JSON 通常保存为文本；PostgreSQL 可使用 `JSONB`，但不应把所有结构都塞进 JSON 绕过建模。

## 练习

运行 `examples/sqlite/01_crud.py`，然后添加一个唯一用户名字段。尝试插入重复用户名，观察异常由哪一层抛出。

