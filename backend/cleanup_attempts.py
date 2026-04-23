import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.attempt import Attempt
from app.core.config import settings
import beanie

async def cleanup():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    await beanie.init_beanie(database=client[settings.DB_NAME], document_models=[Attempt])
    # Delete all attempts to start fresh for demo
    await Attempt.find_all().delete()
    print("All attempts deleted.")

if __name__ == "__main__":
    asyncio.run(cleanup())
