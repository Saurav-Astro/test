import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def clean():
    db = AsyncIOMotorClient(settings.MONGODB_URI)[settings.DB_NAME]
    await db["users"].delete_many({"email": {"$regex": "test.*"}})
    await db["faculty_users"].delete_many({"email": {"$regex": "test.*"}})
    print("Cleaned test users")

if __name__ == "__main__":
    asyncio.run(clean())
