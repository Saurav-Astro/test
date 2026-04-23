from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.core.security import require_admin, require_faculty, hash_password
from app.models.user import User
from app.models.faculty_user import FacultyUser

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
async def list_users(admin=Depends(require_faculty)):
    users = await User.find_all().to_list()
    faculty_users = await FacultyUser.find_all().to_list()
    
    all_users = []
    for u in users + faculty_users:
        all_users.append({
            "id": str(u.id), "name": u.name, "email": u.email,
            "role": u.role, "is_active": u.is_active, "created_at": u.created_at
        })
    return all_users


@router.post("/users")
async def create_user(data: CreateUserSchema, admin=Depends(require_admin)):
    email = data.email.lower()
    if await User.find_one(User.email == email) or await FacultyUser.find_one(FacultyUser.email == email):
        raise HTTPException(status_code=400, detail="Email already exists")
        
    if data.role in ("faculty", "admin"):
        user = FacultyUser(
            email=email,
            name=data.name,
            password_hash=hash_password(data.password),
            role=data.role,
        )
    else:
        user = User(
            email=email,
            name=data.name,
            password_hash=hash_password(data.password),
            role="student",
        )
    await user.insert()
    return {"id": str(user.id), "name": user.name, "email": user.email, "role": user.role}


@router.patch("/users/{user_id}/toggle-active")
async def toggle_active(user_id: str, admin=Depends(require_admin)):
    user = await User.get(user_id)
    if not user:
        user = await FacultyUser.get(user_id)
        
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not user.is_active
    user.updated_at = datetime.utcnow()
    await user.save()
    return {"is_active": user.is_active}


@router.patch("/users/reset-password")
async def admin_reset_password(data: ResetPasswordSchema, admin=Depends(require_admin)):
    user = await User.get(data.user_id)
    if not user:
        user = await FacultyUser.get(data.user_id)
        
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password_hash = hash_password(data.new_password)
    user.updated_at = datetime.utcnow()
    await user.save()
    return {"message": "Password reset successfully"}


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, admin=Depends(require_admin)):
    user = await User.get(user_id)
    if not user:
        user = await FacultyUser.get(user_id)
        
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await user.delete()
    return {"message": "User deleted"}
