import frappe

def run():
    frappe.init(site="localhost", sites_path="/home/frappe/frappe-bench/sites")
    frappe.connect()

    meta = frappe.get_meta("LMS Lesson Note")
    has_timestamp = meta.has_field("video_timestamp")
    has_formatted = meta.has_field("formatted_time")
    has_pinned = meta.has_field("is_pinned")

    print(f"video_timestamp: {has_timestamp}")
    print(f"formatted_time: {has_formatted}")
    print(f"is_pinned: {has_pinned}")

    assert has_timestamp and has_formatted and has_pinned, "Custom fields missing on LMS Lesson Note!"
    print("ALL_CUSTOM_FIELDS_VERIFIED")

if __name__ == "__main__":
    run()
