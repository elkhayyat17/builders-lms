import frappe

def seed_civil_courses():
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
                **data
            })
            doc.insert(ignore_permissions=True)
            print(f"Created Course: {data['title']}")
        else:
            print(f"Course already exists: {data['title']}")

    frappe.db.commit()
    print("All courses seeded successfully!")

if __name__ == "__main__":
    frappe.init(site="lms.localhost", sites_path="/home/frappe/frappe-bench/sites")
    frappe.connect()
    seed_civil_courses()
