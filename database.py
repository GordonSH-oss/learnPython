"""
数据库模型定义 - 翻译数据持久化存储
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class TranslationTask(Base):
    """翻译任务表"""
    __tablename__ = 'translation_tasks'
    
    # 主键：任务ID（UUID）
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 任务基本信息
    task_name = Column(String(255), nullable=False, comment='任务名称')
    source_language = Column(String(10), nullable=False, default='zh', comment='源语言')
    target_language = Column(String(10), nullable=False, default='en', comment='目标语言')
    processing_mode = Column(String(50), nullable=False, comment='处理模式：translate, polish等')
    translation_prompt_type = Column(String(50), nullable=True, comment='翻译提示词类型：translate, translate_ux')
    
    # 文档信息
    source_file_path = Column(String(512), nullable=True, comment='源文件路径')
    source_file_name = Column(String(255), nullable=True, comment='源文件名')
    source_file_size = Column(Integer, nullable=True, comment='源文件大小（字节）')
    output_file_path = Column(String(512), nullable=True, comment='输出文件路径')
    
    # 处理状态
    status = Column(String(50), nullable=False, default='pending', comment='任务状态：pending, processing, completed, failed')
    progress = Column(Integer, nullable=False, default=0, comment='处理进度（0-100）')
    
    # 统计信息
    total_chunks = Column(Integer, nullable=False, default=0, comment='总chunk数量')
    completed_chunks = Column(Integer, nullable=False, default=0, comment='已完成chunk数量')
    failed_chunks = Column(Integer, nullable=False, default=0, comment='失败的chunk数量')
    
    # 性能指标
    processing_time = Column(Float, nullable=True, comment='处理时间（秒）')
    total_tokens = Column(Integer, nullable=True, comment='总token数')
    
    # 错误信息
    error_message = Column(Text, nullable=True, comment='错误信息')
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    completed_at = Column(DateTime, nullable=True, comment='完成时间')
    
    # 关联关系
    chunks = relationship('Chunk', back_populates='task', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<TranslationTask(id={self.id}, task_name='{self.task_name}', status='{self.status}')>"


class Chunk(Base):
    """Chunk表 - 存储原文和译文的chunk，通过chunk_id关联"""
    __tablename__ = 'chunks'
    
    # 主键：Chunk ID（UUID）- 这是原文和译文chunk的关联ID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 关联的任务ID
    task_id = Column(UUID(as_uuid=True), ForeignKey('translation_tasks.id'), nullable=False, index=True)
    
    # Chunk标识：同一个chunk的原文和译文共享这个ID
    chunk_id = Column(UUID(as_uuid=True), nullable=False, index=True, comment='Chunk唯一标识，原文和译文共享')
    
    # Chunk类型：source（原文）或 target（译文）
    chunk_type = Column(String(20), nullable=False, comment='chunk类型：source（原文）或target（译文）')
    
    # Chunk位置信息
    chunk_index = Column(Integer, nullable=False, comment='chunk在文档中的索引位置（从0开始）')
    total_chunks = Column(Integer, nullable=False, comment='文档总chunk数量')
    
    # Chunk内容
    content = Column(Text, nullable=False, comment='chunk内容')
    content_length = Column(Integer, nullable=False, comment='内容长度（字符数）')
    
    # Chunk元数据（JSON格式存储）
    chunk_metadata = Column(JSON, nullable=True, comment='chunk元数据：headers, chunk_type, start_line, end_line等')
    
    # 文档章节信息
    document_section = Column(String(512), nullable=True, comment='文档章节信息')
    
    # 处理状态
    status = Column(String(50), nullable=False, default='pending', comment='处理状态：pending, processing, completed, failed')
    
    # 翻译相关
    translation_method = Column(String(50), nullable=True, comment='翻译方法：react_agent, direct等')
    translation_steps = Column(Integer, nullable=True, comment='翻译步骤数（ReAct agent）')
    
    # 性能指标
    processing_time = Column(Float, nullable=True, comment='处理时间（秒）')
    tokens_used = Column(Integer, nullable=True, comment='使用的token数')
    
    # 错误信息
    error_message = Column(Text, nullable=True, comment='错误信息')
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    task = relationship('TranslationTask', back_populates='chunks')
    context_data = relationship('ChunkContext', back_populates='chunk', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Chunk(id={self.id}, chunk_id={self.chunk_id}, chunk_type='{self.chunk_type}', chunk_index={self.chunk_index})>"


class ChunkContext(Base):
    """Chunk上下文数据表"""
    __tablename__ = 'chunk_contexts'
    
    # 主键
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 关联的chunk ID
    chunk_id = Column(UUID(as_uuid=True), ForeignKey('chunks.id'), nullable=False, index=True)
    
    # 上下文信息
    previous_chunk_translation = Column(Text, nullable=True, comment='前一个chunk的翻译结果')
    following_chunk_preview = Column(Text, nullable=True, comment='后续chunk的预览')
    
    # 术语缓存（JSON格式）
    terminology_cache = Column(JSON, nullable=True, comment='术语缓存')
    
    # 验证和风格信息
    validation_issues = Column(JSON, nullable=True, comment='验证问题列表')
    style_violations = Column(JSON, nullable=True, comment='风格违规列表')
    style_improvements = Column(JSON, nullable=True, comment='风格改进建议列表')
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    chunk = relationship('Chunk', back_populates='context_data')
    
    def __repr__(self):
        return f"<ChunkContext(id={self.id}, chunk_id={self.chunk_id})>"


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, database_url: str):
        """
        初始化数据库管理器
        
        Args:
            database_url: PostgreSQL数据库连接URL
                格式：postgresql://user:password@host:port/database
        """
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
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


# 全局数据库管理器实例（延迟初始化）
_db_manager: Optional[DatabaseManager] = None


def init_database(database_url: str):
    """初始化数据库连接"""
    global _db_manager
    _db_manager = DatabaseManager(database_url)
    return _db_manager


def get_db_manager() -> DatabaseManager:
    """获取数据库管理器实例"""
    if _db_manager is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _db_manager


def get_db_session() -> Session:
    """获取数据库会话（用于with语句）"""
    return get_db_manager().get_session()

