import os
import re
import sys
import frappe
from frappe.translate import get_all_translations

frappe.init("lms.localhost")
frappe.connect()
frappe.cache.delete_key("merged_translations")

tr = get_all_translations("ar")

brief_reqs = {
    'Theater Mode': 'الوضع المسرحي',
    'Standard Mode': 'الوضع القياسي',
    'Zen Mode': 'وضع التركيز (Zen)',
    'Outline': 'المحتوى',
    'Notes': 'الملاحظات',
    'Q&A': 'الأسئلة',
    'Resources': 'المرفقات',
    'Pinned': 'ملاحظات مثبتة',
    'Pin note': 'تثبيت الملاحظة',
    'Export': 'تصدير الملاحظات',
    'Export formatted printable notes': 'تصدير الملاحظات بصيغة قابلة للطباعة',
    'Add note at {0}': 'إضافة ملاحظة عند {0}',
    'Add a note': 'إضافة ملاحظة',
    'Video paused': 'تم إيقاف الفيديو مؤقتاً',
    'Write your note here... (Press Ctrl+Enter to save)': 'اكتب ملاحظتك هنا... (اضغط Ctrl+Enter للحفظ)',
    'Back to Questions': 'العودة للأسئلة',
    'Refresh replies': 'تحديث الردود',
    'No answers yet. Be the first to help!': 'لا توجد إجابات بعد. كن أول من يشارك بالحل!',
    'Link to current video timestamp': 'ربط السؤال بتوقيت الفيديو الحالي',
    'Ask a Question': 'طرح استفسار جديد',
    'Question Title': 'عنوان السؤال',
    'Question Details': 'تفاصيل السؤال',
    'Post Question': 'نشر السؤال',
    'Post Answer': 'إرسال الرد',
    'Question posted successfully': 'تم نشر السؤال بنجاح',
    'Reply posted successfully': 'تم نشر الرد بنجاح',
    'Search Q&A': 'ابحث في أسئلة الدرس...',
    'With Timestamps': 'مرتبطة بالفيديو',
    'No questions yet for this lesson. Have a question about this lecture? Ask below!': 'لا توجد أسئلة بعد لهذا الدرس. هل لديك استفسار حول هذه المحاضرة؟ اطرحه الآن!',
    'Ask a question': 'طرح سؤال',
    'Search files...': 'ابحث في المرفقات...',
    'CAD Drawing': 'مخطط أوتوكاد إنشائي',
    'Calculation Sheet': 'شيت حسابات وتصميم',
    'Engineering Code': 'كود ومواصفات هندسية',
    'Project Bundle': 'حزمة ملفات المشروع',
    'Attachment': 'ملف مرفق',
    'Download': 'تحميل',
    'All': 'الكل',
    'Search lessons...': 'ابحث في الفصول والدروس...',
    'Clear search': 'مسح البحث',
    'Lessons': 'دروس',
    'Lesson': 'درس',
    'Chapter completed': 'الفصل مكتمل بالكامل',
    'Locked': 'مغلق - أكمل الدروس السابقة',
    'Completed': 'تم إكمال هذا الدرس',
    'Certified Engineering Content': 'محتوى هندسي معتمد',
    'SBC Compliant': 'مطابق لكود البناء السعودي',
    'Design Equations (SBC 304 / ACI 318)': 'المعادلات التصميمية المعتمدة (SBC 304 / ACI 318)',
    'LaTeX Math': 'معادلات رياضية (LaTeX)',
    'Instructor Notes': 'ملاحظات المدرب',
    'SBC 304 - Sec. 5.3.1 (Load Combo)': 'كود SBC 304 - بند 5.3.1 (تركيبات الأحمال)',
    'Tension-controlled': 'قطاع محكوم بالشد',
    'My Profile': 'ملفي الشخصي',
    'Settings': 'الإعدادات',
    'Theme': 'المظهر',
    'Language': 'اللغة',
    'Arabic': 'العربية',
    'English': 'الإنجليزية',
    'Log out': 'تسجيل الخروج',
    'Log in': 'تسجيل الدخول',
    'Clear Demo Data': 'مسح البيانات التجريبية',
    'Auto': 'تلقائي',
    'Play video': 'تشغيل الفيديو',
    'Pause': 'إيقاف مؤقت',
    'Play': 'تشغيل',
    'Mute': 'كتم الصوت',
    'Unmute': 'تشغيل الصوت',
    'Toggle fullscreen': 'ملء الشاشة',
    'Seek': 'تقديم / تأخير',
    'Playback Speed': 'سرعة التشغيل',
    'Time for a Quiz': 'حان وقت الاختبار السريع',
    'quiz': 'اختبار',
    'quizzes': 'اختبارات',
    'second': 'ثانية',
    'seconds': 'ثواني',
    'Yellow': 'أصفر',
    'Blue': 'أزرق',
    'Green': 'أخضر',
    'Purple': 'بنفسجي',
    'Red': 'أحمر',
    'Total Notes': 'إجمالي الملاحظات',
    'Pinned Notes': 'الملاحظات المثبتة',
    'Learner': 'المتدرب',
    'Generated': 'تاريخ الاستخراج'
}

missing = []
mismatches = []
for k, exp in brief_reqs.items():
    act = tr.get(k)
    if not act:
        missing.append(k)
    elif act != exp:
        mismatches.append((k, exp, act))

print(f"Total live translations loaded: {len(tr)}")
print(f"Live checked brief requirements: {len(brief_reqs)}")
print(f"Live missing in runtime: {len(missing)}")
if missing:
    print("Missing:", missing)
print(f"Live mismatches in runtime: {len(mismatches)}")
if mismatches:
    for m in mismatches:
        print(f"  Key: {m[0]}\n  Expected: {m[1]}\n  Actual:   {m[2]}")

# Check MO file existence and timestamp
mo_path = "/home/frappe/frappe-bench/sites/assets/locale/ar/LC_MESSAGES/builders.mo"
if os.path.exists(mo_path):
    print(f"MO file found at {mo_path}, size: {os.path.getsize(mo_path)} bytes")
else:
    print(f"MO file NOT found at {mo_path}")

frappe.destroy()

if not missing and not mismatches and os.path.exists(mo_path):
    print("ALL_LIVE_TRANSLATIONS_AND_MO_VERIFIED")
