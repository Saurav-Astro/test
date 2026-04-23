from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class MCQOption(BaseModel):
    text: str
    is_correct: bool = False


class TestCase(BaseModel):
    input: str
    expected_output: str
    is_hidden: bool = False


class Question(BaseModel):
    question_text: str
    question_type: Literal["mcq", "coding"] = "mcq"
    # MCQ fields
    options: List[dict] = []  # [{text, is_correct}]
    # Coding fields
    starter_code: Optional[str] = None
    test_wrapper: Optional[str] = None
    language: Optional[str] = "python"
    test_cases: List[dict] = []  # [{input, expected_output, is_hidden}]
    marks: int = 1
    time_limit_seconds: int = 60  # per-question timer


class ProctoringConfig(BaseModel):
    face_detection: bool = True
    multi_face_check: bool = True
    window_switch_ban: bool = True
    keyboard_restriction: bool = True
    max_warnings: int = 3
    auto_submit_on_max_warnings: bool = True
    fullscreen_required: bool = True


class Section(BaseModel):
    title: str
    description: Optional[str] = None
    time_limit_minutes: int = 30  # overall section time
    time_per_question_seconds: int = 60  # default per question
    questions: List[Question] = []
    proctoring: ProctoringConfig = Field(default_factory=ProctoringConfig)
    order: int = 0


class Exam(Document):
    title: str
    description: Optional[str] = None
    created_by: PydanticObjectId  # faculty user id
    sections: List[Section] = []
    is_published: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    allowed_students: List[PydanticObjectId] = []  # empty = all students
    # Entry protection
    entry_question: Optional[str] = None
    entry_password: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    shuffle_questions: bool = False
    shuffle_options: bool = False
    show_result_immediately: bool = False

    class Settings:
        name = "exams"
        indexes = [
            [("created_by", 1)],
            [("is_published", 1)],
        ]
