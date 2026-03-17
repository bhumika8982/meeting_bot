import pyaudio
import wave
import threading
import os

class MeetingRecorder:
    def __init__(self, meeting_id):
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 2
        self.rate = 44100
        self.is_recording = False
        self.frames = []
        self.p = pyaudio.PyAudio()
        
        if not os.path.exists('recordings'):
            os.makedirs('recordings')
        self.filename = f"recordings/meeting_{meeting_id}.wav"

    def start(self):
        self.is_recording = True
        self.thread = threading.Thread(target=self._record)
        self.thread.start()

    def _record(self):
        try:
            stream = self.p.open(format=self.format, channels=self.channels,
                                 rate=self.rate, input=True, frames_per_buffer=self.chunk)
            while self.is_recording:
                self.frames.append(stream.read(self.chunk))
            stream.stop_stream()
            stream.close()
        except Exception as e:
            print(f"Audio Error: {e}")

    def stop(self):
        self.is_recording = False
        if hasattr(self, 'thread'):
            self.thread.join()
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        self.p.terminate()
        return os.path.abspath(self.filename)