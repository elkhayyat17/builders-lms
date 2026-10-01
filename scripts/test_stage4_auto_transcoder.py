import os
import sys
import subprocess
import requests
import json
import time

def safe_print(msg):
    sys.stdout.buffer.write((str(msg) + "\n").encode("utf-8", errors="replace"))
    sys.stdout.buffer.flush()

safe_print("======================================================================")
safe_print("⚙️   STAGE 4 VERIFICATION: AUTOMATED INGESTION & TRANSCODING PIPELINE")
safe_print("======================================================================")

# Step 1: Create a test video in Frappe's public/files directory inside docker
safe_print("\n[Step 1/5] Creating raw MP4 test upload in public/files...")
cmd1 = [
    "docker", "exec", "docker-frappe-1", "bash", "-c",
    "ffmpeg -y -f lavfi -i testsrc=duration=4:size=640x360:rate=30 -f lavfi -i sine=frequency=880:duration=4 -c:v libx264 -c:a aac /home/frappe/frappe-bench/sites/lms.localhost/public/files/test_raw_lecture.mp4"
]
res = subprocess.run(cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
assert res.returncode == 0, f"Failed to create test raw video: {res.stderr}"
safe_print("  ✅ Raw MP4 created: /files/test_raw_lecture.mp4")

# Step 2: Trigger the automated transcoder pipeline inside the container
safe_print("\n[Step 2/5] Executing automated video transcode pipeline...")
transcode_code = (
    "import frappe; from builders.video_transcoder import transcode_video; "
    "frappe.init('lms.localhost', sites_path='sites'); frappe.connect(); "
    "res = transcode_video(file_path='/files/test_raw_lecture.mp4', video_id='sbc-304-auto-transcoded-test', course='sbc-304', delete_original=True); "
    "print('TRANSCODE_RESULT:' + frappe.as_json(res))"
)

cmd2 = [
    "docker", "exec", "-w", "/home/frappe/frappe-bench", "docker-frappe-1",
    "./env/bin/python", "-c", transcode_code
]
trans_res = subprocess.run(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
safe_print(f"  Container Output:\n{trans_res.stdout.strip()}")
assert trans_res.returncode == 0, f"Transcoding failed: {trans_res.stderr}"
assert "TRANSCODE_RESULT:" in trans_res.stdout, "Transcode result marker missing"

result_json = trans_res.stdout.split("TRANSCODE_RESULT:")[1].strip()
result_data = json.loads(result_json)
safe_print(f"  - Video ID: {result_data.get('video_id')}")
safe_print(f"  - Playlist URL: {result_data.get('playlist_url')}")
safe_print(f"  - Segments Count: {result_data.get('segments_count')}")
safe_print(f"  - Raw Deleted: {result_data.get('raw_deleted')}")

assert result_data.get("segments_count", 0) > 0, "No HLS segments generated"
assert result_data.get("raw_deleted") is True, "Raw unencrypted MP4 was not deleted"
safe_print("  ✅ PASS: AES-128 HLS transcode completed and raw MP4 deleted.")

# Step 3: Verify Output Files and Encryption Playlist on Disk
safe_print("\n[Step 3/5] Verifying HLS playlist and AES-128 encryption tags on disk...")
cmd3 = [
    "docker", "exec", "docker-frappe-1", "cat",
    "/home/frappe/frappe-bench/sites/lms.localhost/public/files/protected_videos/sbc-304-auto-transcoded-test/playlist.m3u8"
]
cat_res = subprocess.run(cmd3, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
playlist_content = cat_res.stdout
safe_print("  Playlist Header:")
for line in playlist_content.splitlines()[:8]:
    safe_print(f"    {line}")

assert "#EXT-X-KEY:METHOD=AES-128" in playlist_content, "Missing AES-128 key directive in playlist"
assert 'URI="/api/method/builders.utils.get_video_key?video_id=sbc-304-auto-transcoded-test"' in playlist_content, "Key URI mismatch in playlist"
safe_print("  ✅ PASS: Playlist enforces AES-128 encryption with authenticated key URI.")

# Step 4: Verify Original Raw MP4 is Completely Gone
safe_print("\n[Step 4/5] Verifying complete elimination of raw unencrypted MP4...")
cmd4 = [
    "docker", "exec", "docker-frappe-1", "bash", "-c",
    "test -f /home/frappe/frappe-bench/sites/lms.localhost/public/files/test_raw_lecture.mp4 && echo 'EXISTS' || echo 'DELETED'"
]
del_res = subprocess.run(cmd4, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
raw_state = del_res.stdout.strip()
safe_print(f"  - Raw File State on Disk: {raw_state}")
assert raw_state == "DELETED", "Raw video file still exists on disk!"
safe_print("  ✅ PASS: Raw unencrypted video successfully purged from server storage.")

# Step 5: Test Key Retrieval through the Full Security Pipeline
safe_print("\n[Step 5/5] Testing key retrieval for auto-transcoded video through API...")
session = requests.Session()
session.post("http://localhost:8000/api/method/login", data={"usr": "student@builders.sa", "pwd": "Student2026!"})
sess_res = session.get(
    "http://localhost:8000/api/method/builders.utils.get_playback_session",
    params={"video_id": "sbc-304-auto-transcoded-test"},
    headers={"Referer": "http://localhost:8000/lms", "Origin": "http://localhost:8000"}
)
token = sess_res.json()["message"]["token"]

key_res = session.get(
    "http://localhost:8000/api/method/builders.utils.get_video_key",
    params={"video_id": "sbc-304-auto-transcoded-test", "token": token},
    headers={"Referer": "http://localhost:8000/lms", "Origin": "http://localhost:8000"}
)
safe_print(f"  - Decryption Key HTTP Status: {key_res.status_code}")
safe_print(f"  - Decryption Key Length: {len(key_res.content)} bytes")
assert key_res.status_code == 200 and len(key_res.content) == 16, "Failed to retrieve transcode key"
safe_print("  ✅ PASS: Authorized learner successfully received 16-byte AES-128 decryption key.")

safe_print("\n======================================================================")
safe_print("🏆 STAGE 4 VERIFICATION RESULT: 100% SUCCESS (ALL TESTS PASSED)")
safe_print("======================================================================")
