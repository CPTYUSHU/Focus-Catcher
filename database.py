"""
Focus Catcher - Database Models
数据库模型定义
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# 数据库配置
DATABASE_URL = "sqlite:///./focus_catcher.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 学习会话表
class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String, default="active")  # active, completed, abandoned
    
    # AI 生成的总结（批量分析后填充）
    core_goal = Column(Text, nullable=True)
    main_thread = Column(Text, nullable=True)
    branches = Column(Text, nullable=True)
    action_guide = Column(Text, nullable=True)
    
    # 关联的捕捉记录
    captures = relationship("Capture", back_populates="session")


# 捕捉记录表
class Capture(Base):
    __tablename__ = "captures"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    
    # 捕捉的原始数据
    selected_text = Column(Text)
    page_url = Column(String)
    page_title = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # AI 分析结果（批量分析后填充）
    focus_point = Column(Text, nullable=True)
    content_type = Column(String, nullable=True)
    suggested_action = Column(Text, nullable=True)
    
    # 关联的会话
    session = relationship("Session", back_populates="captures")


# 创建所有表
def init_db():
    Base.metadata.create_all(bind=engine)


# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

