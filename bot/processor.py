import os
from openai import OpenAI

client = OpenAI(api_key="YOUR_OPENAI_KEY")

def process_meeting_data(audio_path, meeting_id):
    if not os.path.exists(audio_path): return

    try:
        with open(audio_path, "rb") as f:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=f)
        
        text = transcript.text

        # Requirement 4 & 5 ka structured prompt
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system", 
                "content": "You are a professional meeting assistant. Create a Minutes of Meeting (MOM) with: 1. Executive Summary, 2. Topic-wise Details, 3. Decisions Made, 4. Action Items."
            },
            {"role": "user", "content": f"Transcript: {text}"}]
        )

        mom = response.choices[0].message.content
        
        os.makedirs('outputs', exist_ok=True)
        with open(f"outputs/MOM_{meeting_id}.txt", "w") as f:
            f.write(mom)
            
    except Exception as e:
        print(f"Error in AI: {e}")