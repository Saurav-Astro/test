from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy import delete, select
from app.core.sqlite import async_session, LocalAttempt, LocalExam, LocalUser
from app.core.security import get_current_user
from pydantic import BaseModel, Field
from app.services.code_service import execute_code, run_test_cases

router = APIRouter(prefix="/attempts", tags=["Attempts"])

class StartAttemptSchema(BaseModel):
    exam_id: str

class RunCodeSchema(BaseModel):
    attempt_id: Optional[str] = None
    exam_id: Optional[str] = None
    section_index: int
    question_index: int
    code: str
    language: str
    stdin: str = Field(default="", alias="input")
    run_tests: bool = False
    class Config:
        populate_by_name = True

class SubmitSectionSchema(BaseModel):
    exam_id: str
    section_index: int

class SubmitAnswerSchema(BaseModel):
    exam_id: str
    section_index: int
    question_index: int
    selected_option: Optional[int] = None
    code_submission: Optional[str] = None
    time_spent_seconds: int = 0

class SubmitExamSchema(BaseModel):
    attempt_id: str

@router.post("/start")
async def start_attempt(data: StartAttemptSchema, user: LocalUser = Depends(get_current_user)):
    async with async_session() as session:
        exam = await session.get(LocalExam, data.exam_id)
        if not exam:
            raise HTTPException(404, "Exam not found")
        await session.execute(delete(LocalAttempt).where(
            LocalAttempt.exam_id == data.exam_id, LocalAttempt.student_id == str(user.id)))
        a = LocalAttempt(id=str(uuid.uuid4()), exam_id=data.exam_id, student_id=str(user.id),
                         status="in_progress", data={"sections": [], "answers": {}}, started_at=datetime.utcnow())
        session.add(a); await session.commit(); await session.refresh(a)
        return {"id": a.id, "status": a.status, "violation_count": 0}

@router.post("/execute")
async def execute(data: RunCodeSchema, user: LocalUser = Depends(get_current_user)):
    async with async_session() as session:
        exam_id = data.exam_id
        if not exam_id and data.attempt_id:
            at = await session.get(LocalAttempt, data.attempt_id)
            if at: exam_id = at.exam_id
        if not exam_id: raise HTTPException(400, "exam_id or attempt_id required")
        exam = await session.get(LocalExam, exam_id)
        if not exam: raise HTTPException(404, "Exam not found")
        sections = exam.content.get("sections", [])
        if data.section_index >= len(sections): raise HTTPException(400, "Invalid section index")
        questions = sections[data.section_index].get("questions", [])
        if data.question_index >= len(questions): raise HTTPException(400, "Invalid question index")
        q = questions[data.question_index]
        wrapper = q.get("test_wrapper"); test_cases = q.get("test_cases", [])
        if data.run_tests:
            return {"test_results": await run_test_cases(data.language, data.code, test_cases, wrapper=wrapper)}
        nl = chr(10)
        code_to_run = data.code + (nl+nl + wrapper if wrapper else "")
        res = await execute_code(data.language, code_to_run, data.stdin)
        ro = res.get("run", {})
        return {"output": ro.get("stdout"), "stderr": ro.get("stderr"), "exit_code": ro.get("code")}

@router.post("/submit-answer")
async def submit_answer(data: SubmitAnswerSchema, user: LocalUser = Depends(get_current_user)):
    async with async_session() as session:
        r = await session.execute(select(LocalAttempt).where(
            LocalAttempt.exam_id == data.exam_id, LocalAttempt.student_id == str(user.id),
            LocalAttempt.status == "in_progress"))
        a = r.scalar_one_or_none()
        if not a: raise HTTPException(404, "No active attempt")
        d = a.data or {"sections": [], "answers": {}}
        d.setdefault("answers", {})[str(data.section_index)+"-"+str(data.question_index)] = (
            data.selected_option if data.selected_option is not None else data.code_submission)
        a.data = d; await session.commit()
    return {"message": "Answer saved"}

@router.post("/submit-section")
async def submit_section(data: SubmitSectionSchema, user: LocalUser = Depends(get_current_user)):
    async with async_session() as session:
        r = await session.execute(select(LocalAttempt).where(
            LocalAttempt.exam_id == data.exam_id, LocalAttempt.student_id == str(user.id),
            LocalAttempt.status == "in_progress"))
        a = r.scalar_one_or_none()
        if not a: raise HTTPException(404, "No active attempt")
        d = a.data or {"sections": [], "answers": {}}
        secs = d.get("sections", [])
        while len(secs) <= data.section_index: secs.append({"status": "not_started"})
        secs[data.section_index] = {"status": "submitted", "submitted_at": datetime.utcnow().isoformat()}
        d["sections"] = secs; a.data = d; await session.commit()
    return {"message": "Section submitted", "section_score": 0}

@router.post("/submit")
async def submit_exam(data: SubmitExamSchema, user: LocalUser = Depends(get_current_user)):
    async with async_session() as session:
        a = await session.get(LocalAttempt, data.attempt_id)
        if not a or a.student_id != str(user.id): raise HTTPException(404, "Attempt not found")
        a.status = "submitted"; a.submitted_at = datetime.utcnow()
        await session.commit(); await session.refresh(a)
    return {"id": a.id, "status": a.status, "total_score": a.total_score, "max_score": a.max_score,
            "exam_id": a.exam_id, "student_id": a.student_id, "violation_count": a.violation_count,
            "sections": (a.data or {}).get("sections", [])}

@router.get("/results/{attempt_id}")
async def get_results(attempt_id: str, user: LocalUser = Depends(get_current_user)):
    async with async_session() as session:
        a = await session.get(LocalAttempt, attempt_id)
        if not a or (a.student_id != str(user.id) and user.role not in ("faculty", "admin")):
            raise HTTPException(404, "Result not found")
        exam = await session.get(LocalExam, a.exam_id)
    return {"id": a.id, "exam_id": a.exam_id, "exam_title": exam.title if exam else "Unknown",
            "student_id": a.student_id, "status": a.status, "total_score": a.total_score,
            "max_score": a.max_score, "violation_count": a.violation_count,
            "sections": (a.data or {}).get("sections", []),
            "started_at": a.started_at, "submitted_at": a.submitted_at}