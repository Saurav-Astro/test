import asyncio
import os
import sys
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.models.user import User

async def view_users():
    load_dotenv()
    
    print(f"🔍 Connecting to database: {settings.DB_NAME}...")
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    
    try:
        await init_beanie(
            database=client[settings.DB_NAME],
            document_models=[User],
        )
        
        users = await User.find_all().to_list()
        
        if not users:
            print("📭 No users found in the database.")
            return

        print(f"✅ Found {len(users)} user(s):\n")
        print(f"{'ID':<30} | {'Name':<20} | {'Email':<30} | {'Role':<10}")
        print("-" * 95)
        
        for u in users:
            print(f"{str(u.id):<30} | {u.name:<20} | {u.email:<30} | {u.role:<10}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(view_users())
