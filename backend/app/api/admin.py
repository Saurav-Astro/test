from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from datetime import datetime
from sqlalchemy import select
import uuid
from app.core.security import require_admin, require_faculty, hash_password
from app.core.sqlite import async_session, LocalUser

router = APIRouter(prefix="/admin", tags=["Admin"])

class CreateUserSchema(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "student"

class ResetPasswordSchema(BaseModel):
    user_id: str
    new_password: str

@router.get("/users")
async def list_users(admin: LocalUser = Depends(require_faculty)):
    async with async_session() as session:
        r = await session.execute(select(LocalUser))
        users = r.scalars().all()
    return [{"id": u.id, "name": u.name, "email": u.email, "role": u.role,
             "is_active": u.is_active, "created_at": u.created_at} for u in users]

@router.post("/users")
async def create_user(data: CreateUserSchema, admin: LocalUser = Depends(require_admin)):
    async with async_session() as session:
        email = data.email.lower()
        r = await session.execute(select(LocalUser).where(LocalUser.email == email))
        if r.scalar_one_or_none():
            raise HTTPException(400, "Email already exists")
        role = data.role if data.role in ("student", "faculty", "admin") else "student"
        u = LocalUser(id=str(uuid.uuid4()), email=email, name=data.name,
                      password_hash=hash_password(data.password), role=role)
        session.add(u)
        await session.commit()
        await session.refresh(u)
    return {"id": u.id, "name": u.name, "email": u.email, "role": u.role}

@router.patch("/users/{user_id}/toggle-active")
async def toggle_active(user_id: str, admin: LocalUser = Depends(require_admin)):
    async with async_session() as session:
        u = await session.get(LocalUser, user_id)
        if not u:
            raise HTTPException(404, "User not found")
        u.is_active = not u.is_active
        u.updated_at = datetime.utcnow()
        await session.commit()
    return {"is_active": u.is_active}

@router.patch("/users/reset-password")
async def admin_reset_password(data: ResetPasswordSchema, admin: LocalUser = Depends(require_admin)):
    async with async_session() as session:
        u = await session.get(LocalUser, data.user_id)
        if not u:
            raise HTTPException(404, "User not found")
        u.password_hash = hash_password(data.new_password)
        u.updated_at = datetime.utcnow()
        await session.commit()
    return {"message": "Password reset successfully"}

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, admin: LocalUser = Depends(require_admin)):
    async with async_session() as session:
        u = await session.get(LocalUser, user_id)
        if not u:
            raise HTTPException(404, "User not found")
        await session.delete(u)
        await session.commit()
    return {"message": "User deleted"}