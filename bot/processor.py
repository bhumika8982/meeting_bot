import os
import json
import datetime
from deepgram import DeepgramClient, PrerecordedOptions
from openai import OpenAI

DEEPGRAM_API_KEY = "YOUR_DEEPGRAM_API_KEY"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

client = OpenAI(api_key=OPENAI_API_KEY)

def process_meeting_data(audio_path, meeting_id):
    dg_client = DeepgramClient(DEEPGRAM_API_KEY)
    
    if not os.path.exists(audio_path):
        print(f"[-] Error: Audio file {audio_path} not found.")
        return None

    try:
        print(f"[*] Processing audio for Meeting: {meeting_id}...")
        
        with open(audio_path, 'rb') as audio:
            buffer_data = audio.read()
            payload = {"buffer": buffer_data}
            
            options = PrerecordedOptions(
                model="nova-2",
                smart_format=True,
                diarize=True,
                language="en-IN",
                utterances=True
            )
            
            response = dg_client.listen.prerecorded.v("1").transcribe_file(payload, options)
            
        full_text = ""
        results = response.to_dict().get('results', {})
        utterances = results.get('utterances', [])
        
        if not utterances:
            channels = results.get('channels', [])
            if channels:
                full_text = channels[0].get('alternatives', [{}])[0].get('transcript', "")
        else:
            for ut in utterances:
                speaker = f"Speaker {ut.get('speaker', 0)}"
                start_time = ut.get('start', 0)
                text = ut.get('transcript', "")
                timestamp = f"[{int(start_time // 60):02d}:{int(start_time % 60):02d}]"
                full_text += f"{timestamp} {speaker}: {text}\n"

        if not full_text.strip():
            print("[-] No text recognized.")
            return None

        recordings_dir = os.path.dirname(audio_path)
        transcript_file = os.path.join(recordings_dir, f"transcript_{meeting_id}.txt")
        
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(full_text)
        
        print(f"[+] Transcript saved: {transcript_file}")
        
        generate_mom_report(full_text, meeting_id, recordings_dir)
        return transcript_file

    except Exception as e:
        print(f"[-] Deepgram Error: {e}")
        return None

def generate_mom_report(transcript, meeting_id, output_dir):
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    prompt = f"Analyze this transcript and generate professional MOM:\n\n{transcript}"
    
    try:
        print(f"[*] Generating AI MOM for {meeting_id}...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Professional corporate scribe."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        mom_content = response.choices[0].message.content
        mom_file = os.path.join(output_dir, f"mom_{meeting_id}.md")
        
        with open(mom_file, "w", encoding="utf-8") as f:
            f.write(mom_content)
        
        print(f"[SUCCESS] MOM saved: {mom_file}")
        return mom_file
        
    except Exception as e:
        print(f"[-] OpenAI Error: {e}")
        return None