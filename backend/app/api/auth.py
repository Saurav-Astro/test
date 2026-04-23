from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.core.security import (
    hash_password, verify_password, create_access_token, get_current_user
)
from app.models.user import User
from app.models.faculty_user import FacultyUser
from typing import Union
from app.models.otp import OTPRecord
from app.services.email_service import generate_otp, send_otp_email
from fastapi import Depends
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "student"
    secret_key: str = ""  # required if role == faculty/admin


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class VerifyOTPSchema(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/register")
async def register(data: RegisterSchema):
    email = data.email.lower()
    # Check if email exists in either table
    if await User.find_one({"email": email}) or await FacultyUser.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    if data.role in ("faculty", "admin"):
        if data.secret_key != settings.FACULTY_SECRET:
            raise HTTPException(status_code=403, detail="Invalid faculty secret key")
        
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
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": str(user.id), "name": user.name, "email": user.email, "role": user.role},
    }


@router.post("/login")
async def login(data: LoginSchema):
    email = data.email.lower()
    user = await User.find_one(User.email == email)
    if not user:
        user = await FacultyUser.find_one(FacultyUser.email == email)

        

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


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordSchema, background: BackgroundTasks):
    email = data.email.lower()
    user = await User.find_one(User.email == email)
    if not user:
        user = await FacultyUser.find_one(FacultyUser.email == email)

    if not user:
        # Don't reveal if email exists
        return {"message": "If that email is registered, an OTP has been sent."}

    otp_code = generate_otp()
    record = OTPRecord(email=data.email, otp=otp_code)
    await record.insert()

    background.add_task(send_otp_email, data.email, otp_code, user.name)
    return {"message": "If that email is registered, an OTP has been sent."}


@router.post("/verify-otp-reset")
async def verify_otp_reset(data: VerifyOTPSchema):
    email = data.email.lower()
    record = await OTPRecord.find_one(
        OTPRecord.email == email,
        OTPRecord.otp == data.otp,
        OTPRecord.used == False,
    )
    if not record or not record.is_valid():
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user = await User.find_one(User.email == email)
    if not user:
        user = await FacultyUser.find_one(FacultyUser.email == email)


    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(data.new_password)
    user.updated_at = datetime.utcnow()
    await user.save()

    record.used = True
    await record.save()

    return {"message": "Password reset successfully"}


@router.get("/me")
async def me(user: Union[User, FacultyUser] = Depends(get_current_user)):
    return {"id": str(user.id), "name": user.name, "email": user.email, "role": user.role}


@router.patch("/me/password")
async def change_password(
    body: dict,
    user: Union[User, FacultyUser] = Depends(get_current_user),
):
    old_pw = body.get("old_password", "")
    new_pw = body.get("new_password", "")
    if not verify_password(old_pw, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.password_hash = hash_password(new_pw)
    user.updated_at = datetime.utcnow()
    await user.save()
    return {"message": "Password changed successfully"}
