from fastapi import APIRouter, Depends, HTTPException
from beanie import PydanticObjectId
from typing import List, Optional, Union
from datetime import datetime
import json
import logging
import traceback

from app.models.attempt import Attempt, SectionAttempt, QuestionAnswer
from app.models.exam import Exam
from app.models.user import User
from app.core.security import get_current_user
from pydantic import BaseModel, Field
from app.services.code_service import execute_code, run_test_cases

router = APIRouter(prefix="/attempts", tags=["Attempts"])

class StartAttemptSchema(BaseModel):
    exam_id: str
    entry_password: Union[str, None] = None

class SubmitSectionSchema(BaseModel):
    exam_id: str
    section_index: int

class SubmitAnswerSchema(BaseModel):
    exam_id: str
    section_index: int
    question_index: int
    selected_option: Union[int, None] = None
    code_submission: Union[str, None] = None
    time_spent_seconds: int = 0

class SubmitExamSchema(BaseModel):
    attempt_id: str

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

def serialize_attempt(a: Attempt) -> dict:
    d = a.model_dump()
    d["id"] = str(a.id)
    d["exam_id"] = str(a.exam_id)
    d["student_id"] = str(a.student_id)
    return d

@router.post("/start")
async def start_attempt(data: StartAttemptSchema, user: User = Depends(get_current_user)):
    try:
        print(f"DEBUG: Starting attempt for exam {data.exam_id} and user {user.id}")
        exam = await Exam.get(data.exam_id)
        if not exam:
            print(f"DEBUG: Exam {data.exam_id} not found")
            raise HTTPException(status_code=404, detail="Exam not found")

        # Cleanup old attempts
        await Attempt.find(
            Attempt.exam_id == exam.id,
            Attempt.student_id == user.id
        ).delete()

        sections = [
            SectionAttempt(section_index=i, status="not_started", answers=[])
            for i in range(len(exam.sections))
        ]
        
        # Safe score calculation
        total_max_score = 0
        for s in exam.sections:
            for q in s.questions:
                total_max_score += getattr(q, 'marks', 0) or 0

        attempt = Attempt(
            exam_id=exam.id,
            student_id=user.id,
            sections=sections,
            status="in_progress",
            started_at=datetime.utcnow(),
            max_score=total_max_score,
        )
        await attempt.insert()
        print(f"DEBUG: Attempt started successfully: {attempt.id}")
        return serialize_attempt(attempt)
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG ERROR in start_attempt: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Backend Error: {str(e)}")

@router.post("/execute")
async def execute(data: RunCodeSchema, user: User = Depends(get_current_user)):
    attempt = None
    if data.attempt_id:
        attempt = await Attempt.get(data.attempt_id)
    
    if not attempt and data.exam_id:
        attempt = await Attempt.find_one(
            Attempt.exam_id == PydanticObjectId(data.exam_id),
            Attempt.student_id == user.id,
            Attempt.status == "in_progress"
        )
        
    if not attempt:
        raise HTTPException(status_code=404, detail="Active session not found. Please refresh.")

    exam = await Exam.get(str(attempt.exam_id))
    q = exam.sections[data.section_index].questions[data.question_index]
    
    if data.run_tests:
        results = await run_test_cases(data.language, data.code, q.test_cases, wrapper=getattr(q, 'test_wrapper', None))
        return {"test_results": results}
    else:
        code_to_run = data.code
        wrapper = getattr(q, 'test_wrapper', None)
        if wrapper:
            code_to_run = f"{data.code}\n\n{wrapper}"
        res = await execute_code(data.language, code_to_run, data.stdin)
        run_res = res.get("run", {})
        return {
            "output": run_res.get("stdout"),
            "stderr": run_res.get("stderr"),
            "exit_code": run_res.get("code"),
            "compile_output": res.get("compile", {}).get("output")
        }

@router.post("/submit-section")
async def submit_section(data: SubmitSectionSchema, user: User = Depends(get_current_user)):
    attempt = await Attempt.find_one(
        Attempt.exam_id == PydanticObjectId(data.exam_id),
        Attempt.student_id == user.id,
        Attempt.status == "in_progress",
    )
    if not attempt:
        raise HTTPException(status_code=404, detail="No active attempt found")

    if data.section_index >= len(attempt.sections):
        raise HTTPException(status_code=400, detail="Invalid section index")
        
    exam = await Exam.get(str(attempt.exam_id))
    section_data = exam.sections[data.section_index]
    sec = attempt.sections[data.section_index]
    sec.status = "submitted"
    sec.submitted_at = datetime.utcnow()

    sec_score = 0
    for ans in sec.answers:
        if ans.question_index < len(section_data.questions):
            q = section_data.questions[ans.question_index]
            if q.question_type == "mcq" and ans.selected_option is not None:
                is_correct = q.options[ans.selected_option].get("is_correct", False)
                ans.is_correct = is_correct
                if is_correct:
                    ans.marks_awarded = q.marks
                    sec_score += q.marks

    attempt.total_score += sec_score
    await attempt.save()
    return {"message": "Section submitted", "section_score": sec_score}

@router.post("/submit-answer")
async def submit_answer(data: SubmitAnswerSchema, user: User = Depends(get_current_user)):
    attempt = await Attempt.find_one(
        Attempt.exam_id == PydanticObjectId(data.exam_id),
        Attempt.student_id == user.id,
        Attempt.status == "in_progress",
    )
    if not attempt:
        raise HTTPException(status_code=404, detail="No active attempt found")

    sec = attempt.sections[data.section_index]
    ans = next((a for a in sec.answers if a.question_index == data.question_index), None)
    if not ans:
        ans = QuestionAnswer(question_index=data.question_index)
        sec.answers.append(ans)

    if data.selected_option is not None:
        ans.selected_option = data.selected_option
    if data.code_submission is not None:
        ans.code_submission = data.code_submission
    ans.time_spent_seconds += data.time_spent_seconds

    await attempt.save()
    return {"message": "Answer saved"}

@router.post("/submit")
async def submit_exam(data: SubmitExamSchema, user: User = Depends(get_current_user)):
    attempt = await Attempt.get(data.attempt_id)
    if not attempt or attempt.student_id != user.id:
        raise HTTPException(status_code=404, detail="Attempt not found")

    attempt.status = "submitted"
    attempt.submitted_at = datetime.utcnow()

    for s in attempt.sections:
        if s.status != "submitted":
            s.status = "submitted"
            s.submitted_at = datetime.utcnow()

    await attempt.save()
    return serialize_attempt(attempt)

@router.get("/results/{id}")
async def get_results(id: str, user: User = Depends(get_current_user)):
    try:
        attempt = await Attempt.get(id)
    except Exception:
        raise HTTPException(status_code=404, detail="Result not found")
        
    if not attempt or (attempt.student_id != user.id and user.role != "faculty"):
        raise HTTPException(status_code=404, detail="Result not found")

    exam = await Exam.get(str(attempt.exam_id))
    data = serialize_attempt(attempt)
    data["exam_title"] = exam.title if exam else "Unknown Exam"
    return data

@router.get("/exam/{exam_id}/all")
async def get_all_attempts(exam_id: str, user: User = Depends(get_current_user)):
    if user.role != "faculty":
        raise HTTPException(status_code=403, detail="Faculty only")
    attempts = await Attempt.find(Attempt.exam_id == PydanticObjectId(exam_id)).to_list()
    return [serialize_attempt(a) for a in attempts]
