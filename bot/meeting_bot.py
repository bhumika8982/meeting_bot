import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .recorder import start_recording, stop_recording
from .processor import process_meeting_data

def join_zoom_meeting(meeting_id, passcode):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    recordings_dir = os.path.join(base_dir, 'recordings')
    
    if not os.path.exists(recordings_dir):
        os.makedirs(recordings_dir, exist_ok=True)
        
    audio_path = os.path.join(recordings_dir, f"meeting_{meeting_id}.wav")
    
    chrome_options = Options()
    
    prefs = {
        "profile.default_content_setting_values.media_stream_mic": 2,
        "profile.default_content_setting_values.media_stream_camera": 2,
        "profile.default_content_setting_values.notifications": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 45)

    try:
        print(f"[*] Navigating to Zoom Meeting: {meeting_id}")
        driver.get(f"https://app.zoom.us/wc/join/{meeting_id}")
        
        try:
            name_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='inputname'], #inputname")))
            name_input.send_keys("Meeting Assistant (AI Bot)")
            print("[+] Bot name entered.")
        except:
            print("[!] Name input field not found.")

        if passcode:
            try:
                pass_input = driver.find_element(By.CSS_SELECTOR, "input[name='inputpasscode'], #inputpasscode")
                pass_input.send_keys(passcode)
                print("[+] Passcode entered.")
            except:
                pass

        join_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.preview-join-button, .zm-btn")))
        join_btn.click()
        print("[+] Join button clicked.")

        try:
            time.sleep(5)
            mute_btn = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'mute')]")
            if mute_btn:
                mute_btn[0].click()
                print("[+] UI Mute confirmed.")
        except:
            pass

        start_recording(audio_path)
        print("[*] Recording started. Monitoring meeting...")

        while True:
            time.sleep(10)
            if len(driver.window_handles) == 0:
                print("[*] Window closed. Ending session.")
                break
            
            ended_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'ended') or contains(text(), 'left')]")
            if ended_elements:
                print("[*] Meeting ended by host. Bot leaving.")
                break

    except Exception as e:
        print(f"[-] Critical Error: {e}")
        
    finally:
        try:
            print("[*] Stopping recording and saving file...")
            stop_recording(audio_path)
            
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 1024:
                print(f"[+] Audio saved ({os.path.getsize(audio_path)} bytes). Starting AI Processor...")
                process_meeting_data(audio_path, meeting_id)
                print("[SUCCESS] Transcript and MOM files are now in the /recordings folder.")
            else:
                print("[-] Error: Audio file is empty. Check your recorder.py settings.")
        except Exception as proc_err:
            print(f"[-] Post-processing failed: {proc_err}")
            
        driver.quit()
        print("[*] Driver closed. Bot task finished.")