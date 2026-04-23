import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, Float
from datetime import datetime

SQLITE_URL = "sqlite+aiosqlite:///./proxm_local.db"

engine = create_async_engine(SQLITE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class LocalExam(Base):
    __tablename__ = "exams"
    id = Column(String, primary_key=True)
    title = Column(String)
    description = Column(String, nullable=True)
    content = Column(JSON)  # Stores sections, questions, etc.
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class LocalAttempt(Base):
    __tablename__ = "attempts"
    id = Column(String, primary_key=True)
    exam_id = Column(String)
    student_id = Column(String)
    status = Column(String)
    data = Column(JSON)  # Stores sections, answers, etc.
    total_score = Column(Float, default=0.0)
    max_score = Column(Float, default=0.0)
    started_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)

async def init_sqlite():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] Local SQLite Database Initialized")
