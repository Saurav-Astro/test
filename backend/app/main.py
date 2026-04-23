from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.core.sqlite import init_sqlite
from app.api import auth, exams, attempts, proctor, code, admin

app = FastAPI(
    title="ProXM API",
    description="AI-Proctored Online Examination Platform",
    version="1.0.0",
)

# Permissive CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await init_sqlite()
    await init_db()

@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}

# Explicitly use the prefix to be 100% sure
app.include_router(auth.router, prefix="/api/v1")
app.include_router(exams.router, prefix="/api/v1")
app.include_router(attempts.router, prefix="/api/v1")
app.include_router(proctor.router, prefix="/api/v1")
app.include_router(code.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

