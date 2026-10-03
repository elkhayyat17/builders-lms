#!/usr/bin/env python3
"""Generate complete, high-standard Arabic translation catalog for Builders LMS.

This script ensures 100% Arabic coverage for all workspace keys used in:
  - lms/frontend/src/components/LessonWorkspace/
  - lms/frontend/src/pages/Lesson.vue
  - lms/frontend/src/components/VideoBlock.vue
  - lms/frontend/src/components/Sidebar/UserDropdown.vue
as well as comprehensive coverage for core LMS pages, courses, forms, and navigation.

Usage:
  python scripts/generate_complete_po.py
"""

import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "lms", "frontend", "src")
TARGET_PO = os.path.join(BASE_DIR, "builders", "builders", "locale", "ar.po")

PO_HEADER = """# Builders LMS — Arabic Translations
# Copyright (C) 2026 Builders Team
# This file is distributed under the MIT license.
#
msgid ""
msgstr ""
"Project-Id-Version: builders 0.0.1\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2026-10-03 12:00+0000\\n"
"PO-Revision-Date: 2026-10-03 12:00+0000\\n"
"Language: ar\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=6; plural=n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5;\\n"
"""

# Master translations dictionary (exact verbatim matches from specification & professional Gulf engineering vocabulary)
TRANSLATIONS = {
    # --- Task 4 Brief Required Keys (Verbatim) ---
    "Theater Mode": "الوضع المسرحي",
    "Standard Mode": "الوضع القياسي",
    "Zen Mode": "وضع التركيز (Zen)",
    "Outline": "المحتوى",
    "Notes": "الملاحظات",
    "Q&A": "الأسئلة",
    "Resources": "المرفقات",
    "Pinned": "ملاحظات مثبتة",
    "Pin note": "تثبيت الملاحظة",
    "Export": "تصدير الملاحظات",
    "Export formatted printable notes": "تصدير الملاحظات بصيغة قابلة للطباعة",
    "Add note at {0}": "إضافة ملاحظة عند {0}",
    "Add a note": "إضافة ملاحظة",
    "Video paused": "تم إيقاف الفيديو مؤقتاً",
    "Write your note here... (Press Ctrl+Enter to save)": "اكتب ملاحظتك هنا... (اضغط Ctrl+Enter للحفظ)",
    "Back to Questions": "العودة للأسئلة",
    "Refresh replies": "تحديث الردود",
    "No answers yet. Be the first to help!": "لا توجد إجابات بعد. كن أول من يشارك بالحل!",
    "Link to current video timestamp": "ربط السؤال بتوقيت الفيديو الحالي",
    "Ask a Question": "طرح استفسار جديد",
    "Question Title": "عنوان السؤال",
    "Question Details": "تفاصيل السؤال",
    "Post Question": "نشر السؤال",
    "Post Answer": "إرسال الرد",
    "Question posted successfully": "تم نشر السؤال بنجاح",
    "Reply posted successfully": "تم نشر الرد بنجاح",
    "Search Q&A": "ابحث في أسئلة الدرس...",
    "With Timestamps": "مرتبطة بالفيديو",
    "No questions yet for this lesson. Have a question about this lecture? Ask below!": "لا توجد أسئلة بعد لهذا الدرس. هل لديك استفسار حول هذه المحاضرة؟ اطرحه الآن!",
    "Ask a question": "طرح سؤال",
    "Search files...": "ابحث في المرفقات...",
    "CAD Drawing": "مخطط أوتوكاد إنشائي",
    "Calculation Sheet": "شيت حسابات وتصميم",
    "Engineering Code": "كود ومواصفات هندسية",
    "Project Bundle": "حزمة ملفات المشروع",
    "Attachment": "ملف مرفق",
    "Download": "تحميل",
    "All": "الكل",
    "Search lessons...": "ابحث في الفصول والدروس...",
    "Clear search": "مسح البحث",
    "Lessons": "دروس",
    "Lesson": "درس",
    "Chapter completed": "الفصل مكتمل بالكامل",
    "Locked": "مغلق - أكمل الدروس السابقة",
    "Completed": "تم إكمال هذا الدرس",
    "Certified Engineering Content": "محتوى هندسي معتمد",
    "SBC Compliant": "مطابق لكود البناء السعودي",
    "Design Equations (SBC 304 / ACI 318)": "المعادلات التصميمية المعتمدة (SBC 304 / ACI 318)",
    "LaTeX Math": "معادلات رياضية (LaTeX)",
    "Instructor Notes": "ملاحظات المدرب",
    "SBC 304 - Sec. 5.3.1 (Load Combo)": "كود SBC 304 - بند 5.3.1 (تركيبات الأحمال)",
    "Tension-controlled": "قطاع محكوم بالشد",
    "My Profile": "ملفي الشخصي",
    "Settings": "الإعدادات",
    "Theme": "المظهر",
    "Language": "اللغة",
    "Arabic": "العربية",
    "English": "الإنجليزية",
    "Log out": "تسجيل الخروج",
    "Log in": "تسجيل الدخول",
    "Clear Demo Data": "مسح البيانات التجريبية",
    "Auto": "تلقائي",
    "Play video": "تشغيل الفيديو",
    "Pause": "إيقاف مؤقت",
    "Play": "تشغيل",
    "Mute": "كتم الصوت",
    "Unmute": "تشغيل الصوت",
    "Toggle fullscreen": "ملء الشاشة",
    "Seek": "تقديم / تأخير",
    "Playback Speed": "سرعة التشغيل",
    "Time for a Quiz": "حان وقت الاختبار السريع",
    "quiz": "اختبار",
    "quizzes": "اختبارات",
    "second": "ثانية",
    "seconds": "ثواني",
    "Yellow": "أصفر",
    "Blue": "أزرق",
    "Green": "أخضر",
    "Purple": "بنفسجي",
    "Red": "أحمر",
    "Total Notes": "إجمالي الملاحظات",
    "Pinned Notes": "الملاحظات المثبتة",
    "Learner": "المتدرب",
    "Generated": "تاريخ الاستخراج",

    # --- Additional Lesson Workspace Keys ---
    "Add note at": "إضافة ملاحظة عند",
    "Apps": "التطبيقات",
    "Are you sure you want to clear the demo data? This would delete the course \"A guide  to Frappe Learning\" along with all its associated data. This action cannot be undone.": "هل أنت متأكد من رغبتك في مسح البيانات التجريبية؟ سيؤدي ذلك إلى حذف دورة \"دليل التعلم\" مع كافة بياناتها المرتبطة. لا يمكن التراجع عن هذا الإجراء.",
    "Are you sure you want to delete this note? This action cannot be undone.": "هل أنت متأكد من رغبتك في حذف هذه الملاحظة؟ لا يمكن التراجع عن هذا الإجراء.",
    "Are you sure you want to login to your Frappe Cloud dashboard?": "هل أنت متأكد من رغبتك في تسجيل الدخول إلى لوحة تحكم Frappe Cloud؟",
    "Ask a question to get help from the community.": "اطرح سؤالاً للحصول على مساعدة من المجتمع الهندسي.",
    "AutoCAD (DWG), Excel (XLSX), and engineering notes will appear here when added by the instructor.": "ستظهر ملفات أوتوكاد (DWG) وإكسل (XLSX) والملاحظات الهندسية هنا عند إضافتها من قبل المدرب.",
    "Builders LMS Engineering Course Watching & Smart Notes": "منصة بيلدرز التعليمية - متابعة المحاضرات الهندسية والملاحظات الذكية",
    "CAD / DWG": "أوتوكاد / CAD",
    "Cancel": "إلغاء",
    "Capture key formulas, diagrams, or questions synchronized with video timestamps. Press \"N\" anytime while watching to pause and take a note.": "سجّل المعادلات والمخططات والأسئلة متزامنة مع توقيت الفيديو بدقة. اضغط \"N\" في أي وقت أثناء المشاهدة لإيقاف الفيديو وتدوين الملاحظة.",
    "Captured time:": "الوقت المسجل:",
    "Chapters": "الفصول",
    "Collapse all chapters": "طي جميع الفصول",
    "Collapse sidebar": "طي الشريط الجانبي",
    "Community": "المجتمع",
    "Complete the upcoming quiz to continue watching the video. The quiz will open in {0} {1}.": "أكمل الاختبار القصير القادم لمواصلة مشاهدة الفيديو. سيفتح الاختبار بعد {0} {1}.",
    "Configuration": "التهيئة",
    "Confirm": "تأكيد",
    "Confirm clearing demo data?": "تأكيد مسح البيانات التجريبية؟",
    "Contact the Administrator to enroll for this course.": "تواصل مع إدارة المنصة للتسجيل في هذه الدورة.",
    "Copied!": "تم النسخ!",
    "Copy": "نسخ",
    "Copy equation": "نسخ المعادلة",
    "Copy file link": "نسخ رابط الملف",
    "Copy link": "نسخ الرابط",
    "Course Progress": "نسبة إنجاز الدورة",
    "Course reference": "مرجع الدورة",
    "Courses": "الدورات",
    "Create first note": "إنشاء أول ملاحظة",
    "Current": "الحالي",
    "Dark": "داكن",
    "Delete": "حذف",
    "Delete Note": "حذف الملاحظة",
    "Delete note": "حذف الملاحظة",
    "Demo data cleared successfully": "تم مسح البيانات التجريبية بنجاح",
    "Desk": "لوحة التحكم (Desk)",
    "Discussions are currently disabled by the instructor for this course.": "المناقشات معطلة حالياً من قبل المدرب لهذه الدورة.",
    "Discussions are disabled for this course": "المناقشات معطلة لهذه الدورة",
    "Downloading": "جاري التحميل",
    "Edit note": "تعديل الملاحظة",
    "Editor View": "عرض المحرر",
    "Equation copied to clipboard": "تم نسخ المعادلة إلى الحافظة بنجاح",
    "Excel / XLSX": "إكسل / XLSX",
    "Expand all chapters": "توسيع جميع الفصول",
    "Expand sidebar": "توسيع الشريط الجانبي",
    "Explain your question or formula in detail...": "اشرح سؤالك أو المعادلة الهندسية بالتفصيل...",
    "Failed to delete note": "تعذر حذف الملاحظة",
    "Failed to post question": "تعذر نشر السؤال",
    "Failed to post reply": "تعذر نشر الرد",
    "Failed to save note": "تعذر حفظ الملاحظة",
    "Failed to update note": "تعذر تحديث الملاحظة",
    "File link copied to clipboard": "تم نسخ رابط الملف إلى الحافظة",
    "Flexural Design Strength:": "مقاومة الانحناء التصميمية (ΦMn):",
    "Import": "استيراد",
    "Insert current video timestamp into reply": "إدراج التوقيت الحالي للفيديو في الرد",
    "Its content is stored in a form we cannot read. Reload the page, and tell your instructor if it keeps happening.": "المحتوى محفوظ بصيغة غير قابلة للعرض حالياً. حدّث الصفحة وأبلغ المدرب في حال استمرار المشكلة.",
    "Jump video to this timestamp": "الانتقال بالفيديو إلى هذا التوقيت",
    "Jump video to timestamp": "الانتقال بالفيديو إلى التوقيت",
    "Keyboard shortcut": "اختصار لوحة المفاتيح",
    "Lesson attachment": "مرفق الدرس",
    "Lesson workspace tabs": "تبويبات مساحة عمل الدرس",
    "Light": "فاتح",
    "Load combination equations and ultimate flexural strength requirements": "معادلات تراكيب الأحمال واشتراطات مقاومة الانحناء القصوى",
    "Loading curriculum...": "جاري تحميل المنهج الدراسي...",
    "Loading notes...": "جاري تحميل الملاحظات...",
    "Loading questions...": "جاري تحميل الأسئلة والردود...",
    "Loading replies...": "جاري تحميل الردود...",
    "Loading resources...": "جاري تحميل المرفقات الهندسية...",
    "Login": "تسجيل الدخول",
    "Login to Frappe Cloud": "تسجيل الدخول إلى Frappe Cloud",
    "Login to Frappe Cloud?": "تسجيل الدخول إلى Frappe Cloud؟",
    "Next lesson": "الدرس التالي",
    "No attachments for this lesson": "لا توجد مرفقات لهذا الدرس",
    "No curriculum available": "لا يتوفر منهج دراسي",
    "No curriculum outline available for this course yet.": "لا يتوفر مخطط للمنهج الدراسي لهذه الدورة بعد.",
    "No downloadable resources or attachments for this lesson.": "لا توجد ملفات أو مخططات مرفقة لهذا الدرس.",
    "No files found matching": "لم يتم العثور على ملفات مطابقة",
    "No lessons found": "لم يتم العثور على دروس",
    "No lessons matching": "لا توجد دروس مطابقة للبحث",
    "No matching files found": "لم يتم العثور على ملفات مطابقة",
    "No matching questions found": "لم يتم العثور على أسئلة مطابقة للبحث",
    "No notes available to export": "لا توجد ملاحظات مسجلة للتصدير",
    "No notes in this lesson yet": "لا توجد ملاحظات مدونة في هذا الدرس بعد",
    "No notes match your filter": "لا توجد ملاحظات مطابقة لمعايير التصفية",
    "No questions found matching": "لا توجد أسئلة مطابقة",
    "No questions yet": "لا توجد أسئلة بعد",
    "Note deleted successfully": "تم حذف الملاحظة بنجاح",
    "Note saved successfully": "تم حفظ الملاحظة بنجاح",
    "Note updated successfully": "تم تحديث الملاحظة بنجاح",
    "PDF": "ملف PDF",
    "Pin note to top": "تثبيت الملاحظة في الأعلى",
    "Pin to top": "تثبيت في الأعلى",
    "Previous lesson": "الدرس السابق",
    "Questions": "الأسئلة والواجبات",
    "Refresh resources": "تحديث المرفقات",
    "Reinforcement Ratio:": "نسبة التسليح (ρ):",
    "Replies": "الردود",
    "Reply": "رد",
    "Reset filters": "إعادة ضبط التصفية",
    "Save": "حفظ",
    "Save note": "حفظ الملاحظة",
    "Search notes...": "ابحث في ملاحظاتك...",
    "Show all notes": "عرض جميع الملاحظات",
    "Show pinned notes only": "عرض الملاحظات المثبتة فقط",
    "Start Learning": "ابدأ التعلم الآن",
    "Student": "متدرب",
    "System": "النظام",
    "This lesson could not be displayed": "تعذر عرض محتوى هذا الدرس",
    "This lesson is locked": "هذا الدرس مغلق حالياً",
    "This lesson is not available for preview. Please enroll in the course to access it.": "هذا الدرس غير متاح للمعاينة المجانية. يُرجى التسجيل في الدورة للوصول إلى كافة المحاضرات.",
    "This video contains {0} {1}:": "يحتوي هذا الفيديو على {0} {1}:",
    "Toggle discussions": "إظهار / إخفاء المناقشات",
    "Try clearing your search query or pin filter.": "جرّب مسح نص البحث أو إلغاء فلتر التثبيت.",
    "Ultimate Load Combination:": "تراكيب الأحمال القصوى التصميمية:",
    "Unpin note": "إلغاء تثبيت الملاحظة",
    "Update": "تحديث",
    "Update timestamp to current video position": "تحديث التوقيت إلى موقع الفيديو الحالي",
    "Video failed to load. This lesson will still be marked complete after you spend some time on it.": "تعذر تحميل الفيديو. سيتم احتساب إكمال الدرس بعد قضاء الوقت المحدد.",
    "View discussion": "عرض المناقشة",
    "Write an answer...": "اكتب إجابتك هنا...",
    "Write your note...": "اكتب ملاحظتك هنا...",
    "ZIP / Archive": "أرشيف ملفات مضغوطة / ZIP",
    "at {0} minutes": "عند الدقيقة {0}",
    "completed": "مكتمل",
    "e.g. Question about shear reinforcement in beams...": "مثال: سؤال حول تسليح القص في الكمرات الخرسانية...",

    # --- Engineering Categories, Standards & Landing Page ---
    "Structural Engineering": "الهندسة الإنشائية",
    "Construction Management": "إدارة المشاريع الإنشائية",
    "Codes & Standards": "الأكواد والمعايير الهندسية",
    "Software Training": "التدريب الاحترافي على البرمجيات",
    "Quantity Surveying": "حصر الكميات والمواصفات",
    "Beginner": "مبتدئ",
    "Intermediate": "متوسط",
    "Advanced": "متقدم",
    "Bilingual": "ثنائي اللغة",
    "Build Your Civil Engineering Career": "ابنِ مسيرتك المهنية في الهندسة المدنية",
    "Browse Courses": "تصفح الدورات التدريبية",
    "Featured Courses": "الدورات المميزة",
    "All Categories": "جميع التخصصات",
    "View All Courses": "عرض جميع الدورات",
    "Prerequisites": "المتطلبات المسبقة",
    "Target Audience": "الفئة المستهدفة",
    "Difficulty Level": "مستوى الصعوبة",
    "Course Language": "لغة الدورة",
    "Enroll Now": "سجل في الدورة الآن",
    "Preview": "معاينة مجانية",
    "Course Outline": "المنهج الدراسي المعتمد",
    "About Instructor": "نبذة عن المدرب",
    "Home": "الرئيسية",
    "Contact Us": "تواصل معنا",
    "My Dashboard": "لوحة التحكم التعليمية",
    "Continue Learning": "متابعة مسار التعلم",
    "My Courses": "دوراتي المسجلة",
    "Start Quiz": "ابدأ الاختبار",
    "Submit Answers": "إرسال الإجابات",
    "Your Score": "الدرجة النهائية",
    "Correct": "إجابة صحيحة",
    "Incorrect": "إجابة خاطئة",
    "Try Again": "إعادة المحاولة",
    "Upcoming Live Classes": "المحاضرات المباشرة القادمة",
    "Join Class": "انضم للمحاضرة",
    "Discussion": "منتدى النقاش",
    "Post": "نشر",
    "Search": "بحث",
    "Filter": "تصفية",
    "Loading": "جاري التحميل",
    "No results found": "لا توجد نتائج مطابقة",
    "chapters": "فصول",
    "students": "متدربين",
    "Civil Engineering Courses": "دورات الهندسة المدنية",
    "Gulf & MENA Regional Standards • Saudi Building Code • FIDIC • PMP • BIM & Structural Design": "معايير الخليج والشرق الأوسط • كود البناء السعودي • فيديك • إدارة المشاريع • نمذجة معلومات البناء والتصميم الإنشائي",

    # --- Core LMS Platform & Management ---
    "Dashboard": "لوحة المؤشرات",
    "Profile": "الملف الشخصي",
    "Notifications": "الإشعارات",
    "Batch": "الدفعة التدريبية",
    "Batches": "الدفعات التدريبية",
    "Instructors": "هيئة التدريب",
    "Instructor": "المدرب",
    "Certificates": "الشهادات المعتمدة",
    "Certificate": "شهادة إتمام",
    "Enrollment": "التسجيل",
    "Enrollments": "سجلات التسجيل",
    "Assignments": "التكليفات والمشاريع",
    "Assignment": "تكليف هندسي",
    "Programs": "البرامج والدبلومات المهنية",
    "Program": "برنامج مهني",
    "Quizzes": "الاختبارات التقييمية",
    "Quiz": "اختبار تقييمي",
    "Assessments": "التقييمات الدورية",
    "Assessment": "تقييم مستوى",
    "Live Classes": "المحاضرات التفاعلية المباشرة",
    "Live Class": "محاضرة مباشرة",
    "Jobs": "فرص العمل الهندسية",
    "Job": "فرصة عمل",
    "Submit": "إرسال",
    "Submitted": "تم الإرسال",
    "Pending": "قيد المراجعة",
    "Approved": "معتمد ومقبول",
    "Rejected": "مرفوض",
    "Status": "الحالة",
    "Actions": "الإجراءات",
    "Action": "إجراء",
    "Create": "إنشاء جديد",
    "Edit": "تعديل",
    "View": "عرض التفاصيل",
    "Remove": "إزالة",
    "Close": "إغلاق",
    "Back": "رجوع",
    "Next": "التالي",
    "Previous": "السابق",
    "Finish": "إنهاء",
    "Done": "تم بنجاح",
    "Success": "تمت العملية بنجاح",
    "Error": "حدث خطأ",
    "Warning": "تنبيه هام",
    "Info": "معلومات إضافية",
    "Yes": "نعم",
    "No": "لا",
    "Description": "الوصف التفصيلي",
    "Title": "العنوان الرئيسي",
    "Name": "الاسم الكامل",
    "Email": "البريد الإلكتروني",
    "Password": "كلمة المرور",
    "Date": "التاريخ",
    "Time": "الوقت",
    "Duration": "المدة الزمنية",
    "Score": "الدرجة المستحقة",
    "Progress": "نسبة التقدم",
    "Summary": "الملخص التنفيذي",
    "Details": "التفاصيل",
    "General": "إعدادات عامة",
    "Members": "المشتركون",
    "Member": "مشترك",
    "Role": "الصلاحية / الدور",
    "Roles": "الأدوار والصلاحيات",
    "Active": "نشط حالياً",
    "Inactive": "غير نشط",
    "Free": "مجاني",
    "Paid": "مدفوع",
    "Price": "السعر",
    "Currency": "العملة",
    "SAR": "ريال سعودي",
    "USD": "دولار أمريكي",
    "Payment": "السداد والدفع",
    "Payments": "عمليات الدفع",
    "Checkout": "إتمام عملية الشراء",
    "Order": "طلب الشراء",
    "Orders": "طلبات الشراء",
    "Invoice": "فاتورة ضريبية",
    "Invoices": "الفواتير الضريبية",
    "Coupon": "كود الخصم",
    "Coupons": "أكواد الخصم",
    "Discount": "نسبة الخصم",
    "Total": "الإجمالي النهائي",
    "Subtotal": "المجموع الفرعي",
    "Tax": "ضريبة القيمة المضافة",
    "Overview": "نظرة عامة",
    "Reviews": "التقييمات والآراء",
    "Curriculum": "الخطة الدراسية",
    "Announcements": "الإعلانات والتحديثات",
    "Announcement": "إعلان هام",
    "Resources & Downloads": "المرفقات والتحميلات الهندسية",
    "Download Certificate": "تحميل الشهادة المعتمدة",
    "Verify Certificate": "التحقق من صحة الشهادة",
    "Share": "مشاركة",
    "Share on LinkedIn": "مشاركة على لينكد إن",
    "Copy Link": "نسخ الرابط",
    "Enroll in Course": "التسجيل في هذه الدورة",
    "Start Course": "بدء دراسة الدورة",
    "Resume Course": "استئناف دراسة الدورة",
    "Course Completed": "تم إكمال الدورة بنجاح",
    "Passing Score": "درجة النجاح المطلوبة",
    "Attempts": "المحاولات المتاحة",
    "Time Limit": "الوقت المحدد للاختبار",
    "Questions Count": "عدد الأسئلة",
    "Question": "سؤال",
    "Next Question": "السؤال التالي",
    "Previous Question": "السؤال السابق",
    "Review Answers": "مراجعة الإجابات قبل الإرسال",
    "Congratulations!": "تهانينا وألف مبروك!",
    "You have passed the quiz.": "لقد اجتزت هذا الاختبار بنجاح وتم تسجيل النتيجة.",
    "Unfortunately, you did not pass.": "للأسف، لم تحقق درجة النجاح المطلوبة في هذه المحاولة.",
    "Try Again": "إعادة المحاولة",
    "Back to Lesson": "العودة إلى الدرس",
    "Back to Course": "العودة إلى صفحة الدورة",
    "Mark as Completed": "تحديد الدرس كمكتمل",
    "Next Lesson": "الانتقال للدرس التالي",
    "Previous Lesson": "الانتقال للدرس السابق",
    "Course Content": "محتويات الدورة التدريبية",
    "Download All": "تحميل كافة المرفقات",
}

KEY_RE = re.compile(r"""__\(\s*(['"`])((?:\\.|(?!\1).)*?)\1\s*[\),]""", re.S)
ARABIC_RE = re.compile(r"[\u0600-\u06FF]")

WORKSPACE_PATTERNS = [
    "LessonWorkspace",
    "Lesson.vue",
    "VideoBlock.vue",
    "UserDropdown.vue",
]


def extract_workspace_keys():
    """Extract all English translation keys from the workspace Vue components."""
    ws_keys = {}
    for root, _dirs, files in os.walk(FRONTEND_DIR):
        if "node_modules" in root or "/tests" in root:
            continue
        for f in files:
            if not f.endswith((".vue", ".js", ".ts")):
                continue
            path = os.path.join(root, f).replace("\\", "/")
            if not any(wp in path for wp in WORKSPACE_PATTERNS):
                continue
            with open(path, encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
            for m in KEY_RE.finditer(text):
                k = m.group(2)
                if m.group(1) == "`" and "${" in k:
                    continue
                k = k.replace("\\'", "'").replace('\\"', '"')
                if not ARABIC_RE.search(k) and re.search(r"[A-Za-z]", k):
                    ws_keys.setdefault(k, set()).add(path)
    return ws_keys


def escape_po(s: str) -> str:
    """Properly escape a string for a PO msgid or msgstr entry."""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def generate_po():
    ws_keys = extract_workspace_keys()
    print(f"Scanned workspace: found {len(ws_keys)} distinct English keys.")

    # Check for missing workspace keys in our master dictionary
    missing_ws = [k for k in ws_keys if k not in TRANSLATIONS]
    if missing_ws:
        print(f"ERROR: {len(missing_ws)} workspace keys are missing translations in master dictionary:")
        for k in sorted(missing_ws):
            print(f"  - {k!r}")
        sys.exit(1)

    print(f"SUCCESS: 100% of {len(ws_keys)} workspace keys are covered in the catalog!")

    # Sort entries: Brief keys first, then alphabetical
    entries = []
    for msgid, msgstr in sorted(TRANSLATIONS.items()):
        escaped_id = escape_po(msgid)
        escaped_str = escape_po(msgstr)
        entry = f'msgid "{escaped_id}"\nmsgstr "{escaped_str}"\n'
        entries.append(entry)

    po_content = PO_HEADER + "\n" + "\n".join(entries) + "\n"

    with open(TARGET_PO, "w", encoding="utf-8") as f:
        f.write(po_content)

    print(f"Wrote {len(TRANSLATIONS)} translation entries to {TARGET_PO}.")


if __name__ == "__main__":
    generate_po()
