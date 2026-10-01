import frappe

def run():
    frappe.init(site='lms.localhost', sites_path='/home/frappe/frappe-bench/sites')
    frappe.connect()

    lesson_name = '0002 الدرس 1.1: نظرة عامة على فلسفة التصميم ومعاملات الأمان في SBC 304'
    if not frappe.db.exists('Course Lesson', lesson_name):
        # find matching lesson by title or course
        matches = frappe.get_all('Course Lesson', filters={'course': 'sbc-304', 'title': ['like', '%1.1%']}, fields=['name', 'title'])
        if matches:
            lesson_name = matches[0].name
        else:
            print("❌ Could not find Lesson 1.1 in sbc-304")
            return

    doc = frappe.get_doc('Course Lesson', lesson_name)
    print(f"Found lesson: {doc.name}")
    print(f"Previous youtube: {doc.youtube}")

    # Remove youtube URL so it uses VideoBlock instead of YouTube iframe
    doc.youtube = ""

    # Check if {{ Video('/assets/builders/protected-stream/playlist.m3u8') }} is already in body
    macro_tag = "{{ Video('/assets/builders/protected-stream/playlist.m3u8') }}"
    current_body = doc.body or ""

    if macro_tag not in current_body:
        # Prepend video tag at top of lesson
        doc.body = f"{macro_tag}\n\n{current_body}".strip()
    
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    print("✅ Lesson 1.1 updated with protected HLS video stream macro!")
    print("New body starts with:", doc.body[:80])

if __name__ == '__main__':
    run()
