# Builders LMS (منصة بيلدرز للهندسة المدنية)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Frappe: v15](https://img.shields.io/badge/Frappe-v15-blue.svg)](https://frappeframework.com/)
[![Docker: Ready](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://docker.com)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

> **The Gulf Region's Specialized Learning Management System for Civil Engineers**  
> **المنصة الأولى المتخصصة في تدريب وتأهيل المهندسين المدنيين في المملكة العربية السعودية والخليج العربي**

---

## 🏗️ Project Overview (نظرة عامة)

**Builders LMS** is a specialized, production-ready enterprise learning management system tailored for the civil engineering industry in Saudi Arabia and the GCC. Built on top of **Frappe Framework v15** and **Frappe LMS**, extended with the custom **Builders App** (`builders`), the platform delivers:

- 🏛️ **Full Civil Engineering Taxonomy**: 5 core departments (Structural, Construction Management, Codes & Standards, Software Modeling, Quantity Surveying).
- 🌐 **Arabic-First Localization**: Native Right-to-Left (RTL) experience with dynamic English/Arabic switching.
- 🔐 **Zero-Cost Anti-Piracy Video Protection**: Transcoding via FFmpeg HLS AES-128, Frappe token-gated key delivery, memory-blob playback, and dynamic forensic watermarking with DOM tamper-proofing.
- ⚡ **Production Architecture**: Containerized multi-service deployment with MariaDB 10.8, Redis Cache, Redis Queue, Frappe Bench, and Nginx reverse proxy with SSL automation.

---

## 📂 Directory Layout (هيكل المشروع)

```text
LMS civil/
├── builders/               # Custom Frappe App (Civil models, fixtures, branding, APIs)
│   ├── builders/           # Python modules, hooks, custom utilities
│   │   ├── fixtures/       # LMS category seed data
│   │   ├── public/         # Arabic font stylesheets, RTL CSS, language toggle JS
│   │   ├── utils.py        # Frappe whitelisted APIs (email status, secure keys)
│   │   └── seed_curriculum.py # Automated curriculum & lesson generator
│   └── setup.py            # Frappe app setup
├── lms/                    # Customized Frappe LMS upstream application
│   ├── docker/             # Container init scripts and self-healing UI patches
│   ├── frontend/           # Vue 3 / Vite SPA frontend
│   └── lms/                # Core LMS Python backend doctypes
├── nginx/                  # Production Nginx reverse proxy & SSL config
│   ├── conf.d/             # Virtual host configuration (rate limiting, caching)
│   └── ssl/                # TLS/SSL certificates
├── scripts/                # Maintenance, seeding, and automated test suite
│   ├── test_all_screens.py # 36-point full E2E automated testing suite
│   ├── test_enrollment.py  # Live enrollment verification script
│   ├── configure_email.py  # SMTP email configuration helper
│   └── seed_courses.py     # Database seeding runner
├── docs/                   # Documentation and executive presentations
│   └── presentation/       # Builders interactive executive deck & showcase
├── docker-compose.prod.yml # Production multi-container orchestration
├── .env.production.example # Production environment configuration template
├── deploy.sh               # One-click server deployment script
├── README.md               # Project documentation
└── .gitignore              # Git ignore rules (includes .worktrees/)
```

---

## 🚀 Quick Start (التشغيل السريع)

### 1. Requirements
- Docker & Docker Compose v2+
- Python 3.10+
- Git

### 2. Local Development (Docker)
```bash
# Clone the repository
git clone https://github.com/elkhayyat17/builders-lms.git
cd builders-lms

# Start the services
docker compose -f docker-compose.prod.yml up -d

# Verify services health
docker ps
```

The platform will be live at:
- **LMS Portal**: [http://localhost:8000/lms](http://localhost:8000/lms)
- **Frappe Desk**: [http://localhost:8000/app](http://localhost:8000/app)

---

## 👥 Verified Test Accounts (حسابات الاختبار)

| الدور (Role) | البريد الإلكتروني (Email) | كلمة المرور (Password) | الصلاحيات والوصول |
|---|---|---|---|
| **Student** | `student@builders.sa` | `Student2026!` | تصفح الدورات، التسجيل الفوري، مشاهدة الدروس، حل الاختبارات |
| **Instructor** | `instructor@builders.sa` | `Instructor2026!` | إدارة محتوى الدورات الإنشائية، رفع الفيديوهات، متابعة الطلاب |
| **Manager** | `manager@builders.sa` | `Manager2026!` | لوحة تحكم Desk، تقارير الإيرادات، إدارة الاشتراكات، الصلاحيات |
| **Administrator** | `Administrator` | `admin` | الوصول الكامل للنظام وإعدادات السيرفر والمكتبات |

---

## 🧪 Automated Testing Suite (الاختبارات المؤتمتة)

Run the full end-to-end verification covering all 22 screens, REST APIs, static assets, and SPA routes:

```bash
# Run comprehensive 36-point test suite
python scripts/test_all_screens.py

# Verify live course enrollment
python scripts/test_enrollment.py
```

---

## 🔒 Security Architecture (الحماية ومكافحة القرصنة)

Builders LMS includes an in-house anti-piracy video pipeline:
1. **FFmpeg AES-128 HLS Transcoding**: Videos are fragmented into `.ts` chunks encrypted with 128-bit AES keys.
2. **Frappe Dynamic Token Verification**: Decryption keys are NEVER stored publicly; fetched via authenticated whitelisted Frappe API with short-lived session tokens.
3. **In-Memory Blob Playback**: HLS manifest decrypted and bound to video player in memory via `hls.js` without exposing source video links.
4. **Anti-Tamper Forensic Watermark**: Floating translucent watermark displaying student name, email, IP, and timestamp with active `MutationObserver` preventing DOM deletion.

---

## 📄 License
This project is licensed under the MIT License.
