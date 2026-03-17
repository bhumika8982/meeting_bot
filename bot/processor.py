import os
from openai import OpenAI

# Client initialize karein (Make sure aapki API KEY environment variable mein ho ya yahan pass karein)
client = OpenAI(api_key="YOUR_OPENAI_API_KEY_HERE")

def process_meeting_data(audio_path, meeting_id):
    if not os.path.exists(audio_path):
        print("Audio file nahi mili!")
        return

    try:
        # Whisper transcription (Naya tareeka)
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        
        transcript_text = transcript.text
        
        # Summary generation
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates Minutes of Meeting (MOM)."},
                {"role": "user", "content": f"Summarize this transcript into a professional MOM:\n\n{transcript_text}"}
            ]
        )
        
        mom_content = response.choices[0].message.content

        # Save to outputs folder
        if not os.path.exists('outputs'):
            os.makedirs('outputs')
            
        output_file = f"outputs/MOM_{meeting_id}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(mom_content)
            
        print(f"Success! MOM saved for meeting {meeting_id}")

    except Exception as e:
        print(f"AI Processing mein error: {str(e)}")