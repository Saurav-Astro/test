import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.attempt import Attempt
from app.core.config import settings
import beanie

async def check():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    await beanie.init_beanie(database=client[settings.DB_NAME], document_models=[Attempt])
    attempts = await Attempt.find_all().to_list()
    print(f"Total Attempts: {len(attempts)}")
    for a in attempts:
        print(f"ID: {a.id}, Status: {a.status}, Sections: {len(a.sections)}")

if __name__ == "__main__":
    asyncio.run(check())
