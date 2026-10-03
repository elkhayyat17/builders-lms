import os
import sys
import frappe
from frappe.translate import get_all_translations
import frappe.client

def test_translation_engine():
    site = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "lms.localhost"
    os.chdir("/home/frappe/frappe-bench/sites")
    frappe.init(site=site)
    frappe.connect()

    print(f"[TEST] Connected to site: {site}")

    # 1. Test get_all_translations("ar") returns non-empty dict
    frappe.cache.delete_key("merged_translations")
    tr_ar = get_all_translations("ar")
    print(f"[TEST] Total Arabic translations loaded: {len(tr_ar)}")
    assert isinstance(tr_ar, dict), "Translations must be a dictionary"
    assert len(tr_ar) > 0, "Arabic translations catalog is empty!"

    # 2. Test user language persistence and get_translations endpoint
    test_user = "Administrator"
    original_lang = frappe.db.get_value("User", test_user, "language")
    print(f"[TEST] Initial user language for {test_user}: {original_lang}")

    try:
        # Simulate frontend call: frappe.client.set_value(doctype='User', name=test_user, fieldname='language', value='ar')
        frappe.set_user("Administrator")
        frappe.client.set_value(doctype="User", name=test_user, fieldname="language", value="ar")
        frappe.db.commit()

        # Verify persisted in database
        updated_lang = frappe.db.get_value("User", test_user, "language")
        assert updated_lang == "ar", f"Expected language 'ar', got '{updated_lang}'"
        print(f"[TEST] User language updated to 'ar' verified.")

        # Test lms.lms.api.get_translations() for this user
        from lms.lms.api import get_translations
        user_translations = get_translations()
        assert isinstance(user_translations, dict), "get_translations() must return a dict"
        assert len(user_translations) > 0, "get_translations() returned empty dict for language 'ar'"
        print(f"[TEST] get_translations() returned {len(user_translations)} keys for user language 'ar'.")

        # Test switching to 'en'
        frappe.client.set_value(doctype="User", name=test_user, fieldname="language", value="en")
        frappe.db.commit()
        en_lang = frappe.db.get_value("User", test_user, "language")
        assert en_lang == "en", f"Expected language 'en', got '{en_lang}'"
        print(f"[TEST] User language switched to 'en' verified.")

    finally:
        # Restore original language
        frappe.client.set_value(doctype="User", name=test_user, fieldname="language", value=original_lang or "")
        frappe.db.commit()
        print(f"[TEST] Restored user language to {original_lang}.")

    print("ALL_TRANSLATION_ENGINE_TESTS_PASSED")

if __name__ == "__main__":
    test_translation_engine()
