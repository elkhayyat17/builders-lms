import time
import sys
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def safe_print(msg):
    sys.stdout.buffer.write((str(msg) + "\n").encode("utf-8", errors="replace"))
    sys.stdout.buffer.flush()

safe_print("======================================================================")
safe_print("🔒  STAGE 2 VERIFICATION: CONCURRENT STREAM & ACCOUNT SHARING LOCK")
safe_print("======================================================================")

BASE_URL = "http://localhost:8000"

# ----------------------------------------------------------------------
# Part 1: API Level Concurrent Stream Conflict Verification
# ----------------------------------------------------------------------
safe_print("\n--- Part 1: Direct API Level Session Conflict Test ---")
session1 = requests.Session()
login_res = session1.post(f"{BASE_URL}/api/method/login", data={
    "usr": "student@builders.sa",
    "pwd": "Student2026!"
})
assert login_res.status_code == 200, f"Login failed: {login_res.text}"
safe_print("  ✅ Logged in as student@builders.sa (Session 1)")

# Device 1 requests playback session
p1_res = session1.get(f"{BASE_URL}/api/method/builders.utils.get_playback_session", params={"video_id": "sbc-304-1-1"})
assert p1_res.status_code == 200, f"Device 1 get_playback_session failed: {p1_res.text}"
p1_data = p1_res.json().get("message", {})
token_1 = p1_data.get("stream_session_id")
assert token_1, "Device 1 did not receive stream_session_id"
safe_print(f"  - Device 1 Session Token: {token_1[:12]}...")

# Device 1 sends heartbeat
hb1_res = session1.get(f"{BASE_URL}/api/method/builders.utils.stream_heartbeat", params={
    "video_id": "sbc-304-1-1",
    "session_id": token_1
})
assert hb1_res.status_code == 200 and hb1_res.json().get("message", {}).get("status") == "ok", f"HB1 failed: {hb1_res.text}"
safe_print("  ✅ Device 1 Heartbeat: OK (Lease Active)")

# Device 2 simulates a second browser/device opening the stream
session2 = requests.Session()
session2.post(f"{BASE_URL}/api/method/login", data={
    "usr": "student@builders.sa",
    "pwd": "Student2026!"
})
p2_res = session2.get(f"{BASE_URL}/api/method/builders.utils.get_playback_session", params={"video_id": "sbc-304-1-1"})
p2_data = p2_res.json().get("message", {})
token_2 = p2_data.get("stream_session_id")
assert token_2 and token_2 != token_1, "Device 2 did not obtain fresh session token"
safe_print(f"  - Device 2 Session Token: {token_2[:12]}... (Superseded Device 1)")

# Device 2 sends heartbeat (valid)
hb2_res = session2.get(f"{BASE_URL}/api/method/builders.utils.stream_heartbeat", params={
    "video_id": "sbc-304-1-1",
    "session_id": token_2
})
assert hb2_res.json().get("message", {}).get("status") == "ok", "HB2 failed"
safe_print("  ✅ Device 2 Heartbeat: OK")

# Now Device 1 attempts its next heartbeat: MUST return CONFLICT!
hb1_conflict = session1.get(f"{BASE_URL}/api/method/builders.utils.stream_heartbeat", params={
    "video_id": "sbc-304-1-1",
    "session_id": token_1
})
hb1_data = hb1_conflict.json().get("message", {})
safe_print(f"  - Device 1 Heartbeat Status: {hb1_data.get('status')}")
safe_print(f"  - Conflict Message: {hb1_data.get('message')}")
assert hb1_data.get("status") == "conflict", "Device 1 was not rejected with conflict status"
safe_print("  ✅ PASS: Device 1 superseded and rejected with CONFLICT status!")


# ----------------------------------------------------------------------
# Part 2: End-to-End Browser UI Lockout & Reclaim Verification
# ----------------------------------------------------------------------
safe_print("\n--- Part 2: Browser UI Lockout & Reclaim Test ---")

options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1280,720")

driver = webdriver.Chrome(options=options)

try:
    # 1. Login in browser
    safe_print("  [Step 1/4] Logging in student on Chrome...")
    driver.get(f"{BASE_URL}/login")
    time.sleep(2)
    driver.find_element(By.ID, "login_email").send_keys("student@builders.sa")
    driver.find_element(By.ID, "login_password").send_keys("Student2026!")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)

    # 2. Open lesson player
    safe_print("  [Step 2/4] Navigating to lesson player...")
    driver.get(f"{BASE_URL}/lms/courses/sbc-304/learn/1-1")
    time.sleep(3)

    videos = driver.find_elements(By.TAG_NAME, "video")
    assert len(videos) > 0, "Video element not found"
    driver.execute_script("arguments[0].muted = true; arguments[0].play();", videos[0])
    time.sleep(2)

    # Verify no lock shield initially
    initial_shields = driver.find_elements(By.ID, "ht-stream-lock-shield")
    assert len(initial_shields) == 0, "Stream lock shield appeared prematurely"
    safe_print("  ✅ Playback active without lock.")

    # 3. Simulate another device taking over session
    safe_print("  [Step 3/4] Device 2 takes over session via API...")
    hijack_session = requests.Session()
    hijack_session.post(f"{BASE_URL}/api/method/login", data={"usr": "student@builders.sa", "pwd": "Student2026!"})
    hijack_res = hijack_session.get(f"{BASE_URL}/api/method/builders.utils.get_playback_session", params={"video_id": "sbc-304-1-1"})
    safe_print(f"  - Device 2 hijacked session: {hijack_res.status_code == 200}")

    # Trigger heartbeat check in browser
    safe_print("  Triggering browser player heartbeat check via 'ht-check-heartbeat' event...")
    driver.execute_script("window.dispatchEvent(new CustomEvent('ht-check-heartbeat'));")
    time.sleep(3)

    # Check that lockout shield appeared and video paused
    shields = driver.find_elements(By.ID, "ht-stream-lock-shield")
    is_paused = driver.execute_script("return arguments[0].paused;", videos[0])
    safe_print(f"  - Lock Shield Element in DOM: {len(shields) > 0}")
    safe_print(f"  - Video Paused on Conflict: {is_paused}")
    assert len(shields) > 0 and is_paused, "Lock shield did not engage or video did not pause"
    safe_print("  ✅ PASS: Lockout shield engaged and playback halted on concurrent session!")

    # 4. Test Reclaim Playback button
    safe_print("  [Step 4/4] Testing 'المتابعة من هذا الجهاز' (Reclaim Playback)...")
    reclaim_btn = shields[0].find_element(By.TAG_NAME, "button")
    reclaim_btn.click()
    time.sleep(2)

    shields_after_reclaim = driver.find_elements(By.ID, "ht-stream-lock-shield")
    safe_print(f"  - Lock Shield Dismissed: {len(shields_after_reclaim) == 0}")
    assert len(shields_after_reclaim) == 0, "Lock shield was not dismissed after reclaim"
    safe_print("  ✅ PASS: Stream reclaimed and lock dismissed smoothly!")

    safe_print("\n======================================================================")
    safe_print("🏆 STAGE 2 VERIFICATION RESULT: 100% SUCCESS (ALL TESTS PASSED)")
    safe_print("======================================================================")

finally:
    driver.quit()
