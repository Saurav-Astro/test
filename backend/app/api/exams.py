from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import json
import uuid
from sqlalchemy import select, delete
from app.core.sqlite import async_session, LocalExam, LocalUser
from app.core.security import get_current_user, require_faculty

router = APIRouter(prefix="/exams", tags=["Exams"])

class CreateExamSchema(BaseModel):
    title: str
    description: Optional[str] = None
    sections: List[dict] = []
    is_published: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    allowed_students: List[str] = []

@router.get("/")
async def list_exams(user: LocalUser = Depends(require_faculty)):
    async with async_session() as session:
        stmt = select(LocalExam)
        result = await session.execute(stmt)
        exams = result.scalars().all()
        res = []
        for e in exams:
            res.append({
                "id": str(e.id),
                "title": e.title,
                "is_published": e.is_published,
                "created_at": e.created_at
            })
        return res

@router.post("/")
async def create_exam(data: CreateExamSchema, user: LocalUser = Depends(require_faculty)):
    async with async_session() as session:
        exam = LocalExam(
            id=str(uuid.uuid4()),
            title=data.title,
            description=data.description,
            created_by=str(user.id),
            content=data.model_dump(),
            is_published=data.is_published
        )
        session.add(exam)
        await session.commit()
        return {"id": exam.id}

@router.get("/available")
async def available_exams(user: LocalUser = Depends(get_current_user)):
    async with async_session() as session:
        stmt = select(LocalExam).where(LocalExam.is_published == True)
        result = await session.execute(stmt)
        exams = result.scalars().all()
        res = []
        for e in exams:
            res.append({
                "id": e.id,
                "title": e.title,
                "description": e.description
            })
        return res

@router.get("/{exam_id}/student")
async def get_exam_for_student(exam_id: str, user: LocalUser = Depends(get_current_user)):
    async with async_session() as session:
        exam = await session.get(LocalExam, exam_id)
        if not exam or not exam.is_published:
            raise HTTPException(status_code=404, detail="Exam not found")
        return exam.content
