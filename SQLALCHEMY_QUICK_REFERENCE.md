# SQLAlchemy 快速参考指南

基于 `database.py` 的实战案例

## 📚 目录

1. [基础概念](#基础概念)
2. [定义模型](#定义模型)
3. [数据库连接](#数据库连接)
4. [CRUD 操作](#crud-操作)
5. [关联关系](#关联关系)
6. [查询技巧](#查询技巧)
7. [最佳实践](#最佳实践)

---

## 基础概念

### 核心组件

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()  # 所有模型的基类
```

- **Engine**: 数据库连接引擎
- **Session**: 数据库会话（类似数据库连接）
- **Model**: 数据模型（对应数据库表）
- **Query**: 查询对象

---

## 定义模型

### 基本模型定义

```python
class TranslationTask(Base):
    __tablename__ = 'translation_tasks'  # 表名
    
    # 主键
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 普通字段
    task_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default='pending')
    progress = Column(Integer, nullable=False, default=0)
    
    # 时间戳（自动更新）
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, 
                       default=datetime.utcnow, 
                       onupdate=datetime.utcnow)
    
    # 关联关系
    chunks = relationship('Chunk', back_populates='task')
```

### 常用字段类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `Integer` | 整数 | `Column(Integer)` |
| `String(n)` | 字符串（最大长度n） | `Column(String(255))` |
| `Text` | 长文本 | `Column(Text)` |
| `DateTime` | 日期时间 | `Column(DateTime)` |
| `Boolean` | 布尔值 | `Column(Boolean)` |
| `Float` | 浮点数 | `Column(Float)` |
| `JSON` | JSON数据 | `Column(JSON)` |
| `UUID` | UUID（PostgreSQL） | `Column(UUID(as_uuid=True))` |

### 字段参数

```python
Column(
    String(255),                    # 类型
    primary_key=True,               # 主键
    nullable=False,                 # 不允许为空
    default='pending',              # 默认值
    index=True,                     # 创建索引
    unique=True,                    # 唯一约束
    comment='字段说明'              # 注释
)
```

---

## 数据库连接

### 创建连接

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# PostgreSQL
database_url = "postgresql://user:password@localhost:5432/dbname"

# SQLite（测试用）
database_url = "sqlite:///database.db"

# 创建引擎
engine = create_engine(database_url, echo=True)  # echo=True 打印SQL

# 创建会话工厂
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# 创建表
Base.metadata.create_all(engine)
```

### 使用数据库管理器（推荐）

```python
from database import DatabaseManager, init_database

# 初始化
db_manager = init_database("postgresql://user:password@localhost:5432/dbname")

# 获取会话
session = db_manager.get_session()
```

---

## CRUD 操作

### Create（创建）

```python
# 方法1：创建单个对象
task = TranslationTask(
    task_name="新任务",
    source_language="zh",
    target_language="en"
)
session.add(task)
session.commit()

# 方法2：批量创建
tasks = [
    TranslationTask(task_name="任务1"),
    TranslationTask(task_name="任务2")
]
session.add_all(tasks)
session.commit()

# 方法3：通过关系创建
chunk = Chunk(chunk_type="source", content="内容")
task.chunks.append(chunk)  # 自动设置外键
session.commit()
```

### Read（读取）

```python
# 查询所有
all_tasks = session.query(TranslationTask).all()

# 查询单条（主键）
task = session.query(TranslationTask).get(task_id)

# 查询第一条
task = session.query(TranslationTask).first()

# 条件查询
tasks = session.query(TranslationTask).filter(
    TranslationTask.status == 'pending'
).all()

# 多个条件（AND）
tasks = session.query(TranslationTask).filter(
    TranslationTask.status == 'pending',
    TranslationTask.source_language == 'zh'
).all()

# 使用 filter_by（更简洁）
tasks = session.query(TranslationTask).filter_by(
    status='pending',
    source_language='zh'
).all()

# 限制数量
tasks = session.query(TranslationTask).limit(10).all()

# 排序
tasks = session.query(TranslationTask).order_by(
    TranslationTask.created_at.desc()
).all()

# 计数
count = session.query(TranslationTask).count()
```

### Update（更新）

```python
# 方法1：修改对象属性
task = session.query(TranslationTask).get(task_id)
task.status = 'completed'
task.progress = 100
session.commit()

# 方法2：批量更新
session.query(TranslationTask).filter_by(
    status='pending'
).update({
    'status': 'processing',
    'progress': 50
})
session.commit()
```

### Delete（删除）

```python
# 方法1：删除对象
task = session.query(TranslationTask).get(task_id)
session.delete(task)
session.commit()

# 方法2：批量删除
session.query(TranslationTask).filter_by(
    status='completed'
).delete()
session.commit()
```

---

## 关联关系

### 一对多关系

```python
# TranslationTask 模型
class TranslationTask(Base):
    chunks = relationship('Chunk', back_populates='task', 
                         cascade='all, delete-orphan')

# Chunk 模型
class Chunk(Base):
    task_id = Column(UUID(as_uuid=True), 
                     ForeignKey('translation_tasks.id'), 
                     nullable=False)
    task = relationship('TranslationTask', back_populates='chunks')
```

### 使用关联关系

```python
# 通过关系访问
task = session.query(TranslationTask).get(task_id)
for chunk in task.chunks:  # 访问关联的chunks
    print(chunk.content)

# 通过关系创建
chunk = Chunk(chunk_type="source", content="内容")
task.chunks.append(chunk)  # 自动设置 task_id
session.commit()

# JOIN 查询
chunks = session.query(Chunk).join(TranslationTask).filter(
    TranslationTask.status == 'pending'
).all()
```

### 关系类型

| 关系类型 | 说明 | 示例 |
|---------|------|------|
| `relationship()` | 一对多 | `chunks = relationship('Chunk')` |
| `ForeignKey` | 外键 | `task_id = Column(..., ForeignKey('tasks.id'))` |
| `back_populates` | 反向关系 | `back_populates='task'` |
| `cascade` | 级联操作 | `cascade='all, delete-orphan'` |

---

## 查询技巧

### 高级查询

```python
from sqlalchemy import or_, and_, func

# OR 条件
tasks = session.query(TranslationTask).filter(
    or_(
        TranslationTask.status == 'pending',
        TranslationTask.status == 'processing'
    )
).all()

# IN 查询
tasks = session.query(TranslationTask).filter(
    TranslationTask.status.in_(['pending', 'processing'])
).all()

# LIKE 查询
tasks = session.query(TranslationTask).filter(
    TranslationTask.task_name.like('%测试%')
).all()

# 聚合函数
avg_progress = session.query(
    func.avg(TranslationTask.progress)
).scalar()

max_progress = session.query(
    func.max(TranslationTask.progress)
).scalar()

# 分组查询
status_count = session.query(
    TranslationTask.status,
    func.count(TranslationTask.id)
).group_by(TranslationTask.status).all()

# 子查询
subquery = session.query(Chunk.task_id).filter(
    Chunk.chunk_type == 'source'
).subquery()

tasks = session.query(TranslationTask).filter(
    TranslationTask.id.in_(subquery)
).all()
```

### 链式查询

```python
tasks = session.query(TranslationTask)\
    .filter(TranslationTask.status == 'pending')\
    .filter(TranslationTask.source_language == 'zh')\
    .order_by(TranslationTask.created_at.desc())\
    .limit(10)\
    .all()
```

---

## 最佳实践

### 1. 会话管理

```python
# ✅ 推荐：使用上下文管理器
with SessionLocal() as session:
    task = TranslationTask(task_name="任务")
    session.add(task)
    session.commit()

# ✅ 推荐：使用 try-finally
session = SessionLocal()
try:
    # 使用session
    session.commit()
except Exception:
    session.rollback()
finally:
    session.close()

# ✅ 推荐：使用数据库管理器
from database import get_db_session

session = get_db_session()
try:
    # 使用session
    session.commit()
finally:
    session.close()
```

### 2. 事务处理

```python
session = SessionLocal()
try:
    # 多个操作
    task = TranslationTask(...)
    session.add(task)
    
    chunk = Chunk(...)
    session.add(chunk)
    
    session.commit()  # 所有操作一起提交
except Exception:
    session.rollback()  # 发生错误时回滚
    raise
finally:
    session.close()
```

### 3. 使用数据库管理器模式

```python
# database.py 中的模式
class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self) -> Session:
        return self.SessionLocal()

# 全局初始化
_db_manager = None

def init_database(database_url: str):
    global _db_manager
    _db_manager = DatabaseManager(database_url)
    return _db_manager

def get_db_manager() -> DatabaseManager:
    if _db_manager is None:
        raise RuntimeError("Database not initialized")
    return _db_manager
```

### 4. 模型设计建议

```python
# ✅ 推荐：使用 UUID 作为主键
id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

# ✅ 推荐：添加时间戳字段
created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
updated_at = Column(DateTime, nullable=False, 
                   default=datetime.utcnow, 
                   onupdate=datetime.utcnow)

# ✅ 推荐：添加 __repr__ 方法
def __repr__(self):
    return f"<TranslationTask(id={self.id}, task_name='{self.task_name}')>"

# ✅ 推荐：使用 comment 添加字段说明
task_name = Column(String(255), nullable=False, comment='任务名称')
```

### 5. 性能优化

```python
# ✅ 使用索引
task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id'), index=True)

# ✅ 批量操作
session.add_all([task1, task2, task3])  # 比多次 add() 更高效

# ✅ 使用 join 而不是多次查询
chunks = session.query(Chunk).join(TranslationTask).filter(
    TranslationTask.status == 'pending'
).all()

# ✅ 只查询需要的字段
tasks = session.query(TranslationTask.task_name, TranslationTask.status).all()
```

---

## 常见问题

### Q: 如何查看生成的 SQL？

```python
# 方法1：设置 echo=True
engine = create_engine(database_url, echo=True)

# 方法2：打印查询对象
query = session.query(TranslationTask).filter_by(status='pending')
print(str(query))
```

### Q: 如何处理重复插入？

```python
# 使用 get_or_create 模式
task = session.query(TranslationTask).filter_by(
    task_name="任务名"
).first()

if not task:
    task = TranslationTask(task_name="任务名")
    session.add(task)
    session.commit()
```

### Q: 如何更新关联对象？

```python
# 通过关系更新
task = session.query(TranslationTask).get(task_id)
task.chunks[0].content = "新内容"
session.commit()
```

---

## 完整示例

```python
from database import init_database, get_db_session
from database import TranslationTask, Chunk

# 初始化数据库
init_database("postgresql://user:password@localhost:5432/dbname")

# 创建任务
session = get_db_session()
try:
    # 创建任务
    task = TranslationTask(
        task_name="翻译任务",
        source_language="zh",
        target_language="en",
        status="pending"
    )
    session.add(task)
    session.flush()  # 获取 task.id
    
    # 创建关联的chunk
    chunk = Chunk(
        task_id=task.id,
        chunk_type="source",
        chunk_index=0,
        content="原文内容"
    )
    session.add(chunk)
    
    session.commit()
    
    # 查询任务及其chunks
    task = session.query(TranslationTask).get(task.id)
    print(f"任务: {task.task_name}")
    print(f"Chunks数量: {len(task.chunks)}")
    
finally:
    session.close()
```

---

## 参考资源

- [SQLAlchemy 官方文档](https://docs.sqlalchemy.org/)
- [SQLAlchemy ORM 教程](https://docs.sqlalchemy.org/en/14/orm/tutorial.html)
- `database.py` - 实际项目示例
- `sqlalchemy_tutorial.py` - 完整教程代码

