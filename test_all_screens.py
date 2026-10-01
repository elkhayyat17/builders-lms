import requests
import json
import time
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


BASE_URL_8000 = "http://localhost:8000"
BASE_URL_3000 = "http://localhost:3000"

results = []

def record(test_name, category, passed, status_code=None, details=""):
    results.append({
        "name": test_name,
        "category": category,
        "passed": passed,
        "status_code": status_code,
        "details": details
    })
    mark = "PASS" if passed else "FAIL"
    print(f"[{mark}] {category} - {test_name} (Code: {status_code}) -> {details}")

print("=" * 80)
print("🚀 STARTING REAL END-TO-END TEST SUITE FOR BUILDERS LMS")
print("=" * 80)

session = requests.Session()

# ----------------------------------------------------------------------
# 1. LANDING & SHOWCASE (Port 3000)
# ----------------------------------------------------------------------
print("\n--- 1. Testing Landing Page & Marketing Showcase (Port 3000) ---")
try:
    r = requests.get(f"{BASE_URL_3000}/", timeout=5)
    r.encoding = 'utf-8'
    has_brand = any(b in r.text for b in ["Handastech", "هندسة تك", "Builders", "بيلدرز"])
    has_disciplines = "الهندسة الإنشائية" in r.text and ("الفيديك" in r.text or "FIDIC" in r.text)
    has_lms_link = "http://localhost:8000/lms" in r.text
    passed = r.status_code == 200 and has_brand and has_disciplines and has_lms_link
    record("Marketing Landing Page (index.html)", "Landing", passed, r.status_code,
           f"Length: {len(r.text)} bytes, Has Brand: {has_brand}, Has Disciplines: {has_disciplines}, Has LMS Link: {has_lms_link}")
except Exception as e:
    record("Marketing Landing Page (index.html)", "Landing", False, None, str(e))

# ----------------------------------------------------------------------
# 2. LMS PORTAL ROOT & ASSETS (Port 8000)
# ----------------------------------------------------------------------
print("\n--- 2. Testing LMS Portal Root & Static Assets (Port 8000) ---")
try:
    r = requests.get(f"{BASE_URL_8000}/lms", timeout=5)
    has_spa = "_lms" in r.text or "app" in r.text or "frontend" in r.text
    record("LMS Portal Entry (/lms)", "Frontend SPA", r.status_code == 200 and has_spa, r.status_code,
           f"Length: {len(r.text)} bytes, Header: {r.headers.get('X-Page-Name')}")
except Exception as e:
    record("LMS Portal Entry (/lms)", "Frontend SPA", False, None, str(e))

# Test Theme CSS
try:
    r = requests.get(f"{BASE_URL_8000}/assets/builders/css/builders-theme.css", timeout=5)
    has_colors = "--builders-primary: #0066CC" in r.text or "--builders-primary: #1B4D7A" in r.text
    record("Handastech Brand Theme CSS", "Styling & Assets", r.status_code == 200 and has_colors, r.status_code,
           f"Contains modern primary color: {has_colors}")
except Exception as e:
    record("Handastech Brand Theme CSS", "Styling & Assets", False, None, str(e))

# Test RTL CSS
try:
    r = requests.get(f"{BASE_URL_8000}/assets/builders/css/builders-rtl.css", timeout=5)
    has_rtl = "[dir='rtl']" in r.text
    record("Builders Arabic RTL CSS", "Styling & Assets", r.status_code == 200 and has_rtl, r.status_code,
           f"Contains [dir='rtl'] rules: {has_rtl}")
except Exception as e:
    record("Builders Arabic RTL CSS", "Styling & Assets", False, None, str(e))

# Test Language Toggle JS
try:
    r = requests.get(f"{BASE_URL_8000}/assets/builders/js/language-toggle.js", timeout=5)
    has_js = "builders-lang-toggle" in r.text
    record("Builders Language Toggle JS", "Styling & Assets", r.status_code == 200 and has_js, r.status_code,
           f"Contains language switcher logic: {has_js}")
except Exception as e:
    record("Builders Language Toggle JS", "Styling & Assets", False, None, str(e))

# Test Category SVG Icons
for icon in ["structural", "construction-mgmt", "codes", "software", "quantity-surveying"]:
    try:
        r = requests.get(f"{BASE_URL_8000}/assets/builders/images/category-icons/{icon}.svg", timeout=5)
        record(f"Category Icon SVG ({icon})", "Icons & Assets", r.status_code == 200 and "<svg" in r.text, r.status_code,
               f"Content-Type: {r.headers.get('Content-Type')}")
    except Exception as e:
        record(f"Category Icon SVG ({icon})", "Icons & Assets", False, None, str(e))

# ----------------------------------------------------------------------
# 3. GUEST REST APIs & SEED VERIFICATION
# ----------------------------------------------------------------------
print("\n--- 3. Testing Guest REST APIs & Data Seed ---")
try:
    r = requests.get(f"{BASE_URL_8000}/api/method/builders.utils.get_featured_courses", timeout=5)
    data = r.json().get("message", [])
    has_5_courses = len(data) == 5
    currencies = [c.get("currency") for c in data]
    all_sar = all(c == "SAR" for c in currencies)
    record("API: get_featured_courses", "Guest API", r.status_code == 200 and has_5_courses and all_sar, r.status_code,
           f"Courses count: {len(data)}, All SAR: {all_sar}, Titles: {[c.get('name') for c in data]}")
except Exception as e:
    record("API: get_featured_courses", "Guest API", False, None, str(e))

try:
    r = requests.get(f"{BASE_URL_8000}/api/method/builders.utils.get_categories_with_count", timeout=5)
    data = r.json().get("message", [])
    civil_cats = [c for c in data if c.get("course_count", 0) > 0]
    record("API: get_categories_with_count", "Guest API", r.status_code == 200 and len(civil_cats) >= 5, r.status_code,
           f"Total categories: {len(data)}, Categories with active courses: {len(civil_cats)}")
except Exception as e:
    record("API: get_categories_with_count", "Guest API", False, None, str(e))

try:
    r = requests.get(f"{BASE_URL_8000}/api/method/lms.lms.api.get_branding", timeout=5)
    data = r.json().get("message", {})
    record("API: get_branding", "Guest API", r.status_code == 200, r.status_code,
           f"App Name: {data.get('app_name')}")
except Exception as e:
    record("API: get_branding", "Guest API", False, None, str(e))

# ----------------------------------------------------------------------
# 4. AUTHENTICATION & SESSION MANAGEMENT
# ----------------------------------------------------------------------
print("\n--- 4. Testing Authentication & Session Management ---")
login_success = False
try:
    login_payload = {
        "usr": "Administrator",
        "pwd": "admin"
    }
    r = session.post(f"{BASE_URL_8000}/api/method/login", data=login_payload, timeout=5)
    resp_json = r.json()
    login_success = r.status_code == 200 and resp_json.get("message") == "Logged In"
    sid = session.cookies.get("sid")
    record("Authentication (/api/method/login)", "Auth", login_success, r.status_code,
           f"Logged in: {login_success}, SID Cookie present: {bool(sid)}, Home Page: {resp_json.get('home_page')}")
except Exception as e:
    record("Authentication (/api/method/login)", "Auth", False, None, str(e))

# Test Authenticated User Info API
try:
    r = session.get(f"{BASE_URL_8000}/api/method/lms.lms.api.get_user_info", timeout=5)
    user_info = r.json().get("message", {})
    is_admin = user_info.get("name") == "Administrator"
    is_sys_mgr = user_info.get("is_system_manager") == True
    record("API: get_user_info", "Auth", r.status_code == 200 and is_admin, r.status_code,
           f"User: {user_info.get('name')}, Full Name: {user_info.get('full_name')}, Is SysManager: {is_sys_mgr}")
except Exception as e:
    record("API: get_user_info", "Auth", False, None, str(e))

# ----------------------------------------------------------------------
# 5. COURSE OUTLINE & LESSON PLAYER REAL VERIFICATION
# ----------------------------------------------------------------------
print("\n--- 5. Testing Course Curriculum & Lesson Player ---")
courses_to_test = [
    ("sbc-304", "كود البناء السعودي SBC 304"),
    ("fidic", "عقود فيديك FIDIC"),
    ("etabs-safe", "برامج ETABS & SAFE")
]

for course_name, label in courses_to_test:
    try:
        r = session.get(f"{BASE_URL_8000}/api/method/lms.lms.utils.get_course_outline", params={"course": course_name}, timeout=5)
        outline = r.json().get("message", [])
        has_chapters = len(outline) > 0
        total_lessons = sum(len(ch.get("lessons", [])) for ch in outline)
        record(f"Course Outline: {course_name} ({label})", "Curriculum", r.status_code == 200 and has_chapters and total_lessons > 0, r.status_code,
               f"Chapters: {len(outline)}, Lessons: {total_lessons}")
    except Exception as e:
        record(f"Course Outline: {course_name}", "Curriculum", False, None, str(e))

# Test Fetching a Specific Lesson for SBC 304 (Lesson 1.1)
try:
    # First get lesson document name from outline
    r_outline = session.get(f"{BASE_URL_8000}/api/method/lms.lms.utils.get_course_outline", params={"course": "sbc-304"}, timeout=5)
    outline = r_outline.json().get("message", [])
    first_lesson = outline[0]["lessons"][0]
    lesson_name = first_lesson["name"]
    lesson_title = first_lesson["title"]
    
    # Fetch lesson details
    r_lesson = session.get(f"{BASE_URL_8000}/api/resource/Course Lesson/{lesson_name}", timeout=5)
    lesson_doc = r_lesson.json().get("data", {})
    has_body = len(lesson_doc.get("body", "")) > 100
    has_youtube = bool(lesson_doc.get("youtube"))
    has_latex = "1.2 D + 1.6 L" in lesson_doc.get("body", "")
    passed = r_lesson.status_code == 200 and has_body and has_youtube and has_latex
    record("Interactive Lesson Content (/api/resource/Course Lesson)", "Lesson Player", passed, r_lesson.status_code,
           f"Title: {lesson_title}, Has Body: {has_body}, Has Video: {has_youtube}, Has SBC Formulas: {has_latex}")
except Exception as e:
    record("Interactive Lesson Content", "Lesson Player", False, None, str(e))

# ----------------------------------------------------------------------
# 6. DESK BACKEND & ADMIN ACCESS
# ----------------------------------------------------------------------
print("\n--- 6. Testing Frappe Desk Backend & Management Screens ---")
try:
    r = session.get(f"{BASE_URL_8000}/app", timeout=5)
    record("Frappe Desk Home (/app)", "Desk Backend", r.status_code == 200 and "desk" in r.text, r.status_code,
           f"Length: {len(r.text)} bytes")
except Exception as e:
    record("Frappe Desk Home (/app)", "Desk Backend", False, None, str(e))

try:
    r = session.get(f"{BASE_URL_8000}/api/resource/LMS Course?limit=10", timeout=5)
    courses = r.json().get("data", [])
    record("Desk API: List LMS Courses", "Desk Backend", r.status_code == 200 and len(courses) >= 5, r.status_code,
           f"Retrieved {len(courses)} courses from DB")
except Exception as e:
    record("Desk API: List LMS Courses", "Desk Backend", False, None, str(e))

try:
    r = session.get(f"{BASE_URL_8000}/api/resource/LMS Category?limit=20", timeout=5)
    cats = r.json().get("data", [])
    record("Desk API: List LMS Categories", "Desk Backend", r.status_code == 200 and len(cats) >= 5, r.status_code,
           f"Retrieved {len(cats)} categories from DB")
except Exception as e:
    record("Desk API: List LMS Categories", "Desk Backend", False, None, str(e))

# ----------------------------------------------------------------------
# 7. REAL HTTP SCREEN ROUTE CHECKS (SPA Deep-Links)
# ----------------------------------------------------------------------
print("\n--- 7. Testing Real HTTP Screen Route Resolution (SPA Deep-Links) ---")
spa_routes_to_test = [
    ("/lms/courses", "Courses Catalog Screen"),
    ("/lms/courses/sbc-304", "Course Detail Screen (SBC 304)"),
    ("/lms/courses/sbc-304/learn/1-1", "Interactive Lesson Player Screen"),
    ("/lms/batches", "Cohorts & Batches Screen"),
    ("/lms/programs", "Programs & Diplomas Screen"),
    ("/lms/quizzes", "Quizzes & Assessments Screen"),
    ("/lms/assignments", "Assignments & Submissions Screen"),
    ("/lms/programming-exercises", "Programming Exercises Screen"),
    ("/lms/certified-participants", "Certified Participants Screen"),
    ("/lms/job-openings", "Engineering Job Board Screen"),
    ("/lms/user/Administrator", "Learner Profile Screen"),
    ("/lms/billing/course/sbc-304", "Checkout & Billing Screen"),
    ("/lms/you", "Mobile Hub Screen"),
    ("/login", "Login Screen"),
]

for route, screen_name in spa_routes_to_test:
    try:
        r = session.get(f"{BASE_URL_8000}{route}", timeout=5)
        # Check HTTP 200 and valid HTML response
        is_html = "text/html" in r.headers.get("Content-Type", "")
        passed = r.status_code == 200 and is_html and len(r.text) > 500
        record(f"Screen: {screen_name} ({route})", "Screen Route", passed, r.status_code,
               f"Content-Type: {r.headers.get('Content-Type')}, Length: {len(r.text)} bytes")
    except Exception as e:
        record(f"Screen: {screen_name} ({route})", "Screen Route", False, None, str(e))


# ----------------------------------------------------------------------
# SUMMARY REPORT
# ----------------------------------------------------------------------
print("\n" + "=" * 80)
total_tests = len(results)
passed_tests = sum(1 for r in results if r["passed"])
failed_tests = total_tests - passed_tests

print(f"📊 REAL TEST SUITE SUMMARY: {passed_tests}/{total_tests} PASSED ({passed_tests/total_tests*100:.1f}%)")
if failed_tests > 0:
    print(f"❌ FAILED TESTS ({failed_tests}):")
    for r in results:
        if not r["passed"]:
            print(f"   - {r['category']}: {r['name']} -> {r['details']}")
else:
    print("🎉 ALL TESTS PASSED WITH 100% SUCCESS RATE!")
print("=" * 80)
