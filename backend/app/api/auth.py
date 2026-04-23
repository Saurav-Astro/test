from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, EmailStr
from datetime import datetime
from sqlalchemy import select
from app.core.security import (
    hash_password, verify_password, create_access_token, get_current_user
)
from app.core.sqlite import async_session, LocalUser, LocalOTP
from app.services.email_service import generate_otp, send_otp_email
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "student"
    secret_key: str = ""

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordSchema(BaseModel):
    email: EmailStr

class VerifyOTPSchema(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

@router.post("/register")
async def register(data: RegisterSchema):
    email = data.email.lower()
    async with async_session() as session:
        stmt = select(LocalUser).where(LocalUser.email == email)
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")

        if data.role in ("faculty", "admin"):
            if data.secret_key != settings.FACULTY_SECRET:
                raise HTTPException(status_code=403, detail="Invalid faculty secret key")
            role = data.role
        else:
            role = "student"
        
        user = LocalUser(
            email=email,
            name=data.name,
            password_hash=hash_password(data.password),
            role=role
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        token = create_access_token({"sub": str(user.id), "role": user.role})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": str(user.id), "name": user.name, "email": user.email, "role": user.role},
        }

@router.post("/login")
async def login(data: LoginSchema):
    email = data.email.lower()
    async with async_session() as session:
        stmt = select(LocalUser).where(LocalUser.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": str(user.id), "name": user.name, "email": user.email, "role": user.role},
    }

@router.get("/me")
async def me(user: LocalUser = Depends(get_current_user)):
    return {"id": str(user.id), "name": user.name, "email": user.email, "role": user.role}
