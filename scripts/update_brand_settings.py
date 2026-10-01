import frappe
from frappe.utils import now

def run():
    frappe.init(site='lms.localhost', sites_path='/home/frappe/frappe-bench/sites')
    frappe.connect()

    assets = [
        ("handastech-logo.png", "/assets/builders/images/handastech-logo.png"),
        ("handastech-icon.png", "/assets/builders/images/handastech-icon.png"),
        ("handastech-horizontal.png", "/assets/builders/images/handastech-horizontal.png"),
        ("favicon.png", "/assets/builders/images/favicon.png"),
    ]

    for fname, furl in assets:
        if not frappe.db.exists("File", {"file_url": furl}):
            import uuid
            docname = str(uuid.uuid4())[:10]
            frappe.db.sql("""
                INSERT INTO `tabFile` 
                (name, file_name, file_url, is_private, creation, modified, modified_by, owner, docstatus)
                VALUES (%s, %s, %s, 0, %s, %s, 'Administrator', 'Administrator', 0)
            """, (docname, fname, furl, now(), now()))
            print(f"✓ Inserted tabFile row for {fname}")
        else:
            print(f"✓ File exists in tabFile: {fname}")

    # 1. Update Website Settings
    frappe.db.set_single_value('Website Settings', 'app_name', 'Handastech')
    frappe.db.set_single_value('Website Settings', 'banner_image', '/assets/builders/images/handastech-logo.png')
    frappe.db.set_single_value('Website Settings', 'app_logo', '/assets/builders/images/handastech-logo.png')
    frappe.db.set_single_value('Website Settings', 'footer_logo', '/assets/builders/images/handastech-logo.png')
    frappe.db.set_single_value('Website Settings', 'favicon', '/assets/builders/images/favicon.png')
    frappe.db.set_single_value('Website Settings', 'brand_html', '<img src="/assets/builders/images/handastech-horizontal.png" alt="Handastech" style="height: 38px;">')
    frappe.db.set_single_value('Website Settings', 'copyright', '© 2026 Handastech. جميع الحقوق محفوظة')

    # 2. Update System Settings
    frappe.db.set_single_value('System Settings', 'app_name', 'Handastech')

    # 3. Update LMS Settings if exists
    if frappe.db.exists('DocType', 'LMS Settings'):
        try:
            frappe.db.set_single_value('LMS Settings', 'app_name', 'Handastech')
            frappe.db.set_single_value('LMS Settings', 'banner_image', '/assets/builders/images/handastech-logo.png')
            print("✓ Updated LMS Settings")
        except Exception as e:
            print("Note on LMS Settings:", e)

    frappe.db.commit()
    frappe.clear_cache()
    print("✅ Handastech brand settings & file records successfully committed!")

if __name__ == '__main__':
    run()
