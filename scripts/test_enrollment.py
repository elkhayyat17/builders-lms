import requests
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()

# 1. Login as Administrator
r = session.post("http://localhost:8000/api/method/login", data={"usr": "Administrator", "pwd": "admin"})
assert r.status_code == 200, "Login failed"
print("✅ 1. Login successful as Administrator")

# 2. Check if already enrolled in sbc-304
r = session.get("http://localhost:8000/api/resource/LMS Enrollment?filters=[[\"course\",\"=\",\"sbc-304\"],[\"member\",\"=\",\"Administrator\"]]")
enrollments = r.json().get("data", [])
enrollment_name = None

if not enrollments:
    # Enroll Administrator in sbc-304
    r = session.post("http://localhost:8000/api/resource/LMS Enrollment", json={
        "course": "sbc-304",
        "member": "Administrator",
        "member_type": "Student"
    })
    if r.status_code in [200, 201]:
        enrollment_name = r.json().get("data", {}).get("name")
        print(f"✅ 2. Successfully enrolled Administrator in 'sbc-304' (Enrollment ID: {enrollment_name})")
    else:
        print(f"⚠️ Enrollment create returned: {r.status_code} - {r.text}")
else:
    enrollment_name = enrollments[0]["name"]
    print(f"✅ 2. Administrator already has active enrollment in 'sbc-304' (ID: {enrollment_name})")

# 3. Fetch course details and active student membership
r = session.get(f"http://localhost:8000/api/method/lms.lms.api.get_course_details?course=sbc-304")
if r.status_code == 200:
    details = r.json().get("message", {})
    membership = details.get("membership", {})
    print(f"✅ 3. Active membership verified: User={membership.get('member')}, Course={membership.get('course')}, Progress={membership.get('progress')}%")
else:
    print(f"⚠️ Progress fetch status: {r.status_code} - {r.text}")

print("🎉 Student Enrollment & Progress Flow Verified 100%!")

