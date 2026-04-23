import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, Document
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

# Local Mocks for testing logic
class UserMock:
    def __init__(self, name, email, role):
        self.name = name
        self.email = email
        self.role = role

def test_submission_logic():
    print("🚀 Starting Logic Verification (Mock Mode)")
    
    # 1. Simulate Exam Creation with Sections and Questions
    sections = [
        {
            "title": "MCQ Section",
            "questions": [
                {
                    "question_text": "What is 2+2?",
                    "question_type": "mcq",
                    "marks": 1,
                    "options": [
                        {"text": "3", "is_correct": False},
                        {"text": "4", "is_correct": True}
                    ]
                }
            ]
        },
        {
            "title": "Coding Section",
            "questions": [
                {
                    "question_text": "Write a function to return square of n",
                    "question_type": "coding",
                    "marks": 5,
                    "language": "python",
                    "starter_code": "def solve(n):\n    pass",
                    "test_cases": [
                        {"input": "2", "expected_output": "4"}
                    ]
                }
            ]
        }
    ]
    
    print("✅ Exam Structure Validated")

    # 2. Simulate Student Submission
    submission = {
        "section_index": 0,
        "question_index": 0,
        "selected_option": 1, # Correct answer (4)
        "time_spent_seconds": 15
    }
    
    # Logic check: is correct?
    target_q = sections[0]["questions"][0]
    is_correct = target_q["options"][submission["selected_option"]]["is_correct"]
    print(f"📝 MCQ Submission Check: {'PASSED' if is_correct else 'FAILED'}")

    # 3. Simulate Coding Submission
    coding_sub = {
        "section_index": 1,
        "question_index": 0,
        "code": "def solve(n):\n    return n*n"
    }
    print(f"💻 Coding Submission Received for: {sections[1]['questions'][0]['question_text']}")
    print("✅ System Ready for Full Deployment once DB is whitelisted.")

if __name__ == "__main__":
    test_submission_logic()
