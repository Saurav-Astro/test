from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    MONGODB_URI: Optional[str] = None
    DB_NAME: str = 'proxm'
    JWT_SECRET: str = 'CHANGE_ME_IN_PROD'
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRE_MINUTES: int = 480
    FACULTY_SECRET: str = 'PROXM_FACULTY_2026'
    APP_NAME: str = 'ProXM'
    FRONTEND_URL: str = 'http://localhost'
    ENV: str = 'development'
    SMTP_HOST: str = 'smtp.gmail.com'
    SMTP_PORT: int = 587
    SMTP_USER: str = ''
    SMTP_PASSWORD: str = ''
    EMAIL_FROM: str = 'noreply@proxm.io'
    PISTON_API_URL: str = 'https://emkc.org/api/v2/piston'
    LOCAL_EXEC_TIMEOUT: int = 5

    class Config:
        env_file = '.env'
        extra = 'ignore'

settings = Settings()
