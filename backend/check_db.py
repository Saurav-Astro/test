import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def check_db():
    try:
        print(f"Attempting to connect to MongoDB URI: {settings.MONGODB_URI}")
        client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
        # Attempt to fetch server info to test connection
        info = await client.server_info()
        print("Successfully connected to the database!")
        print(f"MongoDB Version: {info.get('version')}")
    except Exception as e:
        print(f"Failed to connect to the database. Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_db())
