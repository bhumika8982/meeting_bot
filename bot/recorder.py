import numpy as np
import sys
import threading
import soundcard as sc
import soundfile as sf
import os
import time

# CRITICAL FIX: Direct replacement for the deprecated function
def patched_fromstring(string, dtype=float, count=-1, sep='', offset=0):
    return np.frombuffer(string, dtype=dtype, count=count, offset=offset)

# Force apply the patch
np.fromstring = patched_fromstring

is_recording = False
recording_data = []
fs = 44100

def record_loop(filename):
    global is_recording, recording_data
    try:
        # Loopback enable karke system ki awaz pakadne ke liye
        speaker = sc.default_speaker()
        mic = sc.get_microphone(id=str(speaker.name), include_loopback=True)
        
        with mic.recorder(samplerate=fs) as recorder:
            while is_recording:
                # numframes ko thoda badhaya hai stability ke liye
                data = recorder.record(numframes=4096)
                if data.ndim > 1:
                    data = np.mean(data, axis=1)
                recording_data.append(data)
    except Exception as e:
        # Terminal mein check karein agar mic access blocked hai
        print(f"[-] Recorder Loop Error: {e}")

def start_recording(filename):
    global is_recording, recording_data
    recording_data = []
    is_recording = True
    thread = threading.Thread(target=record_loop, args=(filename,), daemon=True)
    thread.start()
    print("[*] Recording thread started...")

def stop_recording(filename):
    global is_recording, recording_data
    is_recording = False
    time.sleep(2) # Buffer catch karne ke liye thoda extra time
    
    if recording_data:
        try:
            print(f"[*] Concatenating {len(recording_data)} audio chunks...")
            final_audio = np.concatenate(recording_data, axis=0)
            sf.write(filename, final_audio, fs)
            print(f"[+] Audio saved successfully: {filename}")
        except Exception as e:
            print(f"[-] Error during audio save: {e}")
    else:
        print("[-] ERROR: No audio data captured in recording_data list.")