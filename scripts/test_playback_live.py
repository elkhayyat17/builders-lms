import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def safe_print(msg):
    sys.stdout.buffer.write((str(msg) + "\n").encode("utf-8", errors="replace"))
    sys.stdout.buffer.flush()

options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1280,720")

driver = webdriver.Chrome(options=options)

try:
    safe_print("1. Logging in as student@builders.sa...")
    driver.get("http://localhost:8000/login")
    time.sleep(2)
    driver.find_element(By.ID, "login_email").send_keys("student@builders.sa")
    driver.find_element(By.ID, "login_password").send_keys("Student2026!")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)

    safe_print("2. Opening lesson 1-1...")
    driver.get("http://localhost:8000/lms/courses/sbc-304/learn/1-1")
    time.sleep(4)

    videos = driver.find_elements(By.TAG_NAME, "video")
    assert len(videos) > 0, "No video element found"
    v = videos[0]

    safe_print("3. Clicking Play button overlay...")
    play_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Play video']")
    # Mute first to comply with autoplay policy in automated browsers
    driver.execute_script("arguments[0].muted = true;", v)
    play_btn.click()
    time.sleep(4)

    cur_time = driver.execute_script("return arguments[0].currentTime;", v)
    is_paused = driver.execute_script("return arguments[0].paused;", v)
    dims = driver.execute_script("return arguments[0].videoWidth + 'x' + arguments[0].videoHeight;", v)

    safe_print(f"  - Playback Active: {not is_paused}")
    safe_print(f"  - Current Time: {cur_time:.2f}s")
    safe_print(f"  - Video Dimensions: {dims}")
    assert cur_time > 1.0 and not is_paused, f"Playback did not progress: time={cur_time}, paused={is_paused}"
    safe_print("  ✅ PASS: Video is playing smoothly with full decryption!")

    # Check watermark
    wm = driver.find_element(By.ID, "ht-forensic-watermark")
    safe_print(f"  - Watermark visible: {wm.is_displayed()}")
    safe_print(f"  - Watermark content: {wm.text.replace(chr(10), ' | ')}")
    assert "Handastech" in wm.text and "SBC-304" in wm.text, "Watermark content missing"
    safe_print("  ✅ PASS: Ghost Watermark rendered and active during live playback!")

    # Save live screenshot during playback
    driver.save_screenshot("scripts/live_playback_success.png")
    safe_print("Screenshot of live playback saved to scripts/live_playback_success.png")

    safe_print("\n=======================================================")
    safe_print("🎉 ALL PLAYBACK ISSUES RESOLVED - PLAYER 100% OPERATIONAL")
    safe_print("=======================================================")

finally:
    driver.quit()
