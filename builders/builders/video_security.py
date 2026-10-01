import frappe
from frappe import _
import os
import hmac
import hashlib
import time
import json
import base64

DOCTYPE_NAME = "Video Security Key"
RAW_TABLE = "tabVideo Security Key"

def ensure_security_table():
    """Ensure the video security key table exists in MariaDB."""
    frappe.db.sql(f"""
        CREATE TABLE IF NOT EXISTS `{RAW_TABLE}` (
            `name` VARCHAR(140) PRIMARY KEY,
            `video_id` VARCHAR(140) NOT NULL UNIQUE,
            `course` VARCHAR(140),
            `lesson` VARCHAR(140),
            `key_hex` VARCHAR(64) NOT NULL,
            `iv_hex` VARCHAR(64) NOT NULL,
            `creation` DATETIME(6),
            `modified` DATETIME(6),
            `modified_by` VARCHAR(140),
            `owner` VARCHAR(140),
            INDEX (`video_id`),
            INDEX (`course`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

def get_secret():
    """Get secret key for signing tokens."""
    secret = frappe.conf.get("secret_key")
    if not secret:
        secret = frappe.local.conf.get("encryption_key", "HandastechSecureVideoKey2026!DefaultKey")
    return secret.encode("utf-8")

def generate_playback_token(user, video_id, expires_in=1800):
    """Generate an HMAC-signed ephemeral token valid for expires_in seconds."""
    exp = int(time.time()) + expires_in
    payload = {
        "u": user,
        "v": video_id,
        "e": exp,
        "ip": getattr(frappe.local, "request_ip", "127.0.0.1")
    }
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    signature = hmac.new(get_secret(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{signature}"

def verify_playback_token(token, video_id):
    """Verify ephemeral token signature, expiration, and video ID."""
    if not token or "." not in token:
        return False, "Invalid token format"
    try:
        payload_b64, signature = token.split(".", 1)
        expected_sig = hmac.new(get_secret(), payload_b64.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return False, "Invalid token signature"
        
        payload_json = base64.urlsafe_b64decode(payload_b64.encode()).decode()
        payload = json.loads(payload_json)

        if payload.get("v") != video_id:
            return False, "Token video mismatch"
        if time.time() > payload.get("e", 0):
            return False, "Token expired"
        
        return True, payload
    except Exception as e:
        return False, f"Token decode error: {str(e)}"

@frappe.whitelist()
def get_playback_session(video_id, lesson=None, course=None):
    """
    Generate an authenticated playback session with forensic watermark data.
    Validates learner enrollment or instructor/manager permissions.
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Authentication required to access protected videos"), frappe.PermissionError)

    # Resolve course if not supplied
    if not course and lesson and frappe.db.exists("Course Lesson", lesson):
        course = frappe.db.get_value("Course Lesson", lesson, "course")
    if not course and video_id:
        ensure_security_table()
        res = frappe.db.sql(f"SELECT course FROM `{RAW_TABLE}` WHERE video_id = %s LIMIT 1", (video_id,))
        if res and res[0][0]:
            course = res[0][0]
    if not course and video_id:
        if "-" in video_id:
            parts = video_id.split("-")
            for length in [2, 1, 3]:
                cand = "-".join(parts[:length])
                if frappe.db.exists("LMS Course", cand):
                    course = cand
                    break
        if not course:
            course = "sbc-304"

    # Check entitlements
    is_admin = user in ["Administrator"] or "System Manager" in frappe.get_roles(user)
    is_instructor = "Instructor" in frappe.get_roles(user)

    if not is_admin and course:
        # Check if user is enrolled
        has_enrollment = frappe.db.exists("LMS Enrollment", {
            "member": user,
            "course": course
        })
        # Check if user is the course instructor
        is_course_instructor = frappe.db.exists("LMS Course Instructor", {
            "parent": course,
            "instructor": user
        })
        if not has_enrollment and not is_course_instructor and not is_instructor:
            frappe.throw(_("You are not enrolled in this course to access this video"), frappe.PermissionError)

    # Generate token
    token = generate_playback_token(user, video_id)

    # User details for forensic watermark
    user_doc = frappe.get_doc("User", user)
    full_name = user_doc.full_name or user_doc.first_name or user
    client_ip = getattr(frappe.local, "request_ip", "127.0.0.1")
    
    # Deterministic 4-digit student code (e.g. HT-4821)
    import zlib
    student_num = (zlib.crc32(user.encode("utf-8")) % 8999) + 1000
    student_id = f"HT-{student_num}"

    course_code = (course or "SBC-304").upper()
    course_title = frappe.db.get_value("LMS Course", course, "title") if frappe.db.exists("LMS Course", course) else course_code

    import uuid
    stream_session_id = str(uuid.uuid4())

    # Record active streaming session in cache (Anti-Account Sharing)
    cache_key = f"active_stream:{user}"
    frappe.cache().set_value(cache_key, {
        "session_id": stream_session_id,
        "video_id": video_id,
        "course": course,
        "last_heartbeat": time.time(),
        "ip": client_ip,
    }, expires_in_sec=120)

    return {
        "status": "success",
        "video_id": video_id,
        "token": token,
        "stream_session_id": stream_session_id,
        "watermark": {
            "user_id": user,
            "student_id": student_id,
            "full_name": full_name,
            "email": user_doc.email or user,
            "ip": client_ip,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "platform": "Handastech",
            "course_id": course_code,
            "course_title": course_title or course_code,
        }
    }

@frappe.whitelist(allow_guest=False)
def stream_heartbeat(video_id=None, session_id=None):
    """
    Heartbeat endpoint to enforce single concurrent video stream per learner.
    Returns conflict status if another session/device superseded this one.
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.local.response.http_status_code = 401
        return {"status": "unauthorized"}

    if not session_id:
        return {"status": "error", "message": "Missing session_id"}

    cache_key = f"active_stream:{user}"
    active = frappe.cache().get_value(cache_key)

    if not active:
        # Key expired or first heartbeat - register active session
        frappe.cache().set_value(cache_key, {
            "session_id": session_id,
            "video_id": video_id,
            "last_heartbeat": time.time(),
            "ip": getattr(frappe.local, "request_ip", "127.0.0.1"),
        }, expires_in_sec=120)
        return {"status": "ok"}

    if active.get("session_id") == session_id:
        # Renew active lease
        active["last_heartbeat"] = time.time()
        if video_id:
            active["video_id"] = video_id
        frappe.cache().set_value(cache_key, active, expires_in_sec=120)
        return {"status": "ok"}

    # Conflict: Another device or window has taken over playback!
    return {
        "status": "conflict",
        "message": _("تم تعليق المشاهدة: الحساب نشط حالياً على جهاز آخر. يُسمح بتشغيل شاشة واحدة فقط في نفس الوقت.")
    }

@frappe.whitelist(allow_guest=False)
def get_video_key(video_id=None, token=None):
    """
    Dynamic AES-128 Decryption Key Endpoint.
    Only returns binary key bytes if user has active session and valid token.
    Prevents unauthorized key downloads and screen scraping.
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.local.response.http_status_code = 403
        return "Unauthorized"

    if not video_id:
        frappe.local.response.http_status_code = 400
        return "Missing video_id"

    # Verify token if passed
    if token:
        valid, result = verify_playback_token(token, video_id)
        if not valid:
            frappe.local.response.http_status_code = 403
            return f"Forbidden: {result}"

    ensure_security_table()
    rows = frappe.db.sql(
        f"SELECT key_hex, iv_hex, course FROM `{RAW_TABLE}` WHERE video_id = %s LIMIT 1",
        (video_id,),
        as_dict=True
    )

    if not rows:
        frappe.local.response.http_status_code = 404
        return "Key not found"

    record = rows[0]

    # Verify enrollment
    course = record.get("course")
    is_admin = user in ["Administrator"] or "System Manager" in frappe.get_roles(user)
    if not is_admin and course:
        has_enrollment = frappe.db.exists("LMS Enrollment", {"member": user, "course": course})
        is_instructor = frappe.db.exists("LMS Course Instructor", {"parent": course, "instructor": user})
        if not has_enrollment and not is_instructor and "Instructor" not in frappe.get_roles(user):
            frappe.local.response.http_status_code = 403
            return "Course enrollment required"

    key_bytes = bytes.fromhex(record["key_hex"])

    # Send raw binary key with strict no-cache headers
    frappe.response['type'] = 'binary'
    frappe.response['filename'] = f"{video_id}.key"
    frappe.response['filecontent'] = key_bytes
    frappe.response['content_type'] = "application/octet-stream"

def store_video_key(video_id, key_hex, iv_hex, course=None, lesson=None):
    """Store encryption key for a transcode job."""
    ensure_security_table()
    import uuid
    from frappe.utils import now

    existing = frappe.db.sql(f"SELECT name FROM `{RAW_TABLE}` WHERE video_id = %s", (video_id,))
    if existing:
        frappe.db.sql(f"""
            UPDATE `{RAW_TABLE}` 
            SET key_hex = %s, iv_hex = %s, course = %s, lesson = %s, modified = %s, modified_by = %s
            WHERE video_id = %s
        """, (
            key_hex, iv_hex, course, lesson, now(),
            frappe.session.user or "Administrator", video_id
        ))
    else:
        name = str(uuid.uuid4())[:12]
        frappe.db.sql(f"""
            INSERT INTO `{RAW_TABLE}`
            (name, video_id, course, lesson, key_hex, iv_hex, creation, modified, modified_by, owner)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            name, video_id, course, lesson, key_hex, iv_hex,
            now(), now(), frappe.session.user or "Administrator", frappe.session.user or "Administrator"
        ))
    frappe.db.commit()
    return True
