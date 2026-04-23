import asyncio
import sys
import os

# Add the parent directory to sys.path to find 'app'
sys.path.append(os.path.join(os.getcwd(), "backend"))

from backend.app.core.database import init_db
from backend.app.models.user import User
from backend.app.core.security import hash_password

async def main():
    print("🚀 Initializing ProXM Database...")
    try:
        await init_db()
        
        # Check if admin exists, if not create a default one
        admin = await User.find_one(User.role == "admin")
        if not admin:
            print("👤 Creating default admin user...")
            admin = User(
                email="admin@proxm.io",
                name="Admin User",
                password_hash=hash_password("admin123"),
                role="admin"
            )
            await admin.insert()
            print("✅ Default admin created: admin@proxm.io / admin123")
        else:
            print("✅ Admin user already exists.")
            
        print("🎉 Database setup complete!")
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")

if __name__ == "__main__":
    asyncio.run(main())
