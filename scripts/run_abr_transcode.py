import frappe
from builders.video_transcoder import transcode_video

def execute():
    res = transcode_video(
        file_path="/workspace/lms/frontend/public/Upload.mp4",
        video_id="sbc-304-1-1",
        course="sbc-304",
        lesson="1-1",
        delete_original=False,
        multi_bitrate=True
    )
    print("SUCCESS_ABR_TRANSCODE:", res)
    return res

if __name__ == "__main__":
    frappe.init(site="lms.localhost")
    frappe.connect()
    execute()
