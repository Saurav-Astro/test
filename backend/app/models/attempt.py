from beanie import Document, PydanticObjectId
from pydantic import Field, BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class QuestionAnswer(BaseModel):
    question_index: int
    selected_option: Optional[int] = None  # index of chosen MCQ option
    code_submission: Optional[str] = None
    test_results: List[Dict[str, Any]] = []
    is_correct: Optional[bool] = None
    time_spent_seconds: int = 0
    marks_awarded: float = 0


class SectionAttempt(BaseModel):
    section_index: int
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    answers: List[QuestionAnswer] = []
    status: str = "not_started"  # not_started | in_progress | submitted | timed_out


class Attempt(Document):
    exam_id: PydanticObjectId
    student_id: PydanticObjectId
    sections: List[SectionAttempt] = []
    status: str = "not_started"  # not_started | in_progress | submitted | terminated
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    terminated_reason: Optional[str] = None
    total_score: float = 0
    max_score: float = 0
    violation_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "attempts"
        indexes = [
            [("exam_id", 1), ("student_id", 1)],
        ]
