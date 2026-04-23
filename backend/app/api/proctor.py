from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime
import uuid
from app.core.security import get_current_user
from app.core.sqlite import async_session, LocalProctoringLog, LocalUser

router = APIRouter(prefix="/proctor", tags=["Proctoring"])

class LogEventSchema(BaseModel):
    attempt_id: str
    event_type: str
    detail: Optional[str] = None
    severity: str = "info"

@router.post("/log")
async def log_event(data: LogEventSchema, user: LocalUser = Depends(get_current_user)):
    async with async_session() as session:
        log = LocalProctoringLog(
            id=str(uuid.uuid4()),
            attempt_id=data.attempt_id,
            student_id=str(user.id),
            event_type=data.event_type,
            detail=data.detail,
            severity=data.severity
        )
        session.add(log)
        await session.commit()
        return {"message": "Event logged"}
