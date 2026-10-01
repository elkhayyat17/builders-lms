import frappe

def run():
    frappe.init(site='lms.localhost', sites_path='/home/frappe/frappe-bench/sites')
    frappe.connect()

    RAW_TABLE = "tabVideo Security Key"
    
    # Check if sbc-304-1-1 exists
    row = frappe.db.sql(f"SELECT * FROM `{RAW_TABLE}` WHERE video_id = 'sbc-304-1-1'", as_dict=True)
    if row:
        r = row[0]
        # Also ensure 'playlist' row exists with same key and iv
        exists_playlist = frappe.db.sql(f"SELECT name FROM `{RAW_TABLE}` WHERE video_id = 'playlist'")
        if not exists_playlist:
            frappe.db.sql(f"""
                INSERT INTO `{RAW_TABLE}` (name, video_id, course, lesson, key_hex, iv_hex, creation, modified, modified_by, owner)
                VALUES ('playlist-key', 'playlist', %s, %s, %s, %s, NOW(), NOW(), 'Administrator', 'Administrator')
            """, (r.get('course'), r.get('lesson'), r.get('key_hex'), r.get('iv_hex')))
            print("✓ Inserted alias key row for 'playlist'")
        else:
            print("✓ 'playlist' alias key already exists")
        frappe.db.commit()
    else:
        print("❌ sbc-304-1-1 row not found")

if __name__ == '__main__':
    run()
