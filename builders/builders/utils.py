import frappe
from .video_security import get_playback_session, get_video_key, store_video_key, stream_heartbeat


@frappe.whitelist(allow_guest=True)
def get_featured_courses():
    """Return courses marked as featured for the homepage."""
    courses = frappe.get_all(
        "LMS Course",
        filters={"published": 1, "is_featured": 1},
        fields=[
            "name",
            "title",
            "short_introduction",
            "image",
            "paid_course",
            "course_price",
            "currency",
            "difficulty_level",
            "course_language",
            "preview_video_url",
        ],
        order_by="creation desc",
        page_length=6,
    )
    return courses


@frappe.whitelist(allow_guest=True)
def get_categories_with_count():
    """Return all LMS categories with their course counts."""
    categories = frappe.get_all(
        "LMS Category",
        fields=["name", "category"],
        order_by="category asc",
    )

    for cat in categories:
        cat["course_count"] = frappe.db.count(
            "LMS Course",
            filters={"category": cat["name"], "published": 1},
        )

    return categories


def update_website_context(context):
    """Inject handastech-specific variables into website context."""
    context.builders_brand = {
        "name": "Handastech",
        "name_ar": "هندسة تك",
        "tagline_ar": "حلول تقنية وهندسية متقدمة",
        "tagline_en": "Tech Solutions for Engineering",
        "logo_url": "/assets/builders/images/handastech-logo.png",
        "icon_url": "/assets/builders/images/handastech-icon.png",
        "primary_color": "#0066CC",
        "accent_color": "#0099FF",
        "dark_color": "#1E2530",
    }


@frappe.whitelist(allow_guest=True)
def get_branding():
    """Return public branding settings for Handastech."""
    return {
        "app_name": "Handastech | هندسة تك",
        "app_title": "Handastech",
        "name_ar": "هندسة تك",
        "tagline_ar": "حلول تقنية وهندسية متقدمة",
        "tagline_en": "Tech Solutions for Engineering",
        "logo_url": "/assets/builders/images/handastech-logo.png",
        "icon_url": "/assets/builders/images/handastech-icon.png",
        "favicon": "/assets/builders/images/favicon.png",
        "primary_color": "#0066CC",
        "dark_color": "#1E2530",
    }


@frappe.whitelist()
def check_email_status():
    """Return configured email accounts and queue status."""
    accounts = frappe.get_all(
        "Email Account",
        fields=["name", "email_id", "enable_outgoing", "default_outgoing", "smtp_server", "smtp_port"],
    )
    return {
        "accounts": accounts,
        "queue_total": frappe.db.count("Email Queue"),
        "queue_pending": frappe.db.count("Email Queue", {"status": "Not Sent"}),
        "queue_sent": frappe.db.count("Email Queue", {"status": "Sent"}),
        "queue_error": frappe.db.count("Email Queue", {"status": "Error"}),
    }

