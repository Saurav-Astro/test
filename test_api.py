import asyncio
import httpx

async def main():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000/api/v1") as client:
        # Register a faculty to create an exam
        res = await client.post("/auth/register", json={"name": "Test Faculty", "email": "testfac@test.com", "password": "password123", "role": "faculty", "secret_key": "PROXM_FACULTY_2026"})
        print("Register:", res.status_code)
        
        # Login
        res = await client.post("/auth/login", json={"email": "testfac@test.com", "password": "password123"})
        token = res.json().get("access_token")
        print("Login:", res.status_code, "Token:", token[:10] if token else None)
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create an exam
        exam_data = {
            "title": "Test Exam",
            "is_published": True,
            "sections": [{"title": "Sec 1", "questions": [{"question_text": "Q1"}]}]
        }
        res = await client.post("/exams/", json=exam_data, headers=headers)
        print("Create Exam:", res.status_code)
        exam_id = res.json().get("id")
        print("Exam ID:", exam_id)
        
        # Start attempt
        res = await client.post("/attempts/start", json={"exam_id": exam_id}, headers=headers)
        print("Start Attempt:", res.status_code)
        print("Response:", res.text)
        
        # Get for student
        res = await client.get(f"/exams/{exam_id}/student", headers=headers)
        print("Get for Student:", res.status_code)
        print("Response:", res.text)

asyncio.run(main())
