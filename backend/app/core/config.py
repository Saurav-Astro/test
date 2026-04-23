from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    MONGODB_URI: str
    DB_NAME: str = "proxm"
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480
    APP_NAME: str = "ProXM"
    FRONTEND_URL: str = "http://localhost:5173"
    FACULTY_SECRET: str = "PROXM_FACULTY_2026"  # Default for development

    # Email settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "ProXM <noreply@proxm.io>"

    # Piston API
    PISTON_API_URL: str = "https://emkc.org/api/v2/piston"

    ENV: str = "development"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
