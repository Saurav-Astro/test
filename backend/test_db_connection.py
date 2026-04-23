import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Add the backend directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

async def test_connection():
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DB_NAME", "proxm")
    
    if not uri:
        print("❌ MONGODB_URI not found in .env file.")
        return

    print(f"🔍 Testing connection to: {uri.split('@')[-1]}") # Print only the host part for safety
    
    try:
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        # The ismaster command is cheap and does not require auth.
        await client.admin.command('ismaster')
        print("✅ Success! The system can connect to your MongoDB server.")
        
        db = client[db_name]
        print(f"📁 Database '{db_name}' is accessible.")
        
    except Exception as e:
        print("\n❌ CONNECTION FAILED")
        print(f"Error: {e}")
        
        if "SSL handshake failed" in str(e) or "timeout" in str(e).lower():
            print("\n💡 POSSIBLE CAUSE: Your IP address might be blocked by MongoDB Atlas.")
            print("To fix this for ALL devices:")
            print("1. Go to MongoDB Atlas -> Network Access")
            print("2. Click 'Add IP Address'")
            print("3. Enter '0.0.0.0/0' (Allow Access From Anywhere)")
            print("4. Click 'Confirm'")
        else:
            print("\n💡 Check your MONGODB_URI in the .env file for errors.")

if __name__ == "__main__":
    asyncio.run(test_connection())
