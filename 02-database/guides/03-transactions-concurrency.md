# 03 事务与并发

## 学习目标

能够确定事务边界，解释并发异常，并为死锁或临时连接错误设计有限重试。

## ACID

- 原子性：事务内操作全部成功或全部失败。
- 一致性：事务前后数据满足约束和业务不变量。
- 隔离性：并发事务相互影响受隔离级别约束。
- 持久性：提交后的数据在故障后仍可恢复。

转账必须在同一事务中扣款、加款和记录流水。任何一步失败都要回滚。

```python
try:
    connection.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (100, 1))
    connection.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (100, 2))
    connection.commit()
except Exception:
    connection.rollback()
    raise
```

## 隔离问题

- 脏读：读到其他事务尚未提交的数据。
- 不可重复读：同一事务两次读取同一行，值不同。
- 幻读：同一条件查询两次，行集合不同。
- 丢失更新：两个事务基于旧值写回，后写覆盖先写。

数据库提供 Read Committed、Repeatable Read、Serializable 等隔离级别。隔离越强，通常并发代价越高。具体保证因数据库实现而异。

## 悲观锁与乐观锁

悲观锁先锁定行，例如 PostgreSQL 的 `SELECT ... FOR UPDATE`。适合冲突概率高、操作很短的场景。

乐观锁保存版本号：

```sql
UPDATE documents
SET content = :content, version = version + 1
WHERE id = :id AND version = :expected_version;
```

受影响行数为 0 代表内容已经被其他事务修改。

## 事务边界原则

- 事务对应一个完整业务操作，不对应一个 SQL 函数。
- 事务中不要执行耗时网络调用或等待用户输入。
- 异常后必须回滚，失败的连接或 Session 不能假装仍然可用。
- 只重试可判定为临时的错误，并设置次数、退避和幂等性。
- 不要把数据库事务与消息发送误认为天然原子；跨系统一致性通常需要 outbox、幂等键或补偿机制。

