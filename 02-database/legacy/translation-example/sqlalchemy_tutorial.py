"""
SQLAlchemy 完整教程 - 基于 database.py 的实战案例

本教程将逐步讲解 SQLAlchemy 的核心概念和使用方法
"""

# ============================================================
# 第一部分：基础概念和导入
# ============================================================

print("=" * 80)
print("第一部分：SQLAlchemy 基础概念")
print("=" * 80)

"""
SQLAlchemy 是 Python 最流行的 ORM（对象关系映射）框架

核心组件：
1. Engine：数据库连接引擎
2. Session：数据库会话（类似数据库连接）
3. Model：数据模型（对应数据库表）
4. Query：查询对象
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Base 是所有模型的基类
Base = declarative_base()

print("✓ 导入完成\n")


# ============================================================
# 第二部分：定义模型（Model）
# ============================================================

print("=" * 80)
print("第二部分：定义模型（Model）")
print("=" * 80)

"""
模型（Model）对应数据库中的表（Table）
使用类继承 Base 来定义模型
"""

class TranslationTask(Base):
    """翻译任务表 - 对应 translation_tasks 表"""
    __tablename__ = 'translation_tasks'  # 指定表名
    
    # 主键：任务ID（UUID）
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 普通字段
    task_name = Column(String(255), nullable=False, comment='任务名称')
    source_language = Column(String(10), nullable=False, default='zh', comment='源语言')
    target_language = Column(String(10), nullable=False, default='en', comment='目标语言')
    status = Column(String(50), nullable=False, default='pending', comment='任务状态')
    progress = Column(Integer, nullable=False, default=0, comment='处理进度（0-100）')
    
    # 时间戳字段
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, 
                       onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系（一对多：一个任务有多个chunks）
    chunks = relationship('Chunk', back_populates='task', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<TranslationTask(id={self.id}, task_name='{self.task_name}', status='{self.status}')>"


class Chunk(Base):
    """Chunk表 - 存储原文和译文的chunk"""
    __tablename__ = 'chunks'
    
    # 主键
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 外键：关联到 TranslationTask
    task_id = Column(UUID(as_uuid=True), ForeignKey('translation_tasks.id'), 
                     nullable=False, index=True)
    
    # 普通字段
    chunk_type = Column(String(20), nullable=False, comment='chunk类型：source或target')
    chunk_index = Column(Integer, nullable=False, comment='chunk索引位置')
    content = Column(Text, nullable=False, comment='chunk内容')
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 关联关系
    task = relationship('TranslationTask', back_populates='chunks')
    
    def __repr__(self):
        return f"<Chunk(id={self.id}, chunk_type='{self.chunk_type}', chunk_index={self.chunk_index})>"


print("""
模型定义要点：

1. 继承 Base：
   class TranslationTask(Base):
       ...

2. 指定表名：
   __tablename__ = 'translation_tasks'

3. 定义字段：
   id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
   
   字段类型：
   - UUID(as_uuid=True)  # UUID类型
   - String(255)         # 字符串，最大长度255
   - Integer            # 整数
   - Text               # 长文本
   - DateTime           # 日期时间
   - JSON               # JSON数据
   - ForeignKey         # 外键

4. 字段参数：
   - primary_key=True   # 主键
   - nullable=False     # 不允许为空
   - default=value      # 默认值
   - index=True         # 创建索引
   - comment='说明'     # 字段注释

5. 关联关系：
   chunks = relationship('Chunk', back_populates='task')
   
   这表示：
   - TranslationTask 有多个 Chunk（一对多）
   - back_populates='task' 表示反向关系
""")

print("✓ 模型定义完成\n")


# ============================================================
# 第三部分：创建数据库连接和表
# ============================================================

print("=" * 80)
print("第三部分：创建数据库连接和表")
print("=" * 80)

# 数据库连接URL格式：postgresql://user:password@host:port/database
# 对于 SQLite（测试用）：
database_url = "sqlite:///tutorial.db"  # 使用 SQLite 作为示例

# 创建引擎（Engine）
engine = create_engine(database_url, echo=True)  # echo=True 会打印SQL语句

print(f"✓ 创建引擎: {database_url}")

# 创建会话工厂
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

print("✓ 创建会话工厂")

# 创建所有表
Base.metadata.create_all(engine)

print("✓ 创建数据库表\n")

print("""
关键概念：

1. Engine（引擎）：
   engine = create_engine(database_url)
   - 负责数据库连接
   - 管理连接池
   - 执行SQL语句

2. Session（会话）：
   SessionLocal = sessionmaker(bind=engine)
   - 类似数据库连接
   - 管理事务
   - 跟踪对象状态

3. 创建表：
   Base.metadata.create_all(engine)
   - 根据模型定义创建表
   - 如果表已存在，不会覆盖
""")


# ============================================================
# 第四部分：CRUD 操作 - Create（创建）
# ============================================================

print("=" * 80)
print("第四部分：CRUD 操作 - Create（创建）")
print("=" * 80)

# 创建会话
session = SessionLocal()

try:
    # 方法1：直接创建对象
    task1 = TranslationTask(
        task_name="测试任务1",
        source_language="zh",
        target_language="en",
        status="pending"
    )
    print(f"创建任务对象: {task1}")
    
    # 添加到会话（还未写入数据库）
    session.add(task1)
    print("✓ 添加到会话")
    
    # 提交事务（写入数据库）
    session.commit()
    print(f"✓ 提交成功，任务ID: {task1.id}")
    
    # 方法2：批量创建
    task2 = TranslationTask(
        task_name="测试任务2",
        source_language="en",
        target_language="zh",
        status="pending"
    )
    
    task3 = TranslationTask(
        task_name="测试任务3",
        source_language="zh",
        target_language="en",
        status="processing",
        progress=50
    )
    
    session.add_all([task2, task3])
    session.commit()
    print(f"✓ 批量创建成功，任务ID: {task2.id}, {task3.id}")
    
    # 方法3：创建关联对象（一对多）
    chunk1 = Chunk(
        task_id=task1.id,
        chunk_type="source",
        chunk_index=0,
        content="这是第一个chunk的内容"
    )
    
    chunk2 = Chunk(
        task_id=task1.id,
        chunk_type="target",
        chunk_index=0,
        content="This is the content of the first chunk"
    )
    
    session.add_all([chunk1, chunk2])
    session.commit()
    print(f"✓ 创建关联chunk成功")
    
    # 方法4：通过关系创建（更优雅）
    chunk3 = Chunk(
        chunk_type="source",
        chunk_index=1,
        content="这是第二个chunk的内容"
    )
    task1.chunks.append(chunk3)  # 通过关系添加
    session.commit()
    print(f"✓ 通过关系添加chunk成功")
    
except Exception as e:
    session.rollback()  # 发生错误时回滚
    print(f"❌ 错误: {e}")
finally:
    session.close()

print("""
创建操作要点：

1. 创建对象：
   task = TranslationTask(task_name="...", ...)

2. 添加到会话：
   session.add(task)        # 单个对象
   session.add_all([...])   # 多个对象

3. 提交事务：
   session.commit()         # 写入数据库

4. 错误处理：
   session.rollback()       # 回滚事务
   session.close()          # 关闭会话

5. 通过关系创建：
   task.chunks.append(chunk)  # 自动设置外键
""")


# ============================================================
# 第五部分：CRUD 操作 - Read（读取）
# ============================================================

print("=" * 80)
print("第五部分：CRUD 操作 - Read（读取）")
print("=" * 80)

session = SessionLocal()

try:
    # 方法1：查询所有记录
    all_tasks = session.query(TranslationTask).all()
    print(f"\n所有任务数量: {len(all_tasks)}")
    for task in all_tasks:
        print(f"  - {task}")
    
    # 方法2：查询单条记录（根据主键）
    if all_tasks:
        task_id = all_tasks[0].id
        task = session.query(TranslationTask).get(task_id)
        print(f"\n根据ID查询: {task}")
    
    # 方法3：条件查询（filter）
    pending_tasks = session.query(TranslationTask).filter(
        TranslationTask.status == 'pending'
    ).all()
    print(f"\n待处理任务数量: {len(pending_tasks)}")
    
    # 方法4：多个条件（and）
    zh_tasks = session.query(TranslationTask).filter(
        TranslationTask.source_language == 'zh',
        TranslationTask.status == 'pending'
    ).all()
    print(f"\n中文待处理任务数量: {len(zh_tasks)}")
    
    # 方法5：使用 filter_by（更简洁）
    zh_tasks2 = session.query(TranslationTask).filter_by(
        source_language='zh',
        status='pending'
    ).all()
    print(f"使用 filter_by 查询: {len(zh_tasks2)}")
    
    # 方法6：查询第一条记录
    first_task = session.query(TranslationTask).first()
    print(f"\n第一条任务: {first_task}")
    
    # 方法7：限制数量
    top_2_tasks = session.query(TranslationTask).limit(2).all()
    print(f"\n前2条任务: {len(top_2_tasks)}")
    
    # 方法8：排序
    sorted_tasks = session.query(TranslationTask).order_by(
        TranslationTask.created_at.desc()
    ).all()
    print(f"\n按创建时间倒序: {len(sorted_tasks)}")
    
    # 方法9：计数
    total_count = session.query(TranslationTask).count()
    print(f"\n总任务数: {total_count}")
    
    # 方法10：关联查询（通过关系）
    if all_tasks:
        task = all_tasks[0]
        print(f"\n任务 '{task.task_name}' 的chunks:")
        for chunk in task.chunks:
            print(f"  - {chunk}")
    
    # 方法11：JOIN 查询
    chunks_with_task = session.query(Chunk).join(TranslationTask).filter(
        TranslationTask.status == 'pending'
    ).all()
    print(f"\n待处理任务的chunks数量: {len(chunks_with_task)}")
    
finally:
    session.close()

print("""
查询操作要点：

1. 基本查询：
   session.query(Model).all()        # 所有记录
   session.query(Model).first()      # 第一条
   session.query(Model).get(id)      # 根据主键

2. 条件查询：
   .filter(Model.field == value)     # 等于
   .filter(Model.field != value)     # 不等于
   .filter(Model.field > value)      # 大于
   .filter(Model.field.like('%text%')) # LIKE

3. 链式查询：
   .filter(...).order_by(...).limit(...)

4. 关联查询：
   task.chunks                      # 通过关系访问
   .join(Model)                     # JOIN查询
""")


# ============================================================
# 第六部分：CRUD 操作 - Update（更新）
# ============================================================

print("=" * 80)
print("第六部分：CRUD 操作 - Update（更新）")
print("=" * 80)

session = SessionLocal()

try:
    # 方法1：直接修改对象属性
    task = session.query(TranslationTask).filter_by(status='pending').first()
    if task:
        print(f"更新前: {task}")
        task.status = 'processing'
        task.progress = 30
        session.commit()
        print(f"✓ 更新后: {task}")
    
    # 方法2：批量更新
    updated_count = session.query(TranslationTask).filter_by(
        status='pending'
    ).update({
        'status': 'processing',
        'progress': 10
    })
    session.commit()
    print(f"\n✓ 批量更新了 {updated_count} 条记录")
    
    # 方法3：更新关联对象
    if all_tasks:
        task = all_tasks[0]
        if task.chunks:
            chunk = task.chunks[0]
            print(f"\n更新chunk前: {chunk}")
            chunk.content = "更新后的内容"
            session.commit()
            print(f"✓ 更新chunk后: {chunk}")
    
finally:
    session.close()

print("""
更新操作要点：

1. 修改对象属性：
   task.status = 'new_status'
   session.commit()

2. 批量更新：
   session.query(Model).filter(...).update({...})

3. 自动更新时间戳：
   updated_at = Column(DateTime, onupdate=datetime.utcnow)
   # 更新时自动设置
""")


# ============================================================
# 第七部分：CRUD 操作 - Delete（删除）
# ============================================================

print("=" * 80)
print("第七部分：CRUD 操作 - Delete（删除）")
print("=" * 80)

session = SessionLocal()

try:
    # 方法1：删除对象
    task_to_delete = session.query(TranslationTask).filter_by(
        task_name="测试任务3"
    ).first()
    
    if task_to_delete:
        print(f"删除任务: {task_to_delete}")
        session.delete(task_to_delete)
        session.commit()
        print("✓ 删除成功")
        # 注意：由于 cascade='all, delete-orphan'，关联的chunks也会被删除
    
    # 方法2：批量删除
    deleted_count = session.query(TranslationTask).filter_by(
        status='completed'
    ).delete()
    session.commit()
    print(f"\n✓ 批量删除了 {deleted_count} 条记录")
    
finally:
    session.close()

print("""
删除操作要点：

1. 删除对象：
   session.delete(object)
   session.commit()

2. 批量删除：
   session.query(Model).filter(...).delete()

3. 级联删除：
   cascade='all, delete-orphan'  # 删除父对象时，子对象也会被删除
""")


# ============================================================
# 第八部分：高级查询技巧
# ============================================================

print("=" * 80)
print("第八部分：高级查询技巧")
print("=" * 80)

session = SessionLocal()

try:
    from sqlalchemy import or_, and_, func
    
    # 1. OR 条件
    tasks = session.query(TranslationTask).filter(
        or_(
            TranslationTask.status == 'pending',
            TranslationTask.status == 'processing'
        )
    ).all()
    print(f"OR条件查询: {len(tasks)} 条")
    
    # 2. IN 查询
    tasks = session.query(TranslationTask).filter(
        TranslationTask.status.in_(['pending', 'processing'])
    ).all()
    print(f"IN查询: {len(tasks)} 条")
    
    # 3. 聚合函数
    from sqlalchemy import func
    avg_progress = session.query(func.avg(TranslationTask.progress)).scalar()
    print(f"平均进度: {avg_progress}")
    
    max_progress = session.query(func.max(TranslationTask.progress)).scalar()
    print(f"最大进度: {max_progress}")
    
    # 4. 分组查询
    status_count = session.query(
        TranslationTask.status,
        func.count(TranslationTask.id)
    ).group_by(TranslationTask.status).all()
    print(f"\n按状态分组:")
    for status, count in status_count:
        print(f"  {status}: {count}")
    
    # 5. 子查询
    subquery = session.query(Chunk.task_id).filter(
        Chunk.chunk_type == 'source'
    ).subquery()
    
    tasks_with_source_chunks = session.query(TranslationTask).filter(
        TranslationTask.id.in_(subquery)
    ).all()
    print(f"\n有source chunks的任务: {len(tasks_with_source_chunks)}")
    
finally:
    session.close()

print("""
高级查询技巧：

1. OR条件：
   .filter(or_(condition1, condition2))

2. IN查询：
   .filter(Model.field.in_([value1, value2]))

3. 聚合函数：
   func.count(), func.avg(), func.max(), func.min()

4. 分组：
   .group_by(Model.field)

5. 子查询：
   .subquery()
""")


# ============================================================
# 第九部分：会话管理最佳实践
# ============================================================

print("=" * 80)
print("第九部分：会话管理最佳实践")
print("=" * 80)

print("""
最佳实践：

1. 使用上下文管理器（推荐）：
   with SessionLocal() as session:
       # 使用session
       session.commit()
   # 自动关闭

2. 使用 try-finally：
   session = SessionLocal()
   try:
       # 使用session
       session.commit()
   except:
       session.rollback()
   finally:
       session.close()

3. 使用装饰器模式：
   def with_session(func):
       def wrapper(*args, **kwargs):
           session = SessionLocal()
           try:
               return func(session, *args, **kwargs)
           finally:
               session.close()
       return wrapper
""")

# 示例：上下文管理器
def create_task_with_context(task_name: str):
    """使用上下文管理器创建任务"""
    with SessionLocal() as session:
        task = TranslationTask(task_name=task_name)
        session.add(task)
        session.commit()
        return task

print("✓ 上下文管理器示例已定义")


# ============================================================
# 第十部分：数据库管理器模式（参考 database.py）
# ============================================================

print("=" * 80)
print("第十部分：数据库管理器模式")
print("=" * 80)

class DatabaseManager:
    """数据库管理器 - 封装数据库操作"""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False
        )
        Base.metadata.create_all(self.engine)
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()
    
    def create_tables(self):
        """创建所有表"""
        Base.metadata.create_all(self.engine)
    
    def drop_tables(self):
        """删除所有表（谨慎使用）"""
        Base.metadata.drop_all(self.engine)


# 使用示例
db_manager = DatabaseManager("sqlite:///tutorial.db")

# 获取会话
session = db_manager.get_session()

try:
    # 使用会话进行操作
    task = TranslationTask(task_name="通过管理器创建的任务")
    session.add(task)
    session.commit()
    print(f"✓ 通过管理器创建任务: {task.id}")
finally:
    session.close()

print("""
数据库管理器模式的优势：

1. 封装数据库连接逻辑
2. 统一管理会话
3. 便于配置和扩展
4. 符合单一职责原则
""")


print("\n" + "=" * 80)
print("教程完成！")
print("=" * 80)
print("""
总结：

1. 模型定义：继承 Base，定义字段和关系
2. 创建连接：create_engine() 和 sessionmaker()
3. CRUD操作：
   - Create: session.add(), session.commit()
   - Read: session.query().filter().all()
   - Update: 修改属性，session.commit()
   - Delete: session.delete(), session.commit()
4. 会话管理：使用上下文管理器或 try-finally
5. 最佳实践：使用数据库管理器封装操作

更多信息请参考：
- SQLAlchemy 官方文档：https://docs.sqlalchemy.org/
- database.py 中的实际应用示例
""")

