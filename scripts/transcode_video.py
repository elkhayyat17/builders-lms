import os
import sys
import subprocess
import secrets
import argparse
import requests
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def transcode_to_hls_aes128(input_file, output_dir, video_id, course="sbc-304", lesson="1-1", frappe_url="http://localhost:8000"):
    """
    Transcode MP4 video into an encrypted HLS stream using AES-128 encryption.
    The encryption key is stored securely in MariaDB via Frappe API,
    and segments are served encrypted with dynamic key delivery.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input video file not found: {input_file}")

    os.makedirs(output_dir, exist_ok=True)

    # 1. Generate 128-bit (16-byte) cryptographically secure key and IV
    key_bytes = secrets.token_bytes(16)
    iv_bytes = secrets.token_bytes(16)
    key_hex = key_bytes.hex()
    iv_hex = iv_bytes.hex()

    print(f"🔐 Generated AES-128 Encryption Key for [{video_id}]:")
    print(f"   Key (hex): {key_hex}")
    print(f"   IV  (hex): {iv_hex}")

    # 2. Write temporary key file and key info file for FFmpeg
    temp_key_file = os.path.join(output_dir, "temp_enc.key")
    with open(temp_key_file, "wb") as f:
        f.write(key_bytes)

    # Key URL that the video player will request from the server
    key_url = f"/api/method/builders.utils.get_video_key?video_id={video_id}"

    key_info_file = os.path.join(output_dir, "enc.keyinfo")
    with open(key_info_file, "w", encoding="utf-8") as f:
        f.write(f"{key_url}\n")
        f.write(f"{os.path.abspath(temp_key_file)}\n")
        f.write(f"{iv_hex}\n")

    # 3. Store key in database using Python inside docker container or direct API
    print(f"💾 Storing encryption key in Handastech Database for video_id={video_id}...")
    import_cmd = f"""
import frappe
from builders.video_security import store_video_key
frappe.init(site='lms.localhost', sites_path='/home/frappe/frappe-bench/sites')
frappe.connect()
store_video_key('{video_id}', '{key_hex}', '{iv_hex}', course='{course}', lesson='{lesson}')
print('KEY_SAVED_OK')
"""
    cmd = [
        "docker", "exec", "-w", "/home/frappe/frappe-bench", "docker-frappe-1",
        "/home/frappe/frappe-bench/env/bin/python", "-c", import_cmd
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if "KEY_SAVED_OK" not in res.stdout:
        print(f"⚠️ Warning storing key via Docker: {res.stderr or res.stdout}")
    else:
        print(f"✅ Key securely stored in Database for course={course}")

    # 4. Run FFmpeg command to segment and encrypt
    playlist_path = os.path.join(output_dir, "playlist.m3u8")
    segment_format = os.path.join(output_dir, "segment_%03d.ts")

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", input_file,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-sc_threshold", "0",
        "-g", "48",
        "-keyint_min", "48",
        "-c:a", "aac",
        "-b:a", "128k",
        "-hls_time", "6",
        "-hls_playlist_type", "vod",
        "-hls_key_info_file", key_info_file,
        "-hls_segment_filename", segment_format,
        playlist_path
    ]

    print(f"⚙️ Running FFmpeg HLS Transcoding...")
    print(f"   Command: {' '.join(ffmpeg_cmd)}")
    
    proc = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"❌ FFmpeg error:\n{proc.stderr}")
        raise RuntimeError("FFmpeg transcoding failed")

    # 5. Clean up temporary unencrypted key files from filesystem
    if os.path.exists(temp_key_file):
        os.remove(temp_key_file)
    if os.path.exists(key_info_file):
        os.remove(key_info_file)

    # 6. Verify generated playlist
    if os.path.exists(playlist_path):
        with open(playlist_path, "r", encoding="utf-8") as f:
            manifest = f.read()
        has_key_tag = "#EXT-X-KEY:METHOD=AES-128" in manifest
        num_segments = manifest.count("#EXTINF:")
        print(f"\n🎉 HLS Transcoding Completed Successfully!")
        print(f"   Playlist: {playlist_path}")
        print(f"   Encrypted Segments: {num_segments} chunks")
        print(f"   AES-128 Tag in Manifest: {has_key_tag}")
        print(f"   Temporary key files wiped from disk (Safe)")
        return {
            "success": True,
            "playlist_path": playlist_path,
            "segments": num_segments,
            "has_encryption": has_key_tag
        }
    else:
        raise FileNotFoundError("playlist.m3u8 was not generated")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Handastech HLS AES-128 Video Transcoder")
    parser.add_argument("--input", "-i", default="lms/frontend/public/Upload.mp4", help="Path to input MP4 video")
    parser.add_argument("--outdir", "-o", default="lms/frontend/public/protected-stream", help="Output directory for HLS files")
    parser.add_argument("--videoid", "-v", default="sbc-304-1-1", help="Video unique identifier")
    parser.add_argument("--course", "-c", default="sbc-304", help="Course code")
    parser.add_argument("--lesson", "-l", default="1-1", help="Lesson identifier")

    args = parser.parse_args()
    transcode_to_hls_aes128(
        input_file=args.input,
        output_dir=args.outdir,
        video_id=args.videoid,
        course=args.course,
        lesson=args.lesson
    )
