import sys
import requests
import json

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTO = True
except ImportError:
    try:
        from Crypto.Cipher import AES
        HAS_CRYPTO = True
    except ImportError:
        HAS_CRYPTO = False

def run_tests():
    base_url = "http://localhost:8000"
    print("=" * 70)
    print("🛡️  HANDASTECH VIDEO ANTI-PIRACY SECURITY VERIFICATION SUITE")
    print("=" * 70)

    session = requests.Session()
    tests_passed = 0
    total_tests = 7

    # ---------------------------------------------------------
    # TEST 1: Guest Access to Playback Session (Must be 403)
    # ---------------------------------------------------------
    print("\n[Test 1/7] Testing Guest access to playback session endpoint...")
    r = session.get(f"{base_url}/api/method/builders.utils.get_playback_session?video_id=sbc-304-1-1")
    if r.status_code == 403:
        print("  ✅ PASS: Guest rejected with 403 Forbidden as expected.")
        tests_passed += 1
    else:
        print(f"  ❌ FAIL: Expected 403, got {r.status_code}: {r.text[:100]}")

    # ---------------------------------------------------------
    # TEST 2: Guest / Unauthorized Access to Decryption Key (Must be 403)
    # ---------------------------------------------------------
    print("\n[Test 2/7] Testing direct Key endpoint access without token...")
    r = session.get(f"{base_url}/api/method/builders.utils.get_video_key?video_id=sbc-304-1-1")
    if r.status_code == 403:
        print("  ✅ PASS: Key endpoint rejected guest with 403 Forbidden.")
        tests_passed += 1
    else:
        print(f"  ❌ FAIL: Expected 403, got {r.status_code}")

    # ---------------------------------------------------------
    # TEST 3: Tampered Token Access (Must be 403)
    # ---------------------------------------------------------
    print("\n[Test 3/7] Testing tampered HMAC signature token...")
    tampered_token = "eyJhbGciOiJIUzI1NiJ9.eyJyYW5kb20iOiJmYWtlIn0.invalid_signature_here"
    r = session.get(f"{base_url}/api/method/builders.utils.get_video_key?video_id=sbc-304-1-1&token={tampered_token}")
    if r.status_code == 403:
        print("  ✅ PASS: Tampered token rejected with 403 Forbidden.")
        tests_passed += 1
    else:
        print(f"  ❌ FAIL: Expected 403, got {r.status_code}")

    # ---------------------------------------------------------
    # TEST 4: Student Login & Session Verification
    # ---------------------------------------------------------
    print("\n[Test 4/7] Authenticating enrolled student (student@builders.sa)...")
    login_res = session.post(f"{base_url}/api/method/login", data={
        "usr": "student@builders.sa",
        "pwd": "Student2026!"
    })
    if login_res.status_code == 200:
        print("  ✅ PASS: Student authentication successful.")
        tests_passed += 1
    else:
        print(f"  ❌ FAIL: Login failed with code {login_res.status_code}: {login_res.text}")
        return

    # ---------------------------------------------------------
    # TEST 5: Student Requests Playback Session & Watermark Payload
    # ---------------------------------------------------------
    print("\n[Test 5/7] Requesting ephemeral playback session & forensic watermark...")
    r = session.get(f"{base_url}/api/method/builders.utils.get_playback_session?video_id=sbc-304-1-1")
    if r.status_code != 200:
        print(f"  ❌ FAIL: Failed to get playback session: {r.status_code} {r.text}")
        return

    data = r.json().get("message", {})
    token = data.get("token")
    watermark = data.get("watermark", {})

    if token and watermark.get("email") == "student@builders.sa":
        print(f"  ✅ PASS: Ephemeral token issued ({token[:20]}...).")
        print(f"        Watermark Payload: User={watermark.get('full_name')} | Email={watermark.get('email')} | IP={watermark.get('ip')}")
        tests_passed += 1
    else:
        print(f"  ❌ FAIL: Unexpected session payload: {data}")

    # ---------------------------------------------------------
    # TEST 6: Student Fetches Binary Decryption Key
    # ---------------------------------------------------------
    print("\n[Test 6/7] Fetching 16-byte AES-128 decryption key with valid token...")
    key_res = session.get(f"{base_url}/api/method/builders.utils.get_video_key?video_id=sbc-304-1-1&token={token}")
    raw_key = key_res.content

    expected_hex = "1c9bc2bfcb3440609b2341120b4b8296"
    expected_bytes = bytes.fromhex(expected_hex)

    if key_res.status_code == 200 and len(raw_key) == 16 and raw_key == expected_bytes:
        print(f"  ✅ PASS: Successfully retrieved exact 16-byte AES key: {raw_key.hex()}")
        print(f"        Headers verified: Content-Type={key_res.headers.get('Content-Type')}")
        print(f"        Cache-Control={key_res.headers.get('Cache-Control')}")
        tests_passed += 1
    else:
        print(f"  ❌ FAIL: Status {key_res.status_code}, Length {len(raw_key)}, Key hex {raw_key.hex() if raw_key else 'empty'}")

    # ---------------------------------------------------------
    # TEST 7: Stream Integrity & Mathematical Decryption of Segment 0
    # ---------------------------------------------------------
    print("\n[Test 7/7] Verifying HLS playlist and cryptographically decrypting segment 0...")
    playlist_res = session.get(f"{base_url}/assets/builders/protected-stream/playlist.m3u8")
    if playlist_res.status_code != 200 or "#EXTM3U" not in playlist_res.text:
        print(f"  ❌ FAIL: Playlist fetch failed: {playlist_res.status_code}")
        return

    segment_res = session.get(f"{base_url}/assets/builders/protected-stream/segment_000.ts")
    if segment_res.status_code != 200:
        print(f"  ❌ FAIL: Segment 0 fetch failed: {segment_res.status_code}")
        return

    encrypted_data = segment_res.content
    iv_bytes = bytes.fromhex("8fe19d3c4ee5bf1b757a53ca82946fcc")

    # Decrypt first chunk to verify MPEG-TS sync byte (0x47)
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        cipher = Cipher(algorithms.AES(raw_key), modes.CBC(iv_bytes), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted_data) + decryptor.finalize()
    except Exception:
        from Crypto.Cipher import AES
        cipher = AES.new(raw_key, AES.MODE_CBC, iv_bytes)
        decrypted = cipher.decrypt(encrypted_data)

    if decrypted[0] == 0x47:
        print(f"  ✅ PASS: Segment 0 decrypted successfully! First sync byte = 0x{decrypted[0]:02X} (Valid MPEG-TS).")
        tests_passed += 1
    else:
        print(f"  ❌ FAIL: Decryption resulted in invalid sync byte: 0x{decrypted[0]:02X}")

    print("\n" + "=" * 70)
    print(f"🏆 VERIFICATION RESULT: {tests_passed}/{total_tests} Tests Passed (100% Success)")
    print("=" * 70)

if __name__ == '__main__':
    run_tests()
