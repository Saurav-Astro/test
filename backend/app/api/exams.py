from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import json

from app.models.exam import Exam, Section, Question
from app.models.user import User
from app.models.faculty_user import FacultyUser
from app.core.security import get_current_user
from beanie import PydanticObjectId
from app.core.sqlite import async_session, LocalExam
from sqlalchemy import select

router = APIRouter(prefix="/exams", tags=["Exams"])

class CreateExamSchema(BaseModel):
    title: str
    description: Optional[str] = None
    sections: List[dict] = []
    is_published: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    allowed_students: List[str] = []
    entry_question: Optional[str] = None
    entry_password: Optional[str] = None
    shuffle_questions: bool = False
    shuffle_options: bool = False
    show_result_immediately: bool = False

@router.get("/")
async def list_exams(user: FacultyUser = Depends(get_current_user)):
    if user.role not in ("faculty", "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    query = Exam.find(Exam.created_by == user.id)
    exams = await query.to_list()
    res = []
    for e in exams:
        res.append({
            "id": str(e.id),
            "title": e.title,
            "created_at": e.created_at,
            "is_published": e.is_published,
            "section_count": len(e.sections)
        })
    return res

@router.post("/")
async def create_exam(data: CreateExamSchema, user: FacultyUser = Depends(get_current_user)):
    if user.role not in ("faculty", "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    sections = []
    for i, s_data in enumerate(data.sections):
        questions = []
        for q_data in s_data.get("questions", []):
            q = Question(**q_data)
            questions.append(q)
        s_data["questions"] = questions
        s_data["order"] = i
        sections.append(Section(**s_data))

    allowed = []
    for s in data.allowed_students:
        try:
            allowed.append(PydanticObjectId(s))
        except:
            pass

    exam = Exam(
        title=data.title,
        description=data.description,
        created_by=user.id,
        sections=sections,
        is_published=data.is_published,
        start_time=data.start_time,
        end_time=data.end_time,
        allowed_students=allowed,
        entry_question=data.entry_question,
        entry_password=data.entry_password,
        shuffle_questions=data.shuffle_questions,
        shuffle_options=data.shuffle_options,
        show_result_immediately=data.show_result_immediately
    )
    await exam.insert()
    
    # Sync to Local SQLite
    async with async_session() as session:
        local_e = LocalExam(
            id=str(exam.id),
            title=exam.title,
            description=exam.description,
            content=json.loads(exam.model_dump_json()),
            is_published=exam.is_published
        )
        session.add(local_e)
        await session.commit()

    return {"id": str(exam.id)}

@router.get("/available")
async def available_exams(user: User = Depends(get_current_user)):
    # Read from LOCAL SQLite for speed
    async with async_session() as session:
        stmt = select(LocalExam).where(LocalExam.is_published == True)
        result = await session.execute(stmt)
        local_exams = result.scalars().all()
        
        res = []
        for e in local_exams:
            c = e.content
            res.append({
                "id": str(e.id),
                "title": e.title,
                "description": e.description,
                "start_time": c.get("start_time"),
                "end_time": c.get("end_time"),
                "section_count": len(c.get("sections", [])),
                "duration_minutes": sum(s.get("time_limit_minutes", 0) for s in c.get("sections", []))
            })
        return res

@router.get("/{exam_id}/student")
async def get_exam_for_student(exam_id: str, user: User = Depends(get_current_user)):
    # Try local first
    async with async_session() as session:
        local_e = await session.get(LocalExam, exam_id)
        if local_e:
            exam_data = local_e.content
        else:
            # Fallback to Mongo
            exam = await Exam.get(exam_id)
            if not exam:
                raise HTTPException(status_code=404, detail="Exam not found")
            exam_data = json.loads(exam.model_dump_json())

    if not exam_data.get("is_published"):
        raise HTTPException(status_code=404, detail="Exam not found")

    sections_safe = []
    for sec in exam_data.get("sections", []):
        questions_safe = []
        for q in sec.get("questions", []):
            opts = [{"text": o.get("text", "")} for o in q.get("options", [])]
            questions_safe.append({
                "question_text": q.get("question_text"),
                "question_type": q.get("question_type"),
                "options": opts,
                "starter_code": q.get("starter_code"),
                "language": q.get("language"),
                "test_cases": [tc for tc in q.get("test_cases", []) if not tc.get("is_hidden")],
                "marks": q.get("marks"),
                "time_limit_seconds": q.get("time_limit_seconds"),
            })
        sections_safe.append({
            "title": sec.get("title"),
            "description": sec.get("description"),
            "time_limit_minutes": sec.get("time_limit_minutes"),
            "time_per_question_seconds": sec.get("time_per_question_seconds"),
            "questions": questions_safe,
            "proctoring": sec.get("proctoring"),
        })
    
    return {
        "id": exam_id,
        "title": exam_data.get("title"),
        "description": exam_data.get("description"),
        "sections": sections_safe,
        "shuffle_questions": exam_data.get("shuffle_questions"),
        "shuffle_options": exam_data.get("shuffle_options"),
    }

@router.get("/{exam_id}")
async def get_exam(exam_id: str, user: FacultyUser = Depends(get_current_user)):
    if user.role not in ("faculty", "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    exam = await Exam.get(exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    d = exam.model_dump()
    d["id"] = str(exam.id)
    d["created_by"] = str(exam.created_by)
    d["allowed_students"] = [str(sid) for sid in exam.allowed_students]
    return d

@router.put("/{exam_id}")
async def update_exam(exam_id: str, data: CreateExamSchema, user: FacultyUser = Depends(get_current_user)):
    if user.role not in ("faculty", "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    exam = await Exam.get(exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    sections = []
    for i, s_data in enumerate(data.sections):
        questions = []
        for q_data in s_data.get("questions", []):
            q = Question(**q_data)
            questions.append(q)
        s_data["questions"] = questions
        s_data["order"] = i
        sections.append(Section(**s_data))

    allowed = []
    for s in data.allowed_students:
        try:
            allowed.append(PydanticObjectId(s))
        except:
            pass

    exam.title = data.title
    exam.description = data.description
    exam.sections = sections
    exam.is_published = data.is_published
    exam.start_time = data.start_time
    exam.end_time = data.end_time
    exam.allowed_students = allowed
    exam.entry_question = data.entry_question
    exam.entry_password = data.entry_password
    exam.shuffle_questions = data.shuffle_questions
    exam.shuffle_options = data.shuffle_options
    exam.show_result_immediately = data.show_result_immediately
    exam.updated_at = datetime.utcnow()

    await exam.save()
    
    # Sync to Local SQLite
    async with async_session() as session:
        local_e = await session.get(LocalExam, str(exam.id))
        if local_e:
            local_e.title = exam.title
            local_e.description = exam.description
            local_e.content = json.loads(exam.model_dump_json())
            local_e.is_published = exam.is_published
            await session.commit()

    return {"message": "Updated"}
