import sounddevice as sd
from scipy.io.wavfile import write
import threading

fs = 44100  # Sample rate
recording = []
is_recording = False

def start_recording(filename):
    global is_recording, recording
    recording = []
    is_recording = True
    
    def record():
        global recording
        # Device 0 ya default system output capture karega
        with sd.InputStream(samplerate=fs, channels=2) as stream:
            while is_recording:
                data, overflowed = stream.read(1024)
                recording.append(data)
    
    threading.Thread(target=record).start()

def stop_recording(filename):
    global is_recording
    is_recording = False
    import numpy as np
    full_recording = np.concatenate(recording, axis=0)
    write(filename, fs, full_recording)