import asyncio
import httpx

async def main():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000/api/v1") as client:
        # Login
        res = await client.post("/auth/login", json={"email": "teststu@test.com", "password": "password123"})
        token = res.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Undefined
        res = await client.get("/exams/undefined/student", headers=headers)
        print("GetForStudent undefined:", res.status_code, res.text)
        
        res = await client.post("/attempts/start", json={"exam_id": "undefined"}, headers=headers)
        print("Start Attempt undefined:", res.status_code, res.text)

asyncio.run(main())
