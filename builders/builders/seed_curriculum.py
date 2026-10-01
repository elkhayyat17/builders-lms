import frappe

def seed_curriculum():
    """Seed comprehensive chapters and lessons for civil engineering courses."""
    curriculum_data = [
        {
            "course": "sbc-304",
            "chapters": [
                {
                    "title": "الفصل الأول: مقدمة في كود البناء السعودي SBC 304 والأحمال التصميمية",
                    "lessons": [
                        {
                            "title": "الدرس 1.1: نظرة عامة على فلسفة التصميم ومعاملات الأمان في SBC 304",
                            "youtube": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                            "include_in_preview": 1,
                            "body": """### مقدمة في فلسفة التصميم الإنشائي طبقاً لكود SBC 304

يهدف كود البناء السعودي للخرسانة المسلحة **SBC 304** إلى ضمان سلامة وديمومة المنشآت تحت مختلف حالات التحميل.

#### 1. تركيبات الأحمال التصميمية (Load Combinations):
وفقاً لاشتراطات الكود السعودي، يتم تصميم العناصر الإنشائية على الحمل الأقصى الأرجح حدوثه:
- **الحالة الأساسية للأحمال الميتة والحية:**
  $$U = 1.2 D + 1.6 L$$
- **الحالة المتضمنة أحمال الرياح:**
  $$U = 1.2 D + 1.0 L + 1.0 W$$
- **الحالة المتضمنة أحمال الزلازل (SBC 301 / 304):**
  $$U = 1.2 D + 1.0 L + 1.0 E$$

#### 2. معاملات تخفيض المقاومة (Strength Reduction Factors - $\\phi$):
- قطاعات الانحناء المحكومة بالشد (Tension-controlled): $\\phi = 0.90$
- قطاعات الضغط (أعمدة ذات كانات منفصلة): $\\phi = 0.65$
- قطاعات الضغط (أعمدة حلزونية Spiral): $\\phi = 0.75$
- القص والالتواء (Shear and Torsion): $\\phi = 0.75$

> **ملاحظة للمهندس الإنشائي:** يجب التأكد دائماً من مطابقة رتبة الخرسانة $f'_c$ ومقاومة خضوع الحديد $f_y$ للمخططات المعتمدة من الهيئة السعودية للمهندسين."""
                        },
                        {
                            "title": "الدرس 1.2: اشتراطات الديمومة والغطاء الخرساني في البيئة الخليجية",
                            "youtube": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                            "include_in_preview": 0,
                            "body": """### اعتبارات الديمومة في بيئة الخليج العربي

نظراً لارتفاع درجات الحرارة والرطوبة ووجود أملاح الكلوريدات والكبريتات في التربة والمياه الجوفية، وضع كود SBC 304 اشتراطات صارمة:

#### 1. الحد الأدنى للغطاء الخرساني (Concrete Cover):
- الخرسانة المصبوبة في الموقع والملامسة للتربة بشكل دائم (الأساسات): **75 مم**.
- الخرسانة المعرضة للعوامل الجوية أو الملامسة للتربة (أعمدة وكمرات): **50 مم**.
- الخرسانة غير المعرضة للعوامل الجوية (بلاطات داخلية): **20 مم**.
- كمرات وأعمدة داخلية: **40 مم**.

#### 2. متطلبات رتبة الخرسانة ونسبة الماء إلى الإسمنت (w/c ratio):
- للأساسات المعرضة لأملاح الكبريتات الشديدة (S2, S3): أقصى نسبة $w/c = 0.40$ مع استخدام أسمنت مقاوم للكبريتات (Type V)."""
                        }
                    ]
                },
                {
                    "title": "الفصل الثاني: تصميم الكمرات الخرسانية لمقاومة قوى الانحناء والقص",
                    "lessons": [
                        {
                            "title": "الدرس 2.1: تحليل وتصميم مقاطع الانحناء Singly & Doubly Reinforced",
                            "youtube": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                            "include_in_preview": 0,
                            "body": """### تصميم قطاعات الكمرات لمقاومة عزوم الانحناء $M_u$

معادلة عزم المقاومة الاسمي للقطاع مستطيل التسليح الأحادي:
$$M_n = A_s f_y \\left( d - \\frac{a}{2} \\right)$$

حيث أن عمق بلوك الإجهاد المكافئ لوتني:
$$a = \\frac{A_s f_y}{0.85 f'_c b}$$

ويجب دائماً التحقق من أن نسبة التسليح تقع بين الحد الأدنى $\\rho_{min}$ والحد الأقصى $\\rho_{max}$ لضمان انهيار لدن تحذيري (Ductile Failure)."""
                        },
                        {
                            "title": "الدرس 2.2: تصميم تسليح القص والكانات وتفاصيل التفريد الإنشائي",
                            "youtube": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                            "include_in_preview": 0,
                            "body": """### تصميم تسليح القص (Shear Design)

مقاومة القص التصميمية للقطاع:
$$\\phi V_n = \\phi (V_c + V_s) \\ge V_u$$

مقاومة الخرسانة للقص بدون كانات:
$$V_c = 0.17 \\lambda \\sqrt{f'_c} b_w d$$

في حال كانت $V_u > \\phi V_c$، يتم حساب حديد الكانات $A_v / s$:
$$\\frac{A_v}{s} = \\frac{V_u - \\phi V_c}{\\phi f_{yt} d}$$"""
                        }
                    ]
                }
            ]
        },
        {
            "course": "fidic",
            "chapters": [
                {
                    "title": "الفصل الأول: البنية التعاقدية لعقود الفيديك FIDIC في مشاريع البنية التحتية",
                    "lessons": [
                        {
                            "title": "الدرس 1.1: التزامات وحقوق المقاول والمهندس وصاحب العمل",
                            "youtube": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                            "include_in_preview": 1,
                            "body": """### البنية التعاقدية طبقاً لعقد الفيديك (الكتاب الأحمر)

يعتبر نموذج فيديك 1999 و 2017 المعيار الأبرز لتنظيم عقود الإنشاءات المدنية في منطقة الخليج:
1. **صاحب العمل (Employer - Clause 2):** تسليم الموقع، التمويل، وإصدار شهادات الدفع.
2. **المهندس (The Engineer - Clause 3):** الإشراف الفني، إصدار التعليمات، وإجراء التقييمات الحيادية العادلة (Fair Determination).
3. **المقاول (The Contractor - Clause 4):** تنفيذ الأعمال بموجب المواصفات وإجراءات السلامة وتقديم خطابات الضمان البنكية."""
                        },
                        {
                            "title": "الدرس 1.2: إدارة المطالبات الزمنية والمالية وفق المادة 20 (Claims Procedure)",
                            "youtube": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                            "include_in_preview": 0,
                            "body": """### إجراءات المطالبات العقدية (Clause 20.1)

- **إخطار المطالبة (Notice of Claim):** يجب على المقاول إرسال إخطار كتابي خلال **28 يوماً** من تاريخ علمه بالحدث.
- **التفاصيل الداعمة المعاصرة (Contemporary Records):** تدوين سجلات التنفيذ اليومية وحالة الطقس ودفاتر الحضور.
- **تقديم التقرير المفصل (Detailed Claim):** خلال **42 يوماً** يتضمن التحليل الزمني (Time Impact Analysis)."""
                        }
                    ]
                }
            ]
        },
        {
            "course": "etabs-safe",
            "chapters": [
                {
                    "title": "الفصل الأول: نمذجة الأبراج والمباني السكنية ببرنامج ETABS",
                    "lessons": [
                        {
                            "title": "الدرس 1.1: إعداد الشبكة المحورية ونمذجة الأعمدة وجدران القص",
                            "youtube": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                            "include_in_preview": 1,
                            "body": """### خطوات النمذجة المتقدمة في ETABS 2024

1. استيراد المخططات المعمارية بنسق DXF لضبط أماكن الأعمدة وجدران القص (Shear Walls).
2. تعريف القطاعات الخرسانية وتحديد معاملات تشقق القطاعات (Cracked Section Modifiers):
   - الأعمدة: $I_{eff} = 0.70 I_g$
   - الكمرات: $I_{eff} = 0.35 I_g$
   - البلاطات: $I_{eff} = 0.25 I_g$
   - جدران القص غير المتشققة: $I_{eff} = 0.70 I_g$"""
                        }
                    ]
                }
            ]
        }
    ]

    for c_data in curriculum_data:
        course_name = c_data["course"]
        if not frappe.db.exists("LMS Course", course_name):
            print(f"Course {course_name} not found, skipping...")
            continue

        course_doc = frappe.get_doc("LMS Course", course_name)
        
        # Check if chapters already exist for this course
        existing_chapters = frappe.get_all("Course Chapter", filters={"course": course_name})
        if existing_chapters:
            print(f"Chapters already exist for {course_name} ({len(existing_chapters)} chapters), skipping...")
            continue

        chapter_records = []
        for ch_idx, ch in enumerate(c_data["chapters"], start=1):
            chapter_doc = frappe.get_doc({
                "doctype": "Course Chapter",
                "title": ch["title"],
                "course": course_name,
            })
            chapter_doc.insert(ignore_permissions=True)
            print(f"  + Created Chapter: {ch['title']}")
            chapter_records.append((chapter_doc.name, ch_idx))

            # Add lessons
            for ls_idx, ls in enumerate(ch["lessons"], start=1):
                lesson_doc = frappe.get_doc({
                    "doctype": "Course Lesson",
                    "title": ls["title"],
                    "chapter": chapter_doc.name,
                    "course": course_name,
                    "body": ls.get("body", ""),
                    "youtube": ls.get("youtube", ""),
                    "include_in_preview": ls.get("include_in_preview", 0),
                })
                lesson_doc.insert(ignore_permissions=True)
                print(f"    * Created Lesson: {ls['title']}")

                # Append to chapter lessons child table
                chapter_doc.append("lessons", {
                    "lesson": lesson_doc.name,
                    "idx": ls_idx,
                })

            chapter_doc.save(ignore_permissions=True)

        # Fresh fetch course doc and append chapters
        course_doc = frappe.get_doc("LMS Course", course_name)
        for chap_name, c_idx in chapter_records:
            course_doc.append("chapters", {
                "chapter": chap_name,
                "idx": c_idx
            })
        course_doc.save(ignore_permissions=True)
        print(f"Completed curriculum for {course_name}")

    frappe.db.commit()
    print("All curriculum seeded successfully!")

if __name__ == "__main__":
    seed_curriculum()
