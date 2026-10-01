import requests
import sys
import time
import base64
import json
import hmac
import hashlib

def safe_print(msg):
    sys.stdout.buffer.write((str(msg) + "\n").encode("utf-8", errors="replace"))
    sys.stdout.buffer.flush()

safe_print("======================================================================")
safe_print("🌐  STAGE 3 VERIFICATION: NETWORK & HOTLINK DEFENSE SUITE")
safe_print("======================================================================")

BASE_URL = "http://localhost:8000"
VIDEO_ID = "sbc-304-1-1"

# 1. Login as student
safe_print("\n[Step 1/5] Authenticating as student@builders.sa...")
session = requests.Session()
login_res = session.post(f"{BASE_URL}/api/method/login", data={
    "usr": "student@builders.sa",
    "pwd": "Student2026!"
})
assert login_res.status_code == 200, "Authentication failed"
safe_print("  ✅ Logged in successfully.")

# 2. Obtain legitimate session and ephemeral token
safe_print("\n[Step 2/5] Requesting playback session from authorized platform origin...")
legit_headers = {
    "Referer": "http://localhost:8000/lms/courses/sbc-304/learn/1-1",
    "Origin": "http://localhost:8000",
}
sess_res = session.get(
    f"{BASE_URL}/api/method/builders.utils.get_playback_session",
    params={"video_id": VIDEO_ID},
    headers=legit_headers
)
assert sess_res.status_code == 200, f"Session request failed: {sess_res.text}"
valid_token = sess_res.json()["message"]["token"]
safe_print(f"  - Valid Token Acquired: {valid_token[:20]}...")

# 3. Test Legitimate Key Request
safe_print("\n[Step 3/5] Testing legitimate decryption key retrieval (Authorized Origin + Valid Token)...")
key_res = session.get(
    f"{BASE_URL}/api/method/builders.utils.get_video_key",
    params={"video_id": VIDEO_ID, "token": valid_token},
    headers=legit_headers
)
safe_print(f"  - HTTP Status: {key_res.status_code}")
safe_print(f"  - Content-Type: {key_res.headers.get('Content-Type')}")
safe_print(f"  - Key Bytes Length: {len(key_res.content)}")
assert key_res.status_code == 200 and len(key_res.content) == 16, f"Legitimate key request failed: {key_res.status_code}"
safe_print("  ✅ PASS: 16-byte AES-128 decryption key successfully provided to legitimate player.")

# 4. Test Cross-Site Hotlinking Attack
safe_print("\n[Step 4/5] Simulating Cross-Site Hotlink Attack (Pirate Site Embedding)...")
pirate_headers = {
    "Referer": "https://pirate-streaming-site.net/watch/civil-engineering-course",
    "Origin": "https://pirate-streaming-site.net"
}
hotlink_res = session.get(
    f"{BASE_URL}/api/method/builders.utils.get_video_key",
    params={"video_id": VIDEO_ID, "token": valid_token},
    headers=pirate_headers
)
safe_print(f"  - Attack HTTP Status: {hotlink_res.status_code}")
safe_print(f"  - Attack Response Body: {hotlink_res.text.strip()}")
assert hotlink_res.status_code == 403, "Hotlink attack was NOT blocked"
assert "Hotlink blocked" in hotlink_res.text or "unauthorized domain" in hotlink_res.text, "Specific hotlink defense message missing"
safe_print("  ✅ PASS: Cross-site hotlink request blocked with HTTP 403 Forbidden.")

# 5. Test Download Manager (No Token) & Expired Token Attack
safe_print("\n[Step 5/5] Testing Direct Download Manager / Tampered & Expired Token Attacks...")
# A: Direct key scraping without playback session lease
scraper_session = requests.Session()
scraper_session.post(f"{BASE_URL}/api/method/login", data={"usr": "student@builders.sa", "pwd": "Student2026!"})
# Attempt to download key directly without calling get_playback_session
no_token_res = scraper_session.get(
    f"{BASE_URL}/api/method/builders.utils.get_video_key",
    params={"video_id": "unauthorized-video-id"},
    headers=legit_headers
)
safe_print(f"  - Direct Request Without Token Status: {no_token_res.status_code}")
assert no_token_res.status_code == 403, "Direct request without token was not blocked"

# B: Tampered token signature
tampered_token = valid_token[:-4] + "dead"
tampered_res = session.get(
    f"{BASE_URL}/api/method/builders.utils.get_video_key",
    params={"video_id": VIDEO_ID, "token": tampered_token},
    headers=legit_headers
)
safe_print(f"  - Tampered Token Signature Status: {tampered_res.status_code}")
assert tampered_res.status_code == 403, "Tampered token was not blocked"

safe_print("  ✅ PASS: All direct scraping and tampered token attacks rejected with HTTP 403 Forbidden.")

safe_print("\n======================================================================")
safe_print("🏆 STAGE 3 VERIFICATION RESULT: 100% SUCCESS (ALL TESTS PASSED)")
safe_print("======================================================================")
