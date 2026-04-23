from beanie import Document, Indexed
from pydantic import EmailStr, Field
from datetime import datetime, timedelta
from typing import Annotated


class OTPRecord(Document):
    email: Annotated[EmailStr, Indexed()]
    otp: str
    expires_at: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(minutes=10)
    )
    used: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "otp_records"

    def is_valid(self) -> bool:
        return not self.used and datetime.utcnow() < self.expires_at
