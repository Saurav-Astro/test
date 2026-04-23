from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.user import User
from app.models.faculty_user import FacultyUser
from app.models.exam import Exam
from app.models.attempt import Attempt
from app.models.proctoring_log import ProctoringLog
from app.models.otp import OTPRecord
import json

async def init_db():
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        await init_beanie(
            database=client[settings.DB_NAME],
            document_models=[User, FacultyUser, Exam, Attempt, ProctoringLog, OTPRecord],
        )
        print(f"[OK] Connected to MongoDB: {settings.DB_NAME}")
        
        # Sync to SQLite for speed
        from app.core.sqlite import async_session, LocalExam
        from sqlalchemy import select
        async with async_session() as session:
            exams = await Exam.find_all().to_list()
            for e in exams:
                local_e = await session.get(LocalExam, str(e.id))
                # Use JSON string for model_dump to handle datetimes
                exam_dict = json.loads(e.model_dump_json())
                
                if not local_e:
                    local_e = LocalExam(
                        id=str(e.id),
                        title=e.title,
                        description=e.description,
                        content=exam_dict,
                        is_published=e.is_published
                    )
                    session.add(local_e)
                else:
                    local_e.title = e.title
                    local_e.description = e.description
                    local_e.content = exam_dict
                    local_e.is_published = e.is_published
            await session.commit()
            print("[OK] Synced Exams to Local SQLite")
            
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise e
