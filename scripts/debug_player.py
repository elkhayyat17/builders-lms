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
options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

driver = webdriver.Chrome(options=options)

try:
    safe_print("1. Logging in...")
    driver.get("http://localhost:8000/login")
    time.sleep(2)
    driver.find_element(By.ID, "login_email").send_keys("student@builders.sa")
    driver.find_element(By.ID, "login_password").send_keys("Student2026!")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)

    safe_print("2. Opening lesson 1-1...")
    driver.get("http://localhost:8000/lms/courses/sbc-304/learn/1-1")
    time.sleep(4)

    safe_print("\n=== BROWSER CONSOLE LOGS ===")
    logs = driver.get_log("browser")
    for entry in logs:
        safe_print(f"[{entry['level']}] {entry['message']}")

    safe_print("\n=== DOM & VIDEO STATE ===")
    videos = driver.find_elements(By.TAG_NAME, "video")
    safe_print(f"Video elements count: {len(videos)}")
    if videos:
        v = videos[0]
        safe_print(f"video src: {v.get_attribute('src')}")
        safe_print(f"video currentSrc: {v.get_attribute('currentSrc')}")
        safe_print(f"video readyState: {driver.execute_script('return arguments[0].readyState;', v)}")
        safe_print(f"video error: {driver.execute_script('return arguments[0].error ? arguments[0].error.code + \" \" + arguments[0].error.message : null;', v)}")
        safe_print(f"video paused: {driver.execute_script('return arguments[0].paused;', v)}")
        safe_print(f"video dimensions: {driver.execute_script('return arguments[0].videoWidth + \"x\" + arguments[0].videoHeight;', v)}")

    safe_print("\n=== OVERLAYS & WRAPPERS IN DOM ===")
    safe_print(f"Privacy Shields: {len(driver.find_elements(By.ID, 'ht-screen-capture-shield'))}")
    safe_print(f"Stream Locks: {len(driver.find_elements(By.ID, 'ht-stream-lock-shield'))}")
    tamper_alerts = driver.find_elements(By.XPATH, "//*[contains(@class, 'bg-red-600/20')]")
    safe_print(f"Tamper alert icons: {len(tamper_alerts)}")

    # Check play button
    play_btns = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Play video']")
    safe_print(f"Play overlay button count: {len(play_btns)}")
    if play_btns:
        safe_print(f"Play button displayed: {play_btns[0].is_displayed()}")

    # Check HLS state in window
    hls_state = driver.execute_script("""
        return {
            hlsSupported: typeof window.Hls !== 'undefined' ? window.Hls.isSupported() : 'No Hls.js',
            videoWrapperHTML: document.querySelector('.ht-video-wrapper') ? document.querySelector('.ht-video-wrapper').outerHTML.substring(0, 500) : 'None'
        };
    """)
    safe_print(f"HLS state: {hls_state}")

    # Take a screenshot to inspect visual rendering
    driver.save_screenshot("scripts/debug_player_screenshot.png")
    safe_print("Screenshot saved to scripts/debug_player_screenshot.png")

finally:
    driver.quit()
