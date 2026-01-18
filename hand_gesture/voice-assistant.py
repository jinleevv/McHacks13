import os
import speech_recognition as sr
from google import genai
from google.genai import types

def listen_and_ask_gemini():
    # 1. Initialize Gemini Client (uses GOOGLE_API_KEY from env)
    client = genai.Client()
    sys_instruct = "Respond in plain conversational text ONLY. No markdown, no bolding (**), no bullet points. Use full sentences. This is for text-to-speech."
    
    # 2. Setup Microphone and Recognizer
    recognizer = sr.Recognizer()
    # Adjust for background noise sensitivity if needed
    recognizer.dynamic_energy_threshold = True 
    
    with sr.Microphone() as source:
        print("Listening... (Stop talking to finish)")
        # This records until it detects a significant pause (silence)
        audio_data = recognizer.listen(source)
        print("Processing...")

    # 3. Save audio to a temporary file
    temp_filename = "temp_voice_prompt.wav"
    output_text_file = "gemini_response.txt"
    with open(temp_filename, "wb") as f:
        f.write(audio_data.get_wav_data())

    try:
        # 4. Upload to Gemini
        audio_file = client.files.upload(file=temp_filename)
        
        # 5. Generate Content
        response = client.models.generate_content(
            model="gemini-flash-latest", # Latest stable Flash
            contents=[
            audio_file
            ],
            config=types.GenerateContentConfig(
                system_instruction=sys_instruct
            )
            
        )

        with open(output_text_file, "w", encoding="utf-8") as f:
            f.write(response.text)
        return response.text
    
    finally:
        # Cleanup
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

# Run it
if __name__ == "__main__":
    answer = listen_and_ask_gemini()
    print("-" * 30)
    print(f"Gemini: {answer}")