import asyncio
import os
import sys
from datetime import datetime, timedelta
from beanie import init_beanie, PydanticObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.models.faculty_user import FacultyUser
from app.models.exam import Exam, Section, Question, ProctoringConfig

async def setup_demo():
    load_dotenv()
    
    print(f"Connecting to database: {settings.DB_NAME}...")
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    
    try:
        await init_beanie(
            database=client[settings.DB_NAME],
            document_models=[FacultyUser, Exam],
        )
        
        # 1. Find or create a faculty user
        faculty = await FacultyUser.find_one({"role": "faculty"})
        if not faculty:
            print("Creating a default faculty user...")
            faculty = FacultyUser(
                email="faculty@demo.com",
                name="Demo Faculty",
                password_hash="demo_hash", # Normally hashed
                role="faculty",
                is_active=True
            )
            await faculty.insert()
        
        print(f"Using faculty: {faculty.name} ({faculty.id})")

        # 2. Create a Demo Exam
        demo_exam_title = "ProXM Demo Exam"
        existing = await Exam.find_one({"title": demo_exam_title})
        if existing:
            print(f"Exam '{demo_exam_title}' already exists. Deleting to recreate...")
            await existing.delete()

        exam = Exam(
            title=demo_exam_title,
            description="This is a demo exam to showcase the platform's working capabilities, including proctoring and different question types.",
            created_by=faculty.id,
            is_published=True,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(days=30),
            sections=[
                Section(
                    title="Section 1: General Knowledge",
                    description="Multiple choice questions testing basics.",
                    questions=[
                        Question(
                            question_text="Which planet is known as the Red Planet?",
                            question_type="mcq",
                            options=[
                                {"text": "Venus", "is_correct": False},
                                {"text": "Mars", "is_correct": True},
                                {"text": "Jupiter", "is_correct": False},
                                {"text": "Saturn", "is_correct": False}
                            ],
                            marks=2
                        ),
                        Question(
                            question_text="What is the capital of France?",
                            question_type="mcq",
                            options=[
                                {"text": "London", "is_correct": False},
                                {"text": "Berlin", "is_correct": False},
                                {"text": "Paris", "is_correct": True},
                                {"text": "Madrid", "is_correct": False}
                            ],
                            marks=2
                        )
                    ],
                    proctoring=ProctoringConfig(
                        face_detection=True,
                        multi_face_check=True,
                        window_switch_ban=True,
                        keyboard_restriction=True,
                        max_warnings=3
                    )
                ),
                Section(
                    title="Section 2: Coding Challenge",
                    description="Practical coding tasks.",
                    questions=[
                        Question(
                            question_text="Write a Python function is_even(n) that returns True if n is even, False otherwise.",
                            question_type="coding",
                            starter_code="def is_even(n):\n    # Your code here\n    pass",
                            language="python",
                            test_cases=[
                                {"input": "2", "expected_output": "True"},
                                {"input": "7", "expected_output": "False"},
                                {"input": "0", "expected_output": "True"}
                            ],
                            marks=10,
                            time_limit_seconds=300
                        )
                    ]
                )
            ]
        )
        
        await exam.insert()
        print(f"Successfully created demo exam: {exam.title}")
        print(f"Exam ID: {exam.id}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    asyncio.run(setup_demo())
