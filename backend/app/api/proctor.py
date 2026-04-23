from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
import logging
import hashlib
from sqlalchemy import select

from app.core.security import get_current_user
from app.core.sqlite import async_session, LocalProctoringLog, LocalUser, LocalAttempt

router = APIRouter(prefix="/proctor", tags=["Proctoring"])

logger = logging.getLogger("proctoring_system")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

SECRET_KEY = "proxm_secure_exam_secret_2026"
rate_limit_cache = {}

class LogEventSchema(BaseModel):
    attempt_id: str
    event_type: str
    section_index: Optional[int] = None
    question_index: Optional[int] = None
    detail: Optional[str] = None
    severity: str = "info"
    timestamp: str  
    signature: str  

class TerminateSchema(BaseModel):
    attempt_id: str
    reason: str

VIOLATION_WEIGHTS = {
    "window_switch": 30,
    "copy_attempt": 20,
    "cut_attempt": 20,
    "paste_attempt": 20,
    "screenshot_attempt": 50,
    "devtools_attempt": 40,
    "camera_off": 40,
    "face_not_detected": 10,
    "multiple_faces": 50,
    "fullscreen_exit": 15,
    "keyboard_shortcut": 10
}
TERMINATION_THRESHOLD = 100

@router.post("/log")
async def log_event(data: LogEventSchema, user: LocalUser = Depends(get_current_user)):
    now = datetime.utcnow()
    now_iso = now.isoformat()
    
    last_event_time = rate_limit_cache.get(data.attempt_id)
    if last_event_time and (now - last_event_time).total_seconds() < 0.5:
        return {"message": "Rate limited", "status": "ignored"}
    rate_limit_cache[data.attempt_id] = now

    expected_hash = hashlib.sha256(f"{data.event_type}{data.timestamp}{SECRET_KEY}".encode()).hexdigest()
    trust_score = 100
    
    if expected_hash != data.signature:
        logger.warning(f"[{now_iso}] - [{user.id}] - [SPOOFING_ATTEMPT] - [CRITICAL] - [TRUST: 0]")
        data.event_type = "spoofed_event_attempt"
        data.severity = "critical"
        data.detail = "Invalid event signature detected"
        trust_score = 0

    log_msg = f"[{now_iso}] - [{user.id}] - [{data.event_type.upper()}] - [{data.severity.upper()}] - [TRUST: {trust_score}]"
    logger.info(log_msg)

    async with async_session() as session:
        result = await session.execute(select(LocalAttempt).where(LocalAttempt.id == data.attempt_id, LocalAttempt.student_id == str(user.id)))
        attempt = result.scalar_one_or_none()

        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found")
            
        if attempt.status != "in_progress":
            return {"message": "Exam already ended", "violation_score": attempt.violation_count, "terminated": attempt.status == "terminated"}

        log_id = str(uuid.uuid4())
        log = LocalProctoringLog(
            id=log_id,
            attempt_id=data.attempt_id,
            student_id=str(user.id),
            exam_id=attempt.exam_id,
            event_type=data.event_type,
            section_index=data.section_index,
            question_index=data.question_index,
            detail=data.detail,
            severity=data.severity
        )
        session.add(log)

        is_terminated = False
        if data.severity in ["warning", "critical"]:
            penalty = VIOLATION_WEIGHTS.get(data.event_type, 10)
            if trust_score == 0:
                penalty = 100 
                
            attempt.violation_count += penalty
            
            if attempt.violation_count >= TERMINATION_THRESHOLD:
                attempt.status = "terminated"
                attempt.terminated_reason = f"Auto-terminated: Score {attempt.violation_count} exceeded threshold {TERMINATION_THRESHOLD}."
                attempt.submitted_at = datetime.utcnow()
                is_terminated = True
                logger.info(f"[{now_iso}] - [{user.id}] - [EXAM_TERMINATED] - [CRITICAL] - [TRUST: {trust_score}]")

        await session.commit()
        return {
            "message": "Event logged",
            "violation_score": attempt.violation_count,
            "terminated": is_terminated,
            "threshold": TERMINATION_THRESHOLD
        }

@router.get("/status/{attempt_id}")
async def check_status(attempt_id: str, user: LocalUser = Depends(get_current_user)):
    async with async_session() as session:
        result = await session.execute(select(LocalAttempt).where(LocalAttempt.id == attempt_id, LocalAttempt.student_id == str(user.id)))
        attempt = result.scalar_one_or_none()

        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found")
        
        return {
            "status": attempt.status,
            "terminated": attempt.status == "terminated",
            "violation_score": attempt.violation_count
        }

@router.post("/terminate")
async def terminate_exam(data: TerminateSchema, user: LocalUser = Depends(get_current_user)):
    now_iso = datetime.utcnow().isoformat()
    logger.info(f"[{now_iso}] - [{user.id}] - [MANUAL_TERMINATE] - [CRITICAL] - [TRUST: N/A]")

    async with async_session() as session:
        result = await session.execute(select(LocalAttempt).where(LocalAttempt.id == data.attempt_id))
        attempt = result.scalar_one_or_none()

        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found")
        
        if attempt.status == "in_progress":
            attempt.status = "terminated"
            attempt.terminated_reason = data.reason
            attempt.submitted_at = datetime.utcnow()
            
            term_log = LocalProctoringLog(
                id=str(uuid.uuid4()),
                attempt_id=data.attempt_id,
                student_id=str(attempt.student_id),
                exam_id=attempt.exam_id,
                event_type="exam_terminated",
                detail=data.reason,
                severity="critical"
            )
            session.add(term_log)
            await session.commit()

        return {"message": "Exam terminated successfully"}

@router.get("/logs/{attempt_id}")
async def get_logs(attempt_id: str, user: LocalUser = Depends(get_current_user)):
    async with async_session() as session:
        result = await session.execute(
            select(LocalProctoringLog)
            .where(LocalProctoringLog.attempt_id == attempt_id)
            .order_by(LocalProctoringLog.timestamp.desc())
        )
        logs = result.scalars().all()
        return [
            {
                "id": l.id,
                "event_type": l.event_type,
                "detail": l.detail,
                "severity": l.severity,
                "timestamp": l.timestamp.isoformat()
            } for l in logs
        ]

@router.get("/summary/{exam_id}")
async def get_summary(exam_id: str, user: LocalUser = Depends(get_current_user)):
    async with async_session() as session:
        result = await session.execute(select(LocalAttempt).where(LocalAttempt.exam_id == exam_id))
        attempts = result.scalars().all()
        
        return [
            {
                "attempt_id": att.id,
                "student_id": att.student_id,
                "violation_count": att.violation_count,
                "status": att.status
            } for att in attempts
        ]
