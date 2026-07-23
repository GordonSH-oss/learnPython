# 异步数据库

异步数据库适用于已经使用 `asyncio` 的应用。不要把同步 SQLAlchemy Session 放进异步函数就称为异步；必须使用 async engine、async driver 和 `AsyncSession`。

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

engine = create_async_engine("sqlite+aiosqlite:///app.db")
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)

async def create_user(email: str) -> None:
    async with SessionFactory.begin() as session:
        session.add(User(email=email))

async def shutdown() -> None:
    await engine.dispose()
```

注意：`AsyncSession` 不能跨并发任务共享；懒加载会引发隐式 I/O，异步代码中更应使用 `selectinload()` 等显式加载策略。

