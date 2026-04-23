import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.exam import Exam
from app.core.config import settings
import beanie

async def check():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    await beanie.init_beanie(database=client[settings.DB_NAME], document_models=[Exam])
    exam = await Exam.find_one(Exam.title == "Demo Exam 1: Python Fundamentals")
    if exam:
        print(f"Exam: {exam.title}")
        print(f"Sections: {len(exam.sections)}")
        for i, s in enumerate(exam.sections):
            print(f"  {i}: {s.title} ({len(s.questions)} questions)")
    else:
        print("Exam not found")

if __name__ == "__main__":
    asyncio.run(check())
