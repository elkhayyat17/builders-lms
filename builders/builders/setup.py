import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


from .seed_curriculum import seed_curriculum


def after_install():
    """Create custom fields, seed categories, seed courses, and seed curriculum."""
    create_builders_custom_fields()
    seed_lms_categories()
    seed_civil_courses()
    seed_curriculum()
    frappe.db.commit()


def create_builders_custom_fields():
    """Add civil-engineering-specific fields to LMS Course."""
    create_custom_fields(
        {
            "LMS Course": [
                {
                    "fieldname": "builders_section",
                    "label": "Builders - معلومات إضافية",
                    "fieldtype": "Section Break",
                    "insert_after": "image",
                    "collapsible": 1,
                    "module": "Builders",
                },
                {
                    "fieldname": "difficulty_level",
                    "label": "Difficulty Level / مستوى الصعوبة",
                    "fieldtype": "Select",
                    "options": "\nBeginner / مبتدئ\nIntermediate / متوسط\nAdvanced / متقدم",
                    "insert_after": "builders_section",
                    "module": "Builders",
                },
                {
                    "fieldname": "course_language",
                    "label": "Course Language / لغة الدورة",
                    "fieldtype": "Select",
                    "options": "\nArabic / عربي\nEnglish / إنجليزي\nBilingual / ثنائي اللغة",
                    "insert_after": "difficulty_level",
                    "module": "Builders",
                },
                {
                    "fieldname": "column_break_builders",
                    "fieldtype": "Column Break",
                    "insert_after": "course_language",
                    "module": "Builders",
                },
                {
                    "fieldname": "preview_video_url",
                    "label": "Preview Video URL / رابط فيديو المعاينة",
                    "fieldtype": "Data",
                    "insert_after": "column_break_builders",
                    "module": "Builders",
                },
                {
                    "fieldname": "is_featured",
                    "label": "Featured / مميز",
                    "fieldtype": "Check",
                    "insert_after": "preview_video_url",
                    "description": "Show this course on the homepage featured section",
                    "module": "Builders",
                },
                {
                    "fieldname": "builders_details_section",
                    "label": "Audience & Prerequisites / الفئة المستهدفة والمتطلبات",
                    "fieldtype": "Section Break",
                    "insert_after": "is_featured",
                    "collapsible": 1,
                    "module": "Builders",
                },
                {
                    "fieldname": "target_audience",
                    "label": "Target Audience / الفئة المستهدفة",
                    "fieldtype": "Small Text",
                    "insert_after": "builders_details_section",
                    "module": "Builders",
                },
                {
                    "fieldname": "prerequisites",
                    "label": "Prerequisites / المتطلبات المسبقة",
                    "fieldtype": "Small Text",
                    "insert_after": "target_audience",
                    "module": "Builders",
                },
            ],
            "LMS Lesson Note": [
                {
                    "fieldname": "video_timestamp",
                    "label": "Video Timestamp (Seconds)",
                    "fieldtype": "Float",
                    "insert_after": "color",
                    "module": "Builders",
                },
                {
                    "fieldname": "formatted_time",
                    "label": "Formatted Time (mm:ss)",
                    "fieldtype": "Data",
                    "insert_after": "video_timestamp",
                    "module": "Builders",
                },
                {
                    "fieldname": "is_pinned",
                    "label": "Pinned Note",
                    "fieldtype": "Check",
                    "insert_after": "formatted_time",
                    "module": "Builders",
                },
            ],
        },
        update=True,
    )
    print("✅ Builders custom fields created on LMS Course and LMS Lesson Note")


def seed_lms_categories():
    """Populate LMS Category with civil engineering taxonomy."""
    categories = [
        "الهندسة الإنشائية - Structural Engineering",
        "إدارة المشاريع - Construction Management",
        "الأكواد والمعايير - Codes & Standards",
        "التدريب على البرمجيات - Software Training",
        "حصر الكميات - Quantity Surveying",
    ]

    for cat in categories:
        if not frappe.db.exists("LMS Category", {"category": cat}):
            doc = frappe.get_doc(
                {
                    "doctype": "LMS Category",
                    "category": cat,
                }
            )
            doc.insert(ignore_permissions=True)
            print(f"  📁 Created category: {cat}")
        else:
            print(f"  ✓ Category exists: {cat}")

    print("✅ LMS categories seeded")


def seed_civil_courses():
    """Seed initial sample civil engineering courses."""
    courses_data = [
        {
            "title": "تصميم المنشآت الخرسانية المسلحة وفق الكود السعودي SBC 304",
            "category": "الهندسة الإنشائية - Structural Engineering",
            "short_introduction": "دورة شاملة في التحليل والتصميم الإنشائي للعناصر الخرسانية المسلحة طبقاً لكود البناء السعودي SBC.",
            "description": "تغطي هذه الدورة كافة متطلبات المهندس الإنشائي من تصميم الأساسات والأعمدة والكمرات والبلاطات بأنواعها وفق متطلبات كود البناء السعودي.",
            "published": 1,
            "is_featured": 1,
            "difficulty_level": "Intermediate / متوسط",
            "course_language": "Arabic / عربي",
            "paid_course": 1,
            "course_price": 450,
            "currency": "SAR",
            "preview_video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        },
        {
            "title": "إدارة المشاريع الاحترافية ونظام عقود فيديك FIDIC",
            "category": "إدارة المشاريع - Construction Management",
            "short_introduction": "دليل المهندس في إدارة وتخطيط المشروعات الهندسية، المطالبات، وعقود الفيديك الإنشائية في الخليج.",
            "description": "تعلم التخطيط الزمني، وإدارة الميزانيات، وتوزيع المخاطر، والتعامل مع مطالبات التمديد الزمني والتعويضات المالية طبقاً لشروط عقد فيديك.",
            "published": 1,
            "is_featured": 1,
            "difficulty_level": "Advanced / متقدم",
            "course_language": "Arabic / عربي",
            "paid_course": 1,
            "course_price": 600,
            "currency": "SAR",
            "preview_video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        },
        {
            "title": "كود البناء السعودي الشامل للمهندس المدني SBC",
            "category": "الأكواد والمعايير - Codes & Standards",
            "short_introduction": "شرح عملي وتطبيقي لأهم بنود كود البناء السعودي الإنشائي والأحمال الزلزالية والرياح.",
            "description": "فهم منظومة الأكواد السعودية للمباني السكنية والتجارية، ومعايير السلامة، ومتطلبات كفاءة الطاقة والاشتراطات البلدية.",
            "published": 1,
            "is_featured": 1,
            "difficulty_level": "Beginner / مبتدئ",
            "course_language": "Arabic / عربي",
            "paid_course": 0,
            "course_price": 0,
            "currency": "SAR",
            "preview_video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        },
        {
            "title": "احتراف برامج ETABS & SAFE في النمذجة والتحليل الإنشائي",
            "category": "التدريب على البرمجيات - Software Training",
            "short_introduction": "تطبيق عملي خطوة بخطوة لنمذجة برج سكني وتحليله ضد أحمال الزلازل والرياح باستخدام ETABS و SAFE.",
            "description": "إتقان النمذجة ثلاثية الأبعاد، واستخراج العزوم والقوى، وتصميم العناصر الخرسانية وبلاطات الهوردي والـ Flat Slab وتصدير المخططات.",
            "published": 1,
            "is_featured": 1,
            "difficulty_level": "Intermediate / متوسط",
            "course_language": "Arabic / عربي",
            "paid_course": 1,
            "course_price": 550,
            "currency": "SAR",
            "preview_video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        },
        {
            "title": "حصر الكميات وإعداد جداول المواصفات والأسعار (BOQ)",
            "category": "حصر الكميات - Quantity Surveying",
            "short_introduction": "طرق حصر كميات الحفر والخرسانات والحديد والتشطيبات باحترافية واستخدام شيتات الإكسل الهندسية.",
            "description": "دورة تطبيقية من المخططات المعمارية والإنشائية حتى تسليم مستخلصات التنفيذ والمستخلص الختامي للمشروع.",
            "published": 1,
            "is_featured": 1,
            "difficulty_level": "Beginner / مبتدئ",
            "course_language": "Arabic / عربي",
            "paid_course": 1,
            "course_price": 350,
            "currency": "SAR",
            "preview_video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        },
    ]

    for data in courses_data:
        if not frappe.db.exists("LMS Course", {"title": data["title"]}):
            doc = frappe.get_doc({
                "doctype": "LMS Course",
                "instructors": [{"instructor": "Administrator"}],
                **data
            })
            doc.insert(ignore_permissions=True)
            print(f"  📚 Created Course: {data['title']}")
        else:
            print(f"  ✓ Course exists: {data['title']}")

    frappe.db.commit()
    print("✅ All courses seeded successfully!")
