# 01 数据库与 SQL 基础

## 学习目标

能够从数据关系而不是 Python 类出发设计表，并预测约束、JOIN 和索引对行为的影响。

## 关系模型

表描述一种实体或关系，行是一条事实，列定义事实的属性。主键唯一标识行，外键引用另一张表的主键或唯一键。

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0)
);
```

数据库约束是最后一道防线：

- `PRIMARY KEY`：唯一且非空。
- `FOREIGN KEY`：引用必须有效。
- `UNIQUE`：业务上不允许重复。
- `NOT NULL`：值不可缺失。
- `CHECK`：值必须满足条件。
- `DEFAULT`：插入时未提供值所采用的默认值。

## CRUD 与查询顺序

CRUD 对应 `INSERT`、`SELECT`、`UPDATE`、`DELETE`。理解 `SELECT` 的逻辑处理顺序有助于调试：

```text
FROM/JOIN -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT
```

```sql
SELECT u.email, COUNT(o.id) AS order_count, SUM(o.amount_cents) AS total
FROM users AS u
LEFT JOIN orders AS o ON o.user_id = u.id
WHERE u.created_at >= :start_time
GROUP BY u.id, u.email
HAVING COUNT(o.id) >= 2
ORDER BY total DESC
LIMIT 10;
```

`WHERE` 过滤分组前的行，`HAVING` 过滤聚合后的组。`LEFT JOIN` 保留左表没有匹配项的行，`INNER JOIN` 只保留匹配行。

## NULL 不是普通值

`NULL` 表示未知或缺失。不能用 `= NULL`，应使用 `IS NULL`。SQL 使用三值逻辑：真、假、未知。

```sql
SELECT * FROM users WHERE deleted_at IS NULL;
```

## 规范化与反规范化

规范化减少重复数据和更新异常。常见目标是第三范式：每个非键字段描述主键代表的实体，并且不依赖其他非键字段。

反规范化为了读取性能主动保存重复信息，但必须明确谁是事实来源、如何同步。不要因为 JOIN 看起来复杂就过早反规范化。

## 索引的模型

索引是额外维护的查找结构，通常以 B-tree 为主。它加快筛选、连接、排序，却增加写入成本和存储空间。

适合索引：高频 `WHERE`、JOIN 外键、排序列，以及组合查询。组合索引 `(status, created_at)` 通常可支持只按 `status` 查询，但不能高效支持只按 `created_at` 查询，这称为最左前缀原则。

## 检查点

- 为什么用户邮箱唯一性必须有数据库 `UNIQUE`，不能只在插入前查询？
- `LEFT JOIN` 后在 `WHERE` 中过滤右表字段，为什么可能意外变成类似 `INNER JOIN`？
- 为低区分度布尔字段单独建索引为什么常常收益有限？

