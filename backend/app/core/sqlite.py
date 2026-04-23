import os
import json
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, Float, ForeignKey
from datetime import datetime

SQLITE_URL = "sqlite+aiosqlite:///./proxm_local.db"

engine = create_async_engine(SQLITE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class LocalUser(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password_hash = Column(String)
    role = Column(String, default="student")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class LocalExam(Base):
    __tablename__ = "exams"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    description = Column(String, nullable=True)
    created_by = Column(String)  # User ID
    content = Column(JSON)  # Stores sections, questions, etc.
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class LocalAttempt(Base):
    __tablename__ = "attempts"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id = Column(String)
    student_id = Column(String)
    status = Column(String, default="in_progress")  # in_progress, submitted, terminated
    data = Column(JSON)  # Stores sections, answers, etc.
    total_score = Column(Float, default=0.0)
    max_score = Column(Float, default=0.0)
    violation_count = Column(Integer, default=0)
    terminated_reason = Column(String, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)

class LocalProctoringLog(Base):
    __tablename__ = "proctoring_logs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    attempt_id = Column(String)
    student_id = Column(String)
    exam_id = Column(String)
    event_type = Column(String)
    section_index = Column(Integer, nullable=True)
    question_index = Column(Integer, nullable=True)
    detail = Column(String, nullable=True)
    severity = Column(String, default="info")
    timestamp = Column(DateTime, default=datetime.utcnow)

class LocalOTP(Base):
    __tablename__ = "otp_records"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String)
    otp = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    used = Column(Boolean, default=False)

async def init_sqlite():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] Local SQLite Database Initialized")
