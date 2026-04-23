import asyncio
import httpx

async def main():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000/api/v1") as client:
        # Login
        res = await client.post("/auth/login", json={"email": "testfac@test.com", "password": "password123"})
        token = res.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get available exams
        res = await client.get("/exams/available", headers=headers)
        exams = res.json()
        print("Available exams:", len(exams))
        
        # Start demo exam
        for exam in exams:
            print("Trying", exam["title"])
            res = await client.post("/attempts/start", json={"exam_id": exam["id"]}, headers=headers)
            print("Start Attempt:", res.status_code, res.text[:200])

asyncio.run(main())
