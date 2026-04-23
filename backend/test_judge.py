import requests
import time

base_url = "http://localhost:8000/api/v1"
FACULTY_SECRET = "PROXM_FACULTY_2026"

def run_tests():
    print("--- Starting Judge Test Suite ---")
    
    # 1. Email Normalization Test
    print("1. Testing Email Normalization (Mixed Case Registration)...")
    res = requests.post(f"{base_url}/auth/register", json={
        "name": "Case User",
        "email": "CaseUser@Example.com",
        "password": "password123",
        "role": "student"
    })
    assert res.status_code == 200
    print("✅ Registered with mixed case email")

    print("2. Testing Login with Lowercase Email...")
    res = requests.post(f"{base_url}/auth/login", json={
        "email": "caseuser@example.com",
        "password": "password123"
    })
    assert res.status_code == 200
    print("✅ Logged in with lowercase email (Normalization Works)")

    print("3. Testing Duplicate Registration with Different Case...")
    res = requests.post(f"{base_url}/auth/register", json={
        "name": "Case User Duplicate",
        "email": "CASEUSER@EXAMPLE.COM",
        "password": "password123",
        "role": "student"
    })
    assert res.status_code == 400
    print("✅ Duplicate registration blocked correctly")

    # 4. Exam Time Window Test
    print("4. Testing Exam Time Windows...")
    # Register faculty
    res = requests.post(f"{base_url}/auth/register", json={
        "name": "Judge Faculty",
        "email": "judge_faculty@example.com",
        "password": "password123",
        "role": "faculty",
        "secret_key": FACULTY_SECRET
    })
    f_token = res.json()["access_token"]
    
    # Create an exam in the future
    future_time = "2099-01-01T00:00:00"
    res = requests.post(f"{base_url}/exams/", headers={"Authorization": f"Bearer {f_token}"}, json={
        "title": "Future Exam",
        "is_published": True,
        "start_time": future_time,
        "sections": []
    })
    exam_id = res.json()["id"]
    
    # Try to access as student
    student_res = requests.post(f"{base_url}/auth/register", json={
        "name": "Judge Student",
        "email": "judge_student@example.com",
        "password": "password123",
        "role": "student"
    })
    s_token = student_res.json()["access_token"]
    
    print("Checking if future exam is visible to student...")
    res = requests.get(f"{base_url}/exams/available", headers={"Authorization": f"Bearer {s_token}"})
    available = res.json()
    assert all(e["id"] != exam_id for e in available)
    print("✅ Future exam hidden from available list")

    print("Attempting to access future exam directly...")
    res = requests.get(f"{base_url}/exams/{exam_id}/student", headers={"Authorization": f"Bearer {s_token}"})
    assert res.status_code == 403
    assert "not started" in res.json()["detail"].lower()
    print("✅ Direct access to future exam blocked")

    print("\n⚖️ JUDGE'S VERDICT: ALL SECURITY FIXES VERIFIED!")

if __name__ == "__main__":
    time.sleep(1)
    run_tests()
