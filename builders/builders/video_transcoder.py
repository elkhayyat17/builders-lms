import os
import re
import sys
import time
import uuid
import secrets
import subprocess
import frappe
from frappe import _
from .video_security import store_video_key, RAW_TABLE, ensure_security_table

def resolve_file_path(file_path):
    """Resolve a file path or URL to an absolute filesystem path."""
    if not file_path:
        return None
    if os.path.isabs(file_path) and os.path.exists(file_path):
        return file_path
    
    clean_path = file_path.lstrip("/")
    if clean_path.startswith("files/"):
        clean_path = clean_path[len("files/"):]
    elif clean_path.startswith("private/files/"):
        clean_path = clean_path[len("private/files/"):]
    
    # Try public files first
    public_candidate = os.path.abspath(frappe.get_site_path("public", "files", clean_path))
    if os.path.exists(public_candidate):
        return public_candidate
    
    # Try private files
    private_candidate = os.path.abspath(frappe.get_site_path("private", "files", clean_path))
    if os.path.exists(private_candidate):
        return private_candidate
        
    # Fallback to direct path inside bench
    direct_candidate = os.path.abspath(frappe.get_site_path(clean_path))
    if os.path.exists(direct_candidate):
        return direct_candidate
        
    return public_candidate

def transcode_video(file_path, video_id=None, course=None, lesson=None, delete_original=True):
    """
    Automated AES-128 HLS Transcoder.
    1. Generates 16-byte random key and IV.
    2. Stores key safely in MariaDB video security table.
    3. Runs FFmpeg to create encrypted HLS stream.
    4. Deletes original unencrypted raw MP4.
    5. Returns stream metadata.
    """
    abs_input_path = resolve_file_path(file_path)
    if not abs_input_path or not os.path.exists(abs_input_path):
        raise FileNotFoundError(f"Input video file not found: {file_path}")

    if not video_id:
        base_name = os.path.splitext(os.path.basename(abs_input_path))[0]
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '-', base_name).strip('-')
        video_id = f"{sanitized}-{uuid.uuid4().hex[:6]}"

    # Setup output directory
    output_rel = os.path.join("files", "protected_videos", video_id)
    output_dir = os.path.abspath(frappe.get_site_path("public", output_rel))
    os.makedirs(output_dir, exist_ok=True)

    # Cryptographically secure random key & IV
    key_bytes = secrets.token_bytes(16)
    iv_bytes = secrets.token_bytes(16)
    key_hex = key_bytes.hex()
    iv_hex = iv_bytes.hex()

    # Store key in database
    store_video_key(video_id, key_hex, iv_hex, course=course, lesson=lesson)

    # Create temporary key and keyinfo files for FFmpeg
    temp_key_path = os.path.join(output_dir, ".temp_key.bin")
    temp_keyinfo_path = os.path.join(output_dir, ".temp_keyinfo.txt")

    with open(temp_key_path, "wb") as f:
        f.write(key_bytes)

    # Key info format:
    # 1: Key URI (requested by HLS players via authenticated API)
    # 2: Local path to binary key for FFmpeg to encrypt
    # 3: IV in hex
    key_uri = f"/api/method/builders.utils.get_video_key?video_id={video_id}"
    with open(temp_keyinfo_path, "w", encoding="utf-8") as f:
        f.write(f"{key_uri}\n{temp_key_path}\n{iv_hex}\n")

    playlist_path = os.path.join(output_dir, "playlist.m3u8")
    segment_pattern = os.path.join(output_dir, "segment_%03d.ts")

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", abs_input_path,
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        "-hls_time", "6",
        "-hls_playlist_type", "vod",
        "-hls_key_info_file", temp_keyinfo_path,
        "-hls_segment_filename", segment_pattern,
        playlist_path
    ]

    try:
        proc = subprocess.run(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.decode("utf-8", errors="replace")
        frappe.log_error(f"FFmpeg transcode failed for {video_id}: {err_msg}", "Video Transcoder")
        raise RuntimeError(f"FFmpeg transcoding failed: {err_msg[:300]}")
    finally:
        # Securely wipe temporary key files immediately
        if os.path.exists(temp_key_path):
            os.remove(temp_key_path)
        if os.path.exists(temp_keyinfo_path):
            os.remove(temp_keyinfo_path)

    # Count generated segments
    segments = [f for f in os.listdir(output_dir) if f.endswith(".ts")]

    # Delete original raw video file to eliminate raw media exposure
    raw_deleted = False
    if delete_original and os.path.exists(abs_input_path):
        try:
            os.remove(abs_input_path)
            raw_deleted = True
        except Exception as e:
            frappe.log_error(f"Failed to delete original raw video {abs_input_path}: {str(e)}", "Video Transcoder")

    playlist_url = f"/files/protected_videos/{video_id}/playlist.m3u8"

    # If lesson was provided, update lesson body URL
    if lesson and frappe.db.exists("Course Lesson", lesson):
        lesson_doc = frappe.get_doc("Course Lesson", lesson)
        if lesson_doc.body and file_path in lesson_doc.body:
            lesson_doc.body = lesson_doc.body.replace(file_path, playlist_url)
            lesson_doc.save(ignore_permissions=True)
            frappe.db.commit()

    return {
        "status": "success",
        "video_id": video_id,
        "playlist_url": playlist_url,
        "segments_count": len(segments),
        "raw_deleted": raw_deleted,
        "key_stored": True,
    }

def on_lesson_update(doc, method=None):
    """
    Frappe hook trigger on Course Lesson update.
    Detects unencrypted raw MP4 videos and schedules automated transcoding.
    """
    if not doc.body:
        return
    
    # Check for raw .mp4 references
    mp4_matches = re.findall(r'(/files/[^\s\'"()]+\.mp4)', doc.body)
    if mp4_matches:
        # Enqueue background transcoding job
        frappe.enqueue(
            "builders.video_transcoder.auto_transcode_lesson_videos",
            lesson_name=doc.name,
            course=doc.course,
            queue="default",
            timeout=600
        )

def auto_transcode_lesson_videos(lesson_name, course=None):
    """Background worker to transcode all raw MP4 videos in a lesson."""
    if not frappe.db.exists("Course Lesson", lesson_name):
        return
        
    doc = frappe.get_doc("Course Lesson", lesson_name)
    if not doc.body:
        return

    mp4_matches = list(set(re.findall(r'(/files/[^\s\'"()]+\.mp4)', doc.body)))
    if not mp4_matches:
        return

    updated = False
    for mp4_url in mp4_matches:
        try:
            res = transcode_video(
                file_path=mp4_url,
                course=course or doc.course,
                lesson=doc.name,
                delete_original=True
            )
            if res.get("status") == "success":
                doc.body = doc.body.replace(mp4_url, res["playlist_url"])
                updated = True
        except Exception as e:
            frappe.log_error(f"Auto-transcoding failed for {mp4_url} in {lesson_name}: {str(e)}", "Auto Transcode Worker")

    if updated:
        doc.save(ignore_permissions=True)
        frappe.db.commit()
