import asyncio
import httpx

async def main():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000/api/v1") as client:
        # Login student
        res = await client.post("/auth/login", json={"email": "teststu@test.com", "password": "password123"})
        token = res.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get exams
        exams = (await client.get("/exams/available", headers=headers)).json()
        exam_id = exams[-1]["id"]
        
        # Terminate attempt
        await client.post("/attempts/submit", json={"attempt_id": "dummy"}, headers=headers) # I don't know attempt id, I will just edit the db directly.

