import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def check_collections():
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
        db = client[settings.DB_NAME]
        collections = await db.list_collection_names()
        
        print(f"Total number of collections (tables): {len(collections)}")
        if collections:
            print("Collections present:")
            for coll in collections:
                # Count documents in each collection
                count = await db[coll].count_documents({})
                print(f" - {coll} (Documents: {count})")
        else:
            print("No collections found in the database.")
            
    except Exception as e:
        print(f"Failed to fetch collections. Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_collections())
