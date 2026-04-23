import requests
import time

base_url = "http://localhost:8000/api/v1"
FACULTY_SECRET = "PROXM_FACULTY_2026"

def run_tests():
    print("--- Starting Complete Test Suite ---")
    
    # 1. Student Registration
    print("1. Testing Student Registration...")
    res = requests.post(f"{base_url}/auth/register", json={
        "name": "Complete Student",
        "email": "complete_student@example.com",
        "password": "password123",
        "role": "student"
    })
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    student_token = res.json()["access_token"]
    print("✅ Student registered")

    # 2. Faculty Registration (Invalid Secret)
    print("2. Testing Faculty Registration (Invalid Secret)...")
    res = requests.post(f"{base_url}/auth/register", json={
        "name": "Fake Faculty",
        "email": "fake_faculty@example.com",
        "password": "password123",
        "role": "faculty",
        "secret_key": "WRONG_SECRET"
    })
    assert res.status_code == 403, f"Expected 403, got {res.status_code}: {res.text}"
    print("✅ Invalid secret blocked")

    # 3. Faculty Registration (Valid Secret)
    print("3. Testing Faculty Registration (Valid Secret)...")
    res = requests.post(f"{base_url}/auth/register", json={
        "name": "Complete Faculty",
        "email": "complete_faculty@example.com",
        "password": "password123",
        "role": "faculty",
        "secret_key": FACULTY_SECRET
    })
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    faculty_token = res.json()["access_token"]
    print("✅ Faculty registered")

    # 4. Email Collision (Cross-table)
    print("4. Testing Email Collision (Student email as Faculty)...")
    res = requests.post(f"{base_url}/auth/register", json={
        "name": "Double User",
        "email": "complete_student@example.com",
        "password": "password123",
        "role": "faculty",
        "secret_key": FACULTY_SECRET
    })
    # Since we check both tables in registration logic now (or should), this should fail
    # Wait, my logic in auth.py checks FacultyUser if role is faculty. 
    # But does it check User? 
    # Let's verify: In auth.py, I added checks for both tables in login/forgot-password. 
    # In register, I should ideally check both.
    assert res.status_code == 400 or res.status_code == 409
    print("✅ Email collision blocked")

    # 5. /me endpoint
    print("5. Testing /me endpoint for both...")
    headers_f = {"Authorization": f"Bearer {faculty_token}"}
    res_f = requests.get(f"{base_url}/auth/me", headers=headers_f)
    assert res_f.status_code == 200
    assert res_f.json()["role"] == "faculty"

    headers_s = {"Authorization": f"Bearer {student_token}"}
    res_s = requests.get(f"{base_url}/auth/me", headers=headers_s)
    assert res_s.status_code == 200
    assert res_s.json()["role"] == "student"
    print("✅ /me endpoint works for both collections")

    # 6. Admin Registration
    print("6. Testing Admin Registration...")
    res = requests.post(f"{base_url}/auth/register", json={
        "name": "Complete Admin",
        "email": "complete_admin@example.com",
        "password": "password123",
        "role": "admin",
        "secret_key": FACULTY_SECRET
    })
    assert res.status_code == 200
    admin_token = res.json()["access_token"]
    print("✅ Admin registered")

    # 7. Admin can see all users
    print("7. Testing Admin list users...")
    headers_a = {"Authorization": f"Bearer {admin_token}"}
    res = requests.get(f"{base_url}/admin/users", headers=headers_a)
    assert res.status_code == 200
    users_list = res.json()
    emails = [u["email"] for u in users_list]
    assert "complete_student@example.com" in emails
    assert "complete_faculty@example.com" in emails
    print(f"✅ Admin sees {len(users_list)} total users from both collections")

    # 8. Faculty can create exam
    print("8. Testing Exam Creation...")
    res = requests.post(f"{base_url}/exams/", headers=headers_f, json={
        "title": "Final Exam",
        "description": "Test description",
        "sections": []
    })
    assert res.status_code == 200
    print("✅ Faculty created exam")

    # 9. Student cannot create exam
    print("9. Testing Student Exam Block...")
    res = requests.post(f"{base_url}/exams/", headers=headers_s, json={
        "title": "Illegal Exam",
        "sections": []
    })
    assert res.status_code == 403
    print("✅ Student blocked from exam creation")

    print("\n🚀 ALL COMPLETE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    time.sleep(1)
    run_tests()
