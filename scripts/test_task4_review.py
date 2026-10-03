import re
import sys

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

with open(r'builders/builders/locale/ar.po', encoding='utf-8') as f:
    content = f.read()

# Parse msgid and msgstr (handling potential multiline)
pattern = re.compile(r'msgid\s+"((?:\\.|[^"\\])*)"\s*\nmsgstr\s+"((?:\\.|[^"\\])*)"', re.MULTILINE)
entries = dict(pattern.findall(content))

print(f"Total parsed entries in ar.po: {len(entries)}")

missing = []
mismatches = []
for k, exp in brief_reqs.items():
    if k not in entries:
        missing.append(k)
    elif entries[k] != exp:
        mismatches.append((k, exp, entries[k]))

print(f"Checked brief requirements count: {len(brief_reqs)}")
print(f"Missing in ar.po: {len(missing)}")
if missing:
    print("Missing:", missing)
print(f"Mismatches: {len(mismatches)}")
if mismatches:
    for m in mismatches:
        print(f"  Key: {m[0]}\n  Expected: {m[1]}\n  Actual:   {m[2]}")

if not missing and not mismatches:
    print("ALL_BRIEF_TRANSLATIONS_EXACT_MATCH")
