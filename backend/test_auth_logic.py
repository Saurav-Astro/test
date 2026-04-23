import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import init_db
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = TestClient(app)

async def setup():
    await init_db()
    # Clean up test users if they exist
    db = AsyncIOMotorClient(settings.MONGODB_URI)[settings.DB_NAME]
    await db["users"].delete_many({"email": {"$regex": "test.*"}})
    await db["faculty_users"].delete_many({"email": {"$regex": "test.*"}})

def run_tests():
    # 1. Register student
    print("Testing Student Registration...")
    res = client.post("/api/v1/auth/register", json={
        "name": "Test Student",
        "email": "teststudent@example.com",
        "password": "password123",
        "role": "student"
    })
    assert res.status_code == 200, res.text
    student_token = res.json()["access_token"]
    print("✅ Student registered")

    # 2. Register faculty
    print("Testing Faculty Registration...")
    res = client.post("/api/v1/auth/register", json={
        "name": "Test Faculty",
        "email": "testfaculty@example.com",
        "password": "password123",
        "role": "faculty",
        "secret_key": settings.FACULTY_SECRET
    })
    assert res.status_code == 200, res.text
    faculty_token = res.json()["access_token"]
    print("✅ Faculty registered")

    # 3. Faculty creates an exam
    print("Testing Faculty Exam Creation...")
    res = client.post("/api/v1/exams/", headers={"Authorization": f"Bearer {faculty_token}"}, json={
        "title": "Test Exam",
        "sections": []
    })
    assert res.status_code == 200, res.text
    print("✅ Faculty can create exams")

    # 4. Student tries to create an exam
    print("Testing Student Exam Creation (Should Fail)...")
    res = client.post("/api/v1/exams/", headers={"Authorization": f"Bearer {student_token}"}, json={
        "title": "Hacked Exam",
        "sections": []
    })
    assert res.status_code == 403, res.text
    print("✅ Student correctly denied from creating exams")

    # 5. Login
    print("Testing Login...")
    res = client.post("/api/v1/auth/login", json={
        "email": "testfaculty@example.com",
        "password": "password123"
    })
    assert res.status_code == 200, res.text
    print("✅ Faculty can log in")

    res = client.post("/api/v1/auth/login", json={
        "email": "teststudent@example.com",
        "password": "password123"
    })
    assert res.status_code == 200, res.text
    print("✅ Student can log in")

    print("\n🎉 ALL TESTS PASSED!")

if __name__ == "__main__":
    asyncio.run(setup())
    run_tests()
