# 08 性能、安全与可观测性

## 学习目标

能够从查询计划而不是直觉优化数据库，并识别常见的数据安全边界。

## 性能诊断顺序

1. 找到慢请求和对应 SQL。
2. 记录耗时、返回行数、扫描行数和调用频率。
3. 使用 `EXPLAIN` 或 `EXPLAIN ANALYZE` 查看执行计划。
4. 检查索引、JOIN 顺序、排序、聚合和选择性。
5. 修复后用相同数据规模再次测量。

常见问题包括 N+1、`SELECT *`、缺失索引、索引过多、深分页 `OFFSET`、一次加载过多行、循环单条写入、长事务和连接池不足。

大数据分页优先考虑 keyset pagination：

```sql
SELECT id, created_at
FROM events
WHERE (created_at, id) < (:last_created_at, :last_id)
ORDER BY created_at DESC, id DESC
LIMIT 50;
```

## SQL 注入

错误：

```python
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

正确：

```python
cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
```

绑定参数只能替代值，不能安全替代表名或列名。动态标识符必须来自严格白名单。

## 凭据与权限

- 数据库 URL 从环境变量或密钥服务读取，不提交到 Git。
- 应用账户使用最小权限，不使用数据库超级用户。
- 生产连接启用 TLS，并验证服务端证书。
- 日志不要输出密码、令牌、个人信息或完整敏感 SQL 参数。
- 对备份、导出、测试快照执行相同的数据保护政策。

## 可观测性

记录连接池等待时间、查询耗时、事务回滚、死锁、重试、连接错误和慢查询。为查询打业务操作标签比只记录原始 SQL 更容易定位调用方。

