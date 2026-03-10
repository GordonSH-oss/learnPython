"""
SQLAlchemy 实战示例 - 基于 database.py

演示如何使用 database.py 中的模型进行 CRUD 操作
"""

from database import (
    init_database, 
    get_db_session,
    TranslationTask, 
    Chunk,
    ChunkContext
)

# ============================================================
# 第一步：初始化数据库
# ============================================================

# 使用 SQLite 作为示例（生产环境使用 PostgreSQL）
database_url = "sqlite:///example.db"

# 初始化数据库连接
db_manager = init_database(database_url)
print("✓ 数据库初始化成功\n")


# ============================================================
# 第二步：创建数据（Create）
# ============================================================

print("=" * 60)
print("创建数据示例")
print("=" * 60)

session = get_db_session()

try:
    # 创建翻译任务
    task = TranslationTask(
        task_name="Python 文档翻译任务",
        source_language="zh",
        target_language="en",
        processing_mode="translate",
        translation_prompt_type="translate_ux",
        source_file_name="python_docs.md",
        status="pending",
        progress=0,
        total_chunks=3
    )
    session.add(task)
    session.flush()  # 获取 task.id，但不提交
    
    print(f"✓ 创建任务: {task.task_name} (ID: {task.id})")
    
    # 创建原文 chunks
    source_chunks = [
        {
            "chunk_index": 0,
            "content": "Python 是一种高级编程语言，以其简洁和可读性而闻名。",
            "chunk_metadata": {
                "headers": ["# Python 简介"],
                "chunk_type": "paragraph",
                "start_line": 1,
                "end_line": 3
            }
        },
        {
            "chunk_index": 1,
            "content": "Python 支持多种编程范式，包括面向对象、函数式和过程式编程。",
            "chunk_metadata": {
                "headers": ["## 编程范式"],
                "chunk_type": "paragraph",
                "start_line": 4,
                "end_line": 6
            }
        },
        {
            "chunk_index": 2,
            "content": "Python 拥有丰富的标准库和第三方库生态系统。",
            "chunk_metadata": {
                "headers": ["## 库生态系统"],
                "chunk_type": "paragraph",
                "start_line": 7,
                "end_line": 9
            }
        }
    ]
    
    import uuid
    chunk_ids = []
    
    for chunk_data in source_chunks:
        chunk_id = uuid.uuid4()  # 原文和译文共享的 chunk_id
        
        chunk = Chunk(
            task_id=task.id,
            chunk_id=chunk_id,
            chunk_type="source",
            chunk_index=chunk_data["chunk_index"],
            total_chunks=len(source_chunks),
            content=chunk_data["content"],
            content_length=len(chunk_data["content"]),
            chunk_metadata=chunk_data["chunk_metadata"],
            document_section=chunk_data["chunk_metadata"]["headers"][0] if chunk_data["chunk_metadata"]["headers"] else None,
            status="completed"
        )
        session.add(chunk)
        chunk_ids.append(chunk_id)
    
    print(f"✓ 创建了 {len(source_chunks)} 个原文 chunks")
    
    # 创建译文 chunks（示例）
    target_contents = [
        "Python is a high-level programming language known for its simplicity and readability.",
        "Python supports multiple programming paradigms, including object-oriented, functional, and procedural programming.",
        "Python has a rich ecosystem of standard libraries and third-party libraries."
    ]
    
    for i, (chunk_id, content) in enumerate(zip(chunk_ids, target_contents)):
        chunk = Chunk(
            task_id=task.id,
            chunk_id=chunk_id,  # 使用相同的 chunk_id
            chunk_type="target",
            chunk_index=i,
            total_chunks=len(target_contents),
            content=content,
            content_length=len(content),
            status="completed"
        )
        session.add(chunk)
    
    print(f"✓ 创建了 {len(target_contents)} 个译文 chunks")
    
    # 创建上下文数据（示例）
    if chunk_ids:
        source_chunk = session.query(Chunk).filter_by(
            chunk_id=chunk_ids[0],
            chunk_type="source"
        ).first()
        
        if source_chunk:
            context = ChunkContext(
                chunk_id=source_chunk.id,
                previous_chunk_translation=None,  # 第一个chunk没有前一个
                following_chunk_preview=target_contents[1][:50] + "..." if len(target_contents) > 1 else None,
                terminology_cache={"Python": "Python", "编程语言": "programming language"}
            )
            session.add(context)
            print("✓ 创建了上下文数据")
    
    # 提交所有更改
    session.commit()
    print(f"\n✓ 所有数据已保存到数据库\n")
    
except Exception as e:
    session.rollback()
    print(f"❌ 错误: {e}")
    raise
finally:
    session.close()


# ============================================================
# 第三步：查询数据（Read）
# ============================================================

print("=" * 60)
print("查询数据示例")
print("=" * 60)

session = get_db_session()

try:
    # 查询所有任务
    all_tasks = session.query(TranslationTask).all()
    print(f"\n所有任务数量: {len(all_tasks)}")
    
    if all_tasks:
        task = all_tasks[0]
        print(f"\n任务详情:")
        print(f"  ID: {task.id}")
        print(f"  名称: {task.task_name}")
        print(f"  状态: {task.status}")
        print(f"  进度: {task.progress}%")
        print(f"  源语言: {task.source_language} -> 目标语言: {task.target_language}")
        print(f"  创建时间: {task.created_at}")
        
        # 通过关系查询关联的 chunks
        print(f"\n关联的 Chunks ({len(task.chunks)} 个):")
        for chunk in task.chunks:
            print(f"  - {chunk.chunk_type}: {chunk.content[:50]}...")
            print(f"    chunk_id: {chunk.chunk_id}, index: {chunk.chunk_index}")
        
        # 查询特定类型的 chunks
        source_chunks = session.query(Chunk).filter_by(
            task_id=task.id,
            chunk_type="source"
        ).all()
        
        print(f"\n原文 Chunks ({len(source_chunks)} 个):")
        for chunk in source_chunks:
            print(f"  [{chunk.chunk_index}] {chunk.content[:60]}...")
            if chunk.chunk_metadata:
                print(f"      元数据: {chunk.chunk_metadata.get('headers', [])}")
        
        # 查询译文 chunks
        target_chunks = session.query(Chunk).filter_by(
            task_id=task.id,
            chunk_type="target"
        ).all()
        
        print(f"\n译文 Chunks ({len(target_chunks)} 个):")
        for chunk in target_chunks:
            print(f"  [{chunk.chunk_index}] {chunk.content[:60]}...")
        
        # 查询通过 chunk_id 关联的原文和译文
        if source_chunks:
            chunk_id = source_chunks[0].chunk_id
            source_chunk = session.query(Chunk).filter_by(
                chunk_id=chunk_id,
                chunk_type="source"
            ).first()
            
            target_chunk = session.query(Chunk).filter_by(
                chunk_id=chunk_id,
                chunk_type="target"
            ).first()
            
            if source_chunk and target_chunk:
                print(f"\n通过 chunk_id 关联的原文和译文:")
                print(f"  原文: {source_chunk.content}")
                print(f"  译文: {target_chunk.content}")
    
finally:
    session.close()


# ============================================================
# 第四步：更新数据（Update）
# ============================================================

print("\n" + "=" * 60)
print("更新数据示例")
print("=" * 60)

session = get_db_session()

try:
    # 更新任务状态
    task = session.query(TranslationTask).filter_by(
        task_name="Python 文档翻译任务"
    ).first()
    
    if task:
        print(f"\n更新前: 状态={task.status}, 进度={task.progress}%")
        
        task.status = "processing"
        task.progress = 50
        task.completed_chunks = 2
        
        session.commit()
        
        print(f"✓ 更新后: 状态={task.status}, 进度={task.progress}%")
        
        # 更新 chunk 内容
        chunk = session.query(Chunk).filter_by(
            task_id=task.id,
            chunk_type="target",
            chunk_index=0
        ).first()
        
        if chunk:
            print(f"\n更新 chunk 内容:")
            print(f"  更新前: {chunk.content[:50]}...")
            chunk.content = "Python is a high-level programming language, renowned for its simplicity and readability."
            chunk.content_length = len(chunk.content)
            session.commit()
            print(f"  更新后: {chunk.content[:50]}...")
    
finally:
    session.close()


# ============================================================
# 第五步：高级查询示例
# ============================================================

print("\n" + "=" * 60)
print("高级查询示例")
print("=" * 60)

session = get_db_session()

try:
    from sqlalchemy import func
    
    # 统计查询
    total_tasks = session.query(TranslationTask).count()
    pending_tasks = session.query(TranslationTask).filter_by(
        status="pending"
    ).count()
    processing_tasks = session.query(TranslationTask).filter_by(
        status="processing"
    ).count()
    
    print(f"\n任务统计:")
    print(f"  总任务数: {total_tasks}")
    print(f"  待处理: {pending_tasks}")
    print(f"  处理中: {processing_tasks}")
    
    # 平均进度
    avg_progress = session.query(
        func.avg(TranslationTask.progress)
    ).scalar()
    print(f"  平均进度: {avg_progress:.2f}%")
    
    # 按状态分组统计
    status_stats = session.query(
        TranslationTask.status,
        func.count(TranslationTask.id)
    ).group_by(TranslationTask.status).all()
    
    print(f"\n按状态分组:")
    for status, count in status_stats:
        print(f"  {status}: {count}")
    
    # JOIN 查询：查询有 source chunks 的任务
    tasks_with_chunks = session.query(TranslationTask).join(Chunk).filter(
        Chunk.chunk_type == "source"
    ).distinct().all()
    
    print(f"\n有 source chunks 的任务: {len(tasks_with_chunks)}")
    
finally:
    session.close()


# ============================================================
# 第六步：删除数据示例（谨慎使用）
# ============================================================

print("\n" + "=" * 60)
print("删除数据示例（注释掉，避免误删）")
print("=" * 60)

print("""
# 删除示例代码（已注释）：

session = get_db_session()
try:
    # 删除任务（级联删除关联的 chunks）
    task = session.query(TranslationTask).filter_by(
        task_name="Python 文档翻译任务"
    ).first()
    
    if task:
        print(f"删除任务: {task.task_name}")
        session.delete(task)  # 由于 cascade，chunks 也会被删除
        session.commit()
        print("✓ 删除成功")
finally:
    session.close()
""")

print("\n" + "=" * 60)
print("示例完成！")
print("=" * 60)
print("""
总结：
1. ✅ 初始化数据库连接
2. ✅ 创建数据（任务、chunks、上下文）
3. ✅ 查询数据（基本查询、关联查询）
4. ✅ 更新数据（修改字段）
5. ✅ 高级查询（统计、分组、JOIN）
6. ✅ 删除数据（级联删除）

更多用法请参考：
- database.py - 模型定义
- SQLALCHEMY_QUICK_REFERENCE.md - 快速参考
- sqlalchemy_tutorial.py - 完整教程
""")

