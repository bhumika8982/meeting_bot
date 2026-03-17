import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchWindowException
from .recorder import MeetingRecorder
from .processor import process_meeting_data

def join_zoom_meeting(meeting_id, passcode=None):
    meeting_id = str(meeting_id).replace(" ", "")
    recorder = MeetingRecorder(meeting_id)
    
    chrome_options = Options()
    chrome_options.add_argument("--incognito") 
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    prefs = {"profile.default_content_setting_values": {"media_stream_mic": 2, "media_stream_camera": 2}}
    chrome_options.add_experimental_option("prefs", prefs)

    service = Service(executable_path='./bot/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(f"https://zoom.us/wc/{meeting_id}/join")
        wait = WebDriverWait(driver, 30)

        name_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#inputname")))
        name_input.send_keys("Meeting Assistant")

        if passcode:
            try: driver.find_element(By.CSS_SELECTOR, "input#inputpasscode").send_keys(passcode)
            except: pass

        join_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.preview-join-button")))
        driver.execute_script("arguments[0].click();", join_btn)

        # Start Capture
        try:
            audio_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.join-audio-by-voip__join-btn")))
            audio_btn.click()
            recorder.start()
            
            time.sleep(5) # Mute bot mic
            mute_btn = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'mute')]")
            if "unmute" not in mute_btn.get_attribute("aria-label").lower():
                driver.execute_script("arguments[0].click();", mute_btn)
        except: pass

        # Stay Alive Loop
        time.sleep(60)
        while True:
            time.sleep(20)
            try:
                _ = driver.window_handles 
                if "post_meeting" in driver.current_url: break
                p_count = int(driver.find_element(By.CLASS_NAME, "footer-button__number-counter").text)
                if p_count <= 1: break
            except: break

    finally:
        audio_path = recorder.stop()
        driver.quit()
        process_meeting_data(audio_path, meeting_id) # Final AI Process