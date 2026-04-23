from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import Optional, Literal
from datetime import datetime


class ProctoringLog(Document):
    attempt_id: PydanticObjectId
    student_id: PydanticObjectId
    exam_id: PydanticObjectId
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
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "proctoring_logs"
        indexes = [
            [("attempt_id", 1)],
            [("student_id", 1)],
            [("exam_id", 1)],
            [("timestamp", -1)],
        ]
