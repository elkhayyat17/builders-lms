import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1280,720")
options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

driver = webdriver.Chrome(options=options)

def safe_print(msg):
    sys.stdout.buffer.write((str(msg) + "\n").encode("utf-8", errors="replace"))
    sys.stdout.buffer.flush()

try:
    safe_print("======================================================================")
    safe_print("🛡️  STAGE 1 VERIFICATION: CLIENT & BROWSER SECURITY DEFENSE SUITE")
    safe_print("======================================================================")
    
    # 1. Login
    safe_print("\n[Step 1/5] Logging in as student@builders.sa...")
    driver.get("http://localhost:8000/login")
    time.sleep(2)
    usr = driver.find_element(By.ID, "login_email")
    pwd = driver.find_element(By.ID, "login_password")
    btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    usr.send_keys("student@builders.sa")
    pwd.send_keys("Student2026!")
    btn.click()
    time.sleep(3)
    
    # 2. Open Lesson
    safe_print("[Step 2/5] Navigating to lesson player...")
    driver.get("http://localhost:8000/lms/courses/sbc-304/learn/1-1")
    time.sleep(3)
    
    # Start video
    videos = driver.find_elements(By.TAG_NAME, "video")
    assert len(videos) > 0, "Video element not found"
    driver.execute_script("arguments[0].play();", videos[0])
    time.sleep(1)
    
    # 3. Test Keyboard Shortcuts & DevTools Deterrence
    safe_print("\n[Step 3/5] Testing DevTools keyboard shortcuts interception...")
    f12_blocked = driver.execute_script("""
        const e = new KeyboardEvent('keydown', { key: 'F12', keyCode: 123, cancelable: true });
        window.dispatchEvent(e);
        return e.defaultPrevented;
    """)
    safe_print(f"  - F12 Blocked: {f12_blocked}")
    
    inspect_blocked = driver.execute_script("""
        const e = new KeyboardEvent('keydown', { key: 'I', ctrlKey: true, shiftKey: true, cancelable: true });
        window.dispatchEvent(e);
        return e.defaultPrevented;
    """)
    safe_print(f"  - Ctrl+Shift+I Blocked: {inspect_blocked}")
    
    view_source_blocked = driver.execute_script("""
        const e = new KeyboardEvent('keydown', { key: 'u', ctrlKey: true, cancelable: true });
        window.dispatchEvent(e);
        return e.defaultPrevented;
    """)
    safe_print(f"  - Ctrl+U Blocked: {view_source_blocked}")
    
    assert f12_blocked and inspect_blocked and view_source_blocked, "Shortcut deterrence failed"
    safe_print("  ✅ PASS: All developer shortcut keys intercepted and cancelled.")
    
    # 4. Test Window Blur / Screen Capture Shield
    safe_print("\n[Step 4/5] Simulating Screen Capture Tool / Window Blur event...")
    driver.execute_script("window.dispatchEvent(new Event('blur'));")
    time.sleep(1)
    
    shields = driver.find_elements(By.ID, "ht-screen-capture-shield")
    is_paused = driver.execute_script("return arguments[0].paused;", videos[0])
    safe_print(f"  - Privacy Shield Element in DOM: {len(shields) > 0}")
    safe_print(f"  - Video Paused on Capture/Blur: {is_paused}")
    assert len(shields) > 0 and is_paused, "Screen capture privacy shield did not trigger on blur"
    safe_print("  ✅ PASS: Video paused and privacy blur shield successfully covered the screen.")
    
    # 5. Test Focus / Resume
    safe_print("\n[Step 5/5] Simulating User Return / Window Focus event...")
    driver.execute_script("window.dispatchEvent(new Event('focus'));")
    time.sleep(1)
    
    shields_after_focus = driver.find_elements(By.ID, "ht-screen-capture-shield")
    safe_print(f"  - Privacy Shield Dismissed: {len(shields_after_focus) == 0}")
    assert len(shields_after_focus) == 0, "Privacy shield was not dismissed after focus"
    safe_print("  ✅ PASS: Normal playback resumed smoothly upon return.")
    
    safe_print("\n======================================================================")
    safe_print("🏆 STAGE 1 VERIFICATION RESULT: 100% SUCCESS (ALL TESTS PASSED)")
    safe_print("======================================================================")

finally:
    driver.quit()
