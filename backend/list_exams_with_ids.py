import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.exam import Exam
from app.core.config import settings
import beanie

async def list_exams():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    await beanie.init_beanie(database=client[settings.DB_NAME], document_models=[Exam])
    exams = await Exam.find_all().to_list()
    for e in exams:
        print(f"ID: {e.id} | Title: {e.title}")

if __name__ == "__main__":
    asyncio.run(list_exams())
