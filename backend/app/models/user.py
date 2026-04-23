from beanie import Document, Indexed
from pydantic import EmailStr, Field
from typing import Optional, Literal, Annotated
from datetime import datetime


class User(Document):
    email: Annotated[EmailStr, Indexed(unique=True)]
    name: str
    password_hash: str
    role: Literal["student"] = "student"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        indexes = [
            [("email", 1)],
        ]
