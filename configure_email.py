import frappe
import sys

def setup_email_account(
    email_id="noreply@builders.sa",
    password="",
    smtp_server="smtp.sendgrid.net",
    smtp_port=587,
    use_tls=1,
    login="",
    service=""
):
    """Set up the default outgoing Email Account in Frappe."""
    frappe.init(site="lms.localhost", sites_path="/home/frappe/frappe-bench/sites")
    frappe.connect()

    account_name = "Builders Notifications"
    
    if frappe.db.exists("Email Account", account_name):
        doc = frappe.get_doc("Email Account", account_name)
    elif frappe.db.exists("Email Account", {"email_id": email_id}):
        doc = frappe.get_doc("Email Account", {"email_id": email_id})
    else:
        doc = frappe.new_doc("Email Account")
        doc.email_account_name = account_name

    doc.email_id = email_id
    doc.enable_outgoing = 1
    doc.default_outgoing = 1
    doc.smtp_server = smtp_server
    doc.smtp_port = smtp_port
    doc.use_tls = use_tls
    doc.login = login or email_id
    if password:
        doc.password = password
    if service:
        doc.service = service

    doc.save(ignore_permissions=True)
    frappe.db.commit()
    print(f"✅ Email Account '{doc.name}' ({doc.email_id}) configured successfully as default outgoing!")

def send_test_email(recipient):
    """Send a real test email through the configured outgoing account."""
    frappe.init(site="lms.localhost", sites_path="/home/frappe/frappe-bench/sites")
    frappe.connect()

    subject = "Builders LMS - تجربة نظام إرسال الإيميلات"
    message = """
    <div dir="rtl" style="font-family: Arial, sans-serif; padding: 20px; color: #1B4D7A;">
        <h2>مرحباً بك في منصة بيلدرز (Builders LMS)</h2>
        <p>هذا إيميل تجريبي يؤكد أن نظام إرسال الإيميلات في المنصة يعمل بكفاءة وجاهز لبيئة الإنتاج.</p>
        <hr style="border: none; border-top: 1px solid #D4A843; margin: 20px 0;">
        <p style="color: #666; font-size: 13px;">تم الإرسال آلياً من محرك Frappe LMS لمنصة الهندسة المدنية.</p>
    </div>
    """
    
    frappe.sendmail(
        recipients=[recipient],
        subject=subject,
        message=message,
        now=True
    )
    print(f"✅ Test email successfully dispatched to: {recipient}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "send":
        recipient = sys.argv[2] if len(sys.argv) > 2 else "test@builders.sa"
        send_test_email(recipient)
    else:
        print("Usage:")
        print("  python configure_email.py setup <email> <password> <smtp_server> <port>")
        print("  python configure_email.py send <recipient>")
