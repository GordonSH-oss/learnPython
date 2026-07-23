# 05 SQLAlchemy 2.x ORM

## 学习目标

使用类型化声明模型和关系，并能解释 Session、Identity Map、flush、commit 和对象状态。

## ORM 不是数据库

ORM 把行映射为 Python 对象，把属性变化转换为 SQL。它不改变关系数据库的约束、事务和查询成本。

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    posts: Mapped[list["Post"]] = relationship(back_populates="author")
```

## Session 的运行机制

Session 同时承担：

- Unit of Work：收集对象变化并在 flush 时生成 SQL。
- Identity Map：同一 Session 内，同一主键通常对应同一个 Python 对象。
- 事务边界：commit、rollback。

`add()` 只是把对象加入工作单元；`flush()` 把 SQL 发给数据库但不一定提交；`commit()` 提交事务；`refresh()` 从数据库重新加载；`expunge()` 将对象移出 Session。

推荐生命周期：每个 Web 请求或后台任务一个短生命周期 Session，服务层决定事务边界。

## 关系加载与 N+1

延迟加载在访问关系时额外查询，循环访问可能产生 N+1：先查 N 个用户，再为每个用户查帖子。使用 `selectinload()` 或 `joinedload()` 显式选择策略，并通过 SQL 日志验证。

```python
statement = select(User).options(selectinload(User.posts))
users = session.scalars(statement).all()
```

## 常见错误

- 把 Session 做成跨线程、跨请求的全局单例。
- 在 repository 内随意 commit，使上层无法组合原子操作。
- 序列化对象时意外触发大量延迟查询。
- 仅定义 ORM relationship，却忘记数据库 ForeignKey。
- 使用 `create_all()` 管理生产 schema，而没有 Alembic。

