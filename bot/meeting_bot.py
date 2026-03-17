import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .recorder import start_recording, stop_recording
from .processor import process_meeting_data

def join_zoom_meeting(meeting_id, passcode):
    # Fix: audio_path ko pehle hi define kar dete hain taaki UnboundLocalError na aaye
    audio_path = f"recordings/meeting_{meeting_id}.wav"
    os.makedirs('recordings', exist_ok=True)
    
    chrome_options = Options()
    # Stealth Mode: Zoom ko lage ki ye bot nahi, insaan hai
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 30) # Wait badha diya hai

    try:
        # 1. Zoom Web Link (Direct Join)
        driver.get(f"https://app.zoom.us/wc/join/{meeting_id}")
        print("Zoom page loading...")

        # 2. Name Input (Bot Identity)
        # Zoom web client kabhi kabhi ID badalta hai, isliye multiple try
        try:
            name_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='inputname'], #inputname")))
            name_input.send_keys("Meeting Assistant")
            print("Name entered.")
        except:
            print("Name field directly nahi mila, manual check needed.")

        # 3. Passcode check
        if passcode:
            try:
                pass_input = driver.find_element(By.CSS_SELECTOR, "input[name='inputpasscode'], #inputpasscode")
                pass_input.send_keys(passcode)
            except:
                pass

        # 4. Join Button
        join_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.preview-join-button, .zm-btn")))
        join_btn.click()
        print("Join clicked.")

        # 5. Start Recording ONLY if join successful
        start_recording(audio_path)
        print("Recording started...")

        # Meeting loop
        while True:
            time.sleep(10)
            if not driver.window_handles: # Window close ho gayi
                break

    except Exception as e:
        print(f"Bot Join Error: {e}")
    finally:
        try:
            stop_recording(audio_path)
            print("Recording stopped.")
            process_meeting_data(audio_path, meeting_id)
        except:
            pass
        driver.quit()