"""
Task 5 Verification Script: RTL/LTR Direction, Typography & Formula Immunity
Verifies all CSS files contain exact requirements from task-5-brief.md and
that live HTTP endpoints serve updated assets.
"""

import os
import sys
import re
import requests

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LMS_BUILDERS_CSS = os.path.join(BASE_DIR, "lms", "frontend", "src", "styles", "builders.css")
BUILDERS_THEME_CSS = os.path.join(BASE_DIR, "builders", "builders", "public", "css", "builders-theme.css")
BUILDERS_RTL_CSS = os.path.join(BASE_DIR, "builders", "builders", "public", "css", "builders-rtl.css")

passed_checks = 0
total_checks = 0

def check(name, condition, details=""):
    global passed_checks, total_checks
    total_checks += 1
    if condition:
        passed_checks += 1
        print(f" [PASS] {name} {details}")
    else:
        print(f" [FAIL] {name} {details}")

print("=" * 70)
print("Verifying Task 5: Flawless RTL/LTR Direction, Typography & Formula Immunity")
print("=" * 70)

# 1. Inspect lms/frontend/src/styles/builders.css
print("\n--- 1. Testing lms/frontend/src/styles/builders.css ---")
with open(LMS_BUILDERS_CSS, "r", encoding="utf-8") as f:
    builders_css = f.read()

check("builders.css: RTL font family", "'IBM Plex Sans Arabic'" in builders_css)
check("builders.css: RTL line-height 1.6", "line-height: 1.6" in builders_css)
check("builders.css: LTR font family", "'IBM Plex Sans'" in builders_css)
check("builders.css: LTR line-height 1.5", "line-height: 1.5" in builders_css)
check("builders.css: Chevron mirror transform: scaleX(-1)", "transform: scaleX(-1)" in builders_css)
check("builders.css: LTR formula immunity (engineering-formula)", ".engineering-formula" in builders_css)
check("builders.css: LTR timestamp immunity (timestamp-pill)", ".timestamp-pill" in builders_css)
check("builders.css: LTR time-display immunity", ".time-display" in builders_css)
check("builders.css: Katex LTR immunity", ".katex" in builders_css and ".katex-display" in builders_css)
check("builders.css: unicode-bidi: isolate !important", "unicode-bidi: isolate !important" in builders_css)
check("builders.css: Logical reply-indent (margin-inline-start)", "margin-inline-start" in builders_css)
check("builders.css: Logical card-accent-strip", ".card-accent-strip" in builders_css and "border-inline-start" in builders_css)
check("builders.css: RTL reply-indent padding 0.75rem", "padding-right: 0.75rem" in builders_css)

# 2. Inspect builders/builders/public/css/builders-theme.css
print("\n--- 2. Testing builders/builders/public/css/builders-theme.css ---")
with open(BUILDERS_THEME_CSS, "r", encoding="utf-8") as f:
    theme_css = f.read()

check("theme.css: RTL font family", "'IBM Plex Sans Arabic'" in theme_css)
check("theme.css: RTL line-height 1.6", "line-height: 1.6" in theme_css)
check("theme.css: LTR font family", "'IBM Plex Sans'" in theme_css)
check("theme.css: LTR line-height 1.5", "line-height: 1.5" in theme_css)
check("theme.css: Chevron mirror transform: scaleX(-1)", "transform: scaleX(-1)" in theme_css)
check("theme.css: LTR formula immunity (.engineering-formula)", ".engineering-formula" in theme_css)
check("theme.css: LTR timestamp immunity (.timestamp-pill)", ".timestamp-pill" in theme_css)
check("theme.css: unicode-bidi: isolate !important", "unicode-bidi: isolate !important" in theme_css)
check("theme.css: Logical properties (.reply-indent)", "margin-inline-start" in theme_css)
check("theme.css: Logical card-accent-strip", ".card-accent-strip" in theme_css)

# 3. Inspect builders/builders/public/css/builders-rtl.css
print("\n--- 3. Testing builders/builders/public/css/builders-rtl.css ---")
with open(BUILDERS_RTL_CSS, "r", encoding="utf-8") as f:
    rtl_css = f.read()

check("rtl.css: RTL font family", "'IBM Plex Sans Arabic'" in rtl_css)
check("rtl.css: RTL line-height 1.6", "line-height: 1.6" in rtl_css)
check("rtl.css: Chevron mirror transform: scaleX(-1)", "transform: scaleX(-1)" in rtl_css)
check("rtl.css: lucide-chevron-right mirrored", ".lucide-chevron-right" in rtl_css)
check("rtl.css: LTR formula immunity (.engineering-formula)", ".engineering-formula" in rtl_css)
check("rtl.css: LTR timestamp immunity (.timestamp-pill)", ".timestamp-pill" in rtl_css)
check("rtl.css: unicode-bidi: isolate !important", "unicode-bidi: isolate !important" in rtl_css)
check("rtl.css: Logical properties (.reply-indent)", "margin-inline-start" in rtl_css)
check("rtl.css: Logical card-accent-strip", ".card-accent-strip" in rtl_css)
check("rtl.css: RTL reply-indent padding 0.75rem", "padding-right: 0.75rem" in rtl_css)

# 4. Test live HTTP assets on port 8000
print("\n--- 4. Testing Live HTTP Assets (Port 8000) ---")
try:
    r_theme = requests.get("http://localhost:8000/assets/builders/css/builders-theme.css", timeout=5)
    check("HTTP 200 builders-theme.css", r_theme.status_code == 200)
    check("HTTP served theme.css has formula immunity", ".engineering-formula" in r_theme.text)
    check("HTTP served theme.css has unicode-bidi isolate", "unicode-bidi: isolate !important" in r_theme.text)
except Exception as e:
    check("HTTP builders-theme.css fetch", False, str(e))

try:
    r_rtl = requests.get("http://localhost:8000/assets/builders/css/builders-rtl.css", timeout=5)
    check("HTTP 200 builders-rtl.css", r_rtl.status_code == 200)
    check("HTTP served rtl.css has formula immunity", ".engineering-formula" in r_rtl.text)
    check("HTTP served rtl.css has chevron mirroring", "transform: scaleX(-1)" in r_rtl.text)
except Exception as e:
    check("HTTP builders-rtl.css fetch", False, str(e))

print("\n" + "=" * 70)
print(f"Results: {passed_checks}/{total_checks} checks passed.")
if passed_checks == total_checks:
    print("ALL_TASK5_RTL_TESTS_PASSED")
    sys.exit(0)
else:
    print("SOME_CHECKS_FAILED")
    sys.exit(1)
