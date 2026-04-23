from beanie import Document, Indexed
from pydantic import EmailStr, Field
from typing import Literal, Annotated
from datetime import datetime


class FacultyUser(Document):
    email: Annotated[EmailStr, Indexed(unique=True)]
    name: str
    password_hash: str
    role: Literal["admin", "faculty"] = "faculty"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "faculty_users"
        indexes = [
            [("email", 1)],
        ]
