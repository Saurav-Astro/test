import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, Document, PydanticObjectId
from pydantic import Field
from typing import List, Optional, Literal
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DB_NAME', 'proxm')

class MCQOption(Document):
    text: str
    is_correct: bool = False

class Question(BaseModel):
    question_text: str
    question_type: Literal['mcq', 'coding'] = 'mcq'
    options: List[dict] = []
    starter_code: Optional[str] = None
    language: Optional[str] = 'python'
    test_cases: List[dict] = []
    marks: int = 1
    time_limit_seconds: int = 60

class Section(BaseModel):
    title: str
    description: Optional[str] = None
    questions: List[Question] = []
    proctoring: dict = {}

class Exam(Document):
    title: str
    description: Optional[str] = None
    created_by: PydanticObjectId
    sections: List[Section] = []
    is_published: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FacultyUser(Document):
    email: str
    name: str
    role: str = 'faculty'

    class Settings:
        name = 'faculty_users'

async def create_demo():
    client = AsyncIOMotorClient(MONGODB_URI)
    await init_beanie(database=client[DB_NAME], document_models=[FacultyUser, Exam])

    faculty = await FacultyUser.find_one({'role': 'faculty'})
    if not faculty:
        print('No faculty user found. Please register a faculty user first.')
        return

    print(f'Found faculty: {faculty.name} ({faculty.id})')

    demo_exams = [
        {
            'title': 'General Science Demo',
            'description': 'A basic MCQ exam covering physics and chemistry.',
            'sections': [
                {
                    'title': 'Physics',
                    'questions': [
                        {'question_text': 'What is the SI unit of force?', 'options': [{'text': 'Newton', 'is_correct': True}, {'text': 'Joule', 'is_correct': False}, {'text': 'Watt', 'is_correct': False}, {'text': 'Volt', 'is_correct': False}], 'marks': 2},
                        {'question_text': 'Speed of light is approx 3x10^8 m/s.', 'options': [{'text': 'True', 'is_correct': True}, {'text': 'False', 'is_correct': False}], 'marks': 1}
                    ]
                }
            ]
        },
        {
            'title': 'Python Programming Demo',
            'description': 'Advanced coding exam with proctoring enabled.',
            'sections': [
                {
                    'title': 'Coding Section',
                    'questions': [
                        {
                            'question_text': 'Write a function add(a, b) that returns the sum of two numbers.',
                            'question_type': 'coding',
                            'starter_code': 'def solution(a, b):\n    # write code here\n    pass',
                            'language': 'python',
                            'test_cases': [{'input': '1 2', 'expected_output': '3'}, {'input': '10 20', 'expected_output': '30'}],
                            'marks': 10,
                            'time_limit_seconds': 300
                        }
                    ]
                }
            ]
        },
        {
            'title': 'Mathematics Final',
            'description': 'Comprehensive math exam for seniors.',
            'sections': [
                {
                    'title': 'Algebra',
                    'questions': [
                        {'question_text': 'Solve for x: 2x + 5 = 15', 'options': [{'text': '5', 'is_correct': True}, {'text': '10', 'is_correct': False}, {'text': '7', 'is_correct': False}, {'text': '0', 'is_correct': False}], 'marks': 5}
                    ]
                }
            ]
        }
    ]

    for data in demo_exams:
        exam = Exam(
            title=data['title'],
            description=data['description'],
            created_by=faculty.id,
            sections=data['sections'],
            is_published=True,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(days=7)
        )
        await exam.insert()
        print(f'Created exam: {exam.title}')

if __name__ == '__main__':
    asyncio.run(create_demo())


