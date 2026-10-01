import frappe

def create_demo_users():
    """Create test / demo accounts for Student, Instructor, and Manager."""
    demo_users = [
        {
            "email": "student@builders.sa",
            "first_name": "م. أحمد",
            "last_name": "الشمري",
            "username": "ahmed_civil",
            "password": "Student2026!",
            "roles": ["All"],
            "bio": "مهندس مدني متدرب - مهتم بالتصميم الإنشائي وكود البناء السعودي SBC.",
            "user_type": "Website User",
            "enroll_courses": ["sbc-304", "boq"]
        },
        {
            "email": "instructor@builders.sa",
            "first_name": "د. م. خالد",
            "last_name": "العتيبي",
            "username": "dr_khaled",
            "password": "Instructor2026!",
            "roles": ["Course Creator", "Instructor", "Batch Evaluator", "Desk User"],
            "bio": "استشاري تصميم المنشآت الخرسانية وإدارة المشاريع - أكثر من 15 عاماً من الخبرة في المشاريع الخليجية وكود SBC.",
            "user_type": "System User",
            "instruct_courses": ["sbc-304", "fidic", "etabs-safe"]
        },
        {
            "email": "manager@builders.sa",
            "first_name": "م. فهد",
            "last_name": "القحطاني",
            "username": "fahad_manager",
            "password": "Manager2026!",
            "roles": ["System Manager", "Course Creator", "Moderator", "Desk User"],
            "bio": "مدير العمليات الأكاديمية والمنصة التعليمية - بيلدرز للتعليم الهندسي.",
            "user_type": "System User",
        }
    ]

    for u in demo_users:
        email = u["email"]
        if not frappe.db.exists("User", email):
            user = frappe.new_doc("User")
            user.email = email
            user.first_name = u["first_name"]
            user.last_name = u["last_name"]
            user.username = u["username"]
            user.new_password = u["password"]
            user.user_type = u.get("user_type", "Website User")
            user.bio = u.get("bio", "")
            user.send_welcome_email = 0
            user.insert(ignore_permissions=True)
            print(f"✅ Created User: {email} ({u['first_name']} {u['last_name']})")
        else:
            user = frappe.get_doc("User", email)
            user.first_name = u["first_name"]
            user.last_name = u["last_name"]
            user.new_password = u["password"]
            user.bio = u.get("bio", "")
            user.save(ignore_permissions=True)
            print(f"✓ Updated User: {email}")

        # Assign Roles
        current_roles = frappe.get_roles(email)
        all_system_roles = [r.name for r in frappe.get_all("Role")]
        roles_to_add = [r for r in u.get("roles", []) if r in all_system_roles and r not in current_roles]
        if roles_to_add:
            user.add_roles(*roles_to_add)
            print(f"  + Added roles: {roles_to_add} to {email}")

        # Enroll in courses if applicable
        for course in u.get("enroll_courses", []):
            if frappe.db.exists("LMS Course", course):
                if not frappe.db.exists("LMS Enrollment", {"course": course, "member": email}):
                    enrollment = frappe.new_doc("LMS Enrollment")
                    enrollment.course = course
                    enrollment.member = email
                    enrollment.member_type = "Student"
                    enrollment.insert(ignore_permissions=True)
                    print(f"  + Enrolled {email} in course {course}")

        # Add as Instructor to courses if applicable
        for course in u.get("instruct_courses", []):
            if frappe.db.exists("LMS Course", course):
                course_doc = frappe.get_doc("LMS Course", course)
                instructors = [i.instructor for i in course_doc.instructors]
                if email not in instructors:
                    course_doc.append("instructors", {"instructor": email})
                    course_doc.save(ignore_permissions=True)
                    print(f"  + Assigned {email} as instructor for course {course}")

    frappe.db.commit()
    print("\n🎉 All Demo Accounts Created & Configured Successfully!")

if __name__ == "__main__":
    create_demo_users()
