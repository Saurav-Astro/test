import asyncio
import uuid
from sqlalchemy import select
from app.core.sqlite import async_session, LocalUser, init_sqlite
from app.core.security import hash_password

async def create_users():
    await init_sqlite()
    async with async_session() as session:
        users_to_create = [
            ("admin@proxm.io", "System Admin", "admin"),
            ("faculty@proxm.io", "Exam Faculty", "faculty"),
            ("student@proxm.io", "Test Student", "student")
        ]
        
        password_hash = hash_password("password123")
        
        for email, name, role in users_to_create:
            stmt = select(LocalUser).where(LocalUser.email == email)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                user = LocalUser(
                    id=str(uuid.uuid4()),
                    email=email,
                    name=name,
                    password_hash=password_hash,
                    role=role,
                    is_active=True
                )
                session.add(user)
                print(f"? Created {role}: {email}")
            else:
                user.password_hash = password_hash
                print(f"?? Updated password for {email}")
        
        await session.commit()

if __name__ == "__main__":
    asyncio.run(create_users())
