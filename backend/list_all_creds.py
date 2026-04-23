import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def list_creds():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DB_NAME]
    
    print("--- Students (User Collection) ---")
    students = await db["users"].find().to_list(10)
    for s in students:
        print(f"Email: {s['email']} | Role: {s['role']}")
        
    print("\n--- Faculty (FacultyUser Collection) ---")
    faculty = await db["faculty_users"].find().to_list(10)
    for f in faculty:
        print(f"Email: {f['email']} | Role: {f['role']}")

if __name__ == "__main__":
    asyncio.run(list_creds())
