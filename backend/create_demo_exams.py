import asyncio
import uuid
from datetime import datetime
from app.core.sqlite import async_session, LocalExam, init_sqlite

async def seed_exams():
    await init_sqlite()
    async with async_session() as session:
        exams = [
            {
                "title": "Coding Challenge: Sum of Two",
                "description": "LeetCode style coding challenge",
                "sections": [
                    {
                        "title": "Coding Section",
                        "questions": [
                            {
                                "question_text": "Write a function solution(a, b) that returns the sum of two numbers.",
                                "question_type": "coding",
                                "language": "python",
                                "starter_code": "def solution(a, b):\n    # Write your code here\n    pass",
                                "test_cases": [
                                    {"input": "1 2", "expected_output": "3", "is_hidden": False},
                                    {"input": "10 20", "expected_output": "30", "is_hidden": False}
                                ],
                                "test_wrapper": "import sys\n\nif __name__ == '__main__':\n    inputs = sys.stdin.read().split()\n    if len(inputs) >= 2:\n        a = int(inputs[0])\n        b = int(inputs[1])\n        print(solution(a, b))",
                                "marks": 10
                            }
                        ]
                    }
                ],
                "is_published": True
            }
        ]
        
        for e_data in exams:
            exam = LocalExam(
                id=str(uuid.uuid4()),
                title=e_data["title"],
                description=e_data["description"],
                content=e_data,
                is_published=True
            )
            session.add(exam)
        await session.commit()
        print("? Coding exams seeded")

if __name__ == "__main__":
    asyncio.run(seed_exams())
