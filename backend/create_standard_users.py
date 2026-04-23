import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.security import hash_password

async def create_users():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DB_NAME]
    
    users_to_create = [
        ("admin@proxm.io", "System Admin", "admin", "faculty_users"),
        ("faculty@proxm.io", "Exam Faculty", "faculty", "faculty_users"),
        ("student@proxm.io", "Test Student", "student", "users")
    ]
    
    password_hash = hash_password("password123")
    
    for email, name, role, collection in users_to_create:
        # Check if exists
        exists = await db[collection].find_one({"email": email})
        if not exists:
            await db[collection].insert_one({
                "email": email,
                "name": name,
                "password_hash": password_hash,
                "role": role,
                "is_active": True
            })
            print(f"✅ Created {role}: {email}")
        else:
            print(f"ℹ️ {email} already exists")

if __name__ == "__main__":
    asyncio.run(create_users())
