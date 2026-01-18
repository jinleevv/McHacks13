import speech_recognition as sr
from dotenv import load_dotenv
from google import genai
import os
import time
from hand_gesture.elevenLabsBridge import ElevenLabsBridge
from playsound import playsound


class GeminiVoiceAssistant:
    def __init__(self, gemini_key=None, model_name="gemini-2.0-flash"):
        load_dotenv()

        # Setup Gemini
        self.api_key = gemini_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required.")

        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name

        # Setup Speech Recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Setup Text-to-Speech Bridge
        print("Connecting to ElevenLabs...")
        self.tts_bridge = ElevenLabsBridge()

    def listen(self):
        """Captures audio from the microphone and returns text."""
        print("\n🎤 Listening... (Speak now)")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=8)
                print("Processing speech...")
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text
            except sr.WaitTimeoutError:
                print("No speech detected.")
            except sr.UnknownValueError:
                print("Could not understand audio.")
            except Exception as e:
                print(f"Error: {e}")
        return None

    def generate_response(self, prompt):
        """Sends text to Gemini and returns the AI's response."""
        if not prompt:
            return None

        print("🧠 Gemini is thinking...")
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return "I am having trouble connecting to my brain."

    def speak(self, text):
        """Uses ElevenLabs to generate audio and plays it."""
        if not text:
            return

        print("🔊 Generating voice...")
        try:
            # 1. Get raw audio bytes from your Bridge
            audio_bytes = self.tts_bridge.generate_speech(text)

            # 2. Save to a temporary file (playsound requires a file path)
            temp_file = "temp_response.mp3"
            with open(temp_file, "wb") as f:
                f.write(audio_bytes)

            # 3. Play the audio
            print(f"Gemini says: {text}")
            playsound(temp_file)

            # 4. Cleanup
            if os.path.exists(temp_file):
                os.remove(temp_file)

        except Exception as e:
            print(f"TTS Error: {e}")

    def run(self):
        """Main interaction loop."""
        while True:
            user_text = self.listen()
            if user_text:
                # Exit condition
                if "exit" in user_text.lower() or "stop" in user_text.lower():
                    print("Goodbye!")
                    break

                ai_response = self.generate_response(user_text)
                self.speak(ai_response)
                # 3. THE COOLDOWN LOGIC
                # This block runs only after the bot has finished speaking.
                print("\n--- Cooling down for 15 seconds... ---")
                time.sleep(15)
                print("--- Ready to listen again ---\n")


# --- 3. Usage ---
if __name__ == "__main__":
    # Ensure you have a .env file with:
    # GEMINI_API_KEY=your_key
    # ELEVEN_LABS_API_KEY=your_key

    try:
        bot = GeminiVoiceAssistant()
        bot.run()
    except Exception as e:
        print(f"Setup Error: {e}")