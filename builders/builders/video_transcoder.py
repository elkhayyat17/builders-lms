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

def probe_video_resolution(input_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=s=x:p=0",
        input_path
    ]
    try:
        res = subprocess.check_output(cmd).decode().strip()
        parts = res.split("x")
        if len(parts) == 2:
            return int(parts[0]), int(parts[1])
    except Exception:
        pass
    return 1920, 1080

ALL_RENDITIONS = [
    {
        "name": "1080p",
        "height": 1080,
        "width": 1920,
        "bitrate": "2800k",
        "maxrate": "3200k",
        "bufsize": "5600k",
        "audio_bitrate": "128k",
        "bandwidth": 3328000,
    },
    {
        "name": "720p",
        "height": 720,
        "width": 1280,
        "bitrate": "1400k",
        "maxrate": "1600k",
        "bufsize": "2800k",
        "audio_bitrate": "128k",
        "bandwidth": 1728000,
    },
    {
        "name": "480p",
        "height": 480,
        "width": 854,
        "bitrate": "800k",
        "maxrate": "950k",
        "bufsize": "1600k",
        "audio_bitrate": "96k",
        "bandwidth": 896000,
    },
    {
        "name": "360p",
        "height": 360,
        "width": 640,
        "bitrate": "400k",
        "maxrate": "450k",
        "bufsize": "800k",
        "audio_bitrate": "64k",
        "bandwidth": 464000,
    },
]

def transcode_video(file_path, video_id=None, course=None, lesson=None, delete_original=True, multi_bitrate=True):
    """
    Automated AES-128 Multi-Bitrate Adaptive HLS Transcoder (ABR).
    1. Generates 16-byte random key and IV.
    2. Stores key safely in MariaDB video security table.
    3. Transcodes video into multi-rendition HLS (1080p, 720p, 480p, 360p).
    4. Generates standard Master Playlist with bandwidth tiers.
    5. Deletes original unencrypted raw MP4.
    6. Returns stream metadata.
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

    key_uri = f"/api/method/builders.utils.get_video_key?video_id={video_id}"
    with open(temp_keyinfo_path, "w", encoding="utf-8") as f:
        f.write(f"{key_uri}\n{temp_key_path}\n{iv_hex}\n")

    # Probe source resolution to determine active renditions
    src_width, src_height = probe_video_resolution(abs_input_path)
    if multi_bitrate:
        active_renditions = [r for r in ALL_RENDITIONS if src_height >= r["height"] - 50]
        if not active_renditions:
            active_renditions = [ALL_RENDITIONS[-1]]  # At least 360p
    else:
        active_renditions = [{
            "name": "default",
            "height": src_height,
            "width": src_width,
            "bitrate": "2200k",
            "maxrate": "2600k",
            "bufsize": "4400k",
            "audio_bitrate": "128k",
            "bandwidth": 2328000
        }]

    try:
        # Transcode each rendition
        for r in active_renditions:
            rendition_m3u8 = os.path.join(output_dir, f"{r['name']}.m3u8")
            segment_pattern = os.path.join(output_dir, f"{r['name']}_%03d.ts")

            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-i", abs_input_path,
                "-vf", f"scale=-2:{r['height']}",
                "-c:v", "libx264", "-preset", "veryfast",
                "-b:v", r["bitrate"], "-maxrate", r["maxrate"], "-bufsize", r["bufsize"],
                "-c:a", "aac", "-b:a", r["audio_bitrate"],
                "-hls_time", "6",
                "-hls_playlist_type", "vod",
                "-hls_key_info_file", temp_keyinfo_path,
                "-hls_segment_filename", segment_pattern,
                rendition_m3u8
            ]

            subprocess.run(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )

        # Generate Master Playlist (playlist.m3u8) referencing all variants
        master_playlist_path = os.path.join(output_dir, "playlist.m3u8")
        if len(active_renditions) > 1:
            master_lines = ["#EXTM3U", "#EXT-X-VERSION:3"]
            for r in active_renditions:
                master_lines.append(f'#EXT-X-STREAM-INF:BANDWIDTH={r["bandwidth"]},RESOLUTION={r["width"]}x{r["height"]},NAME="{r["name"]}"')
                master_lines.append(f'{r["name"]}.m3u8')
            with open(master_playlist_path, "w", encoding="utf-8") as f:
                f.write("\n".join(master_lines) + "\n")
        else:
            # Single rendition backward-compat
            single_r = active_renditions[0]
            single_file = os.path.join(output_dir, f"{single_r['name']}.m3u8")
            if os.path.exists(single_file):
                with open(single_file, "r", encoding="utf-8") as sf:
                    content = sf.read()
                with open(master_playlist_path, "w", encoding="utf-8") as mf:
                    mf.write(content)

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
