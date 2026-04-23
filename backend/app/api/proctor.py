from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime
from app.core.security import get_current_user, require_faculty
from app.models.user import User
from app.models.attempt import Attempt
from app.models.proctoring_log import ProctoringLog
from app.models.exam import Exam

router = APIRouter(prefix="/proctor", tags=["Proctoring"])


class LogEventSchema(BaseModel):
    attempt_id: str
    event_type: Literal[
        "face_not_detected",
        "multiple_faces",
        "window_switch",
        "keyboard_shortcut",
        "fullscreen_exit",
        "exam_terminated",
        "warning_issued",
        "session_start",
        "session_end",
        "screenshot_captured",
    ]
    section_index: Optional[int] = None
    question_index: Optional[int] = None
    detail: Optional[str] = None
    severity: Literal["info", "warning", "critical"] = "info"


class TerminateSchema(BaseModel):
    attempt_id: str
    reason: str


@router.post("/log")
async def log_event(data: LogEventSchema, user: User = Depends(get_current_user)):
    attempt = await Attempt.get(data.attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if str(attempt.student_id) != str(user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    if attempt.status in ("submitted", "terminated"):
        return {"message": "Attempt already ended"}

    log = ProctoringLog(
        attempt_id=attempt.id,
        student_id=attempt.student_id,
        exam_id=attempt.exam_id,
        event_type=data.event_type,
        section_index=data.section_index,
        question_index=data.question_index,
        detail=data.detail,
        severity=data.severity,
    )
    await log.insert()

    # Increment violation count for warning/critical events
    if data.severity in ("warning", "critical"):
        attempt.violation_count += 1

        # Check auto-terminate (get exam config)
        exam = await Exam.get(str(attempt.exam_id))
        current_section_idx = data.section_index
        if current_section_idx is not None and exam.sections:
            proctoring_cfg = exam.sections[current_section_idx].proctoring
            if (
                proctoring_cfg.auto_submit_on_max_warnings
                and attempt.violation_count >= proctoring_cfg.max_warnings
            ):
                attempt.status = "terminated"
                attempt.terminated_reason = "Exceeded maximum violations"
                attempt.submitted_at = datetime.utcnow()

        await attempt.save()

    return {
        "message": "Event logged",
        "violation_count": attempt.violation_count,
        "terminated": attempt.status == "terminated",
    }


@router.post("/terminate")
async def terminate_attempt(data: TerminateSchema, faculty: User = Depends(require_faculty)):
    attempt = await Attempt.get(data.attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    attempt.status = "terminated"
    attempt.terminated_reason = data.reason
    attempt.submitted_at = datetime.utcnow()
    await attempt.save()
    return {"message": "Attempt terminated"}


@router.get("/logs/{attempt_id}")
async def get_logs(attempt_id: str, faculty: User = Depends(require_faculty)):
    logs = await ProctoringLog.find(
        ProctoringLog.attempt_id == attempt_id
    ).sort(-ProctoringLog.timestamp).to_list()
    return [
        {
            "id": str(l.id),
            "event_type": l.event_type,
            "section_index": l.section_index,
            "question_index": l.question_index,
            "detail": l.detail,
            "severity": l.severity,
            "timestamp": l.timestamp,
        }
        for l in logs
    ]


@router.get("/summary/{exam_id}")
async def proctor_summary(exam_id: str, faculty: User = Depends(require_faculty)):
    """Get violation summary for all students in an exam."""
    logs = await ProctoringLog.find(
        ProctoringLog.exam_id == exam_id
    ).to_list()
    summary = {}
    for l in logs:
        sid = str(l.student_id)
        if sid not in summary:
            summary[sid] = {
                "student_id": sid,
                "total_events": 0,
                "critical": 0,
                "warnings": 0,
                "face_events": 0,
                "window_switches": 0,
            }
        summary[sid]["total_events"] += 1
        if l.severity == "critical":
            summary[sid]["critical"] += 1
        elif l.severity == "warning":
            summary[sid]["warnings"] += 1
        if l.event_type in ("face_not_detected", "multiple_faces"):
            summary[sid]["face_events"] += 1
        if l.event_type == "window_switch":
            summary[sid]["window_switches"] += 1
    return list(summary.values())
