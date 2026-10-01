import frappe


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
    """Inject builders-specific variables into website context."""
    context.builders_brand = {
        "name": "Builders",
        "tagline_ar": "ابنِ مسيرتك المهنية في الهندسة المدنية",
        "tagline_en": "Build Your Civil Engineering Career",
        "primary_color": "#1B4D7A",
        "accent_color": "#D4A843",
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

