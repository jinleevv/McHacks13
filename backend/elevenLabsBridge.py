import os
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

class ElevenLabsBridge:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("ELEVEN_LABS_API_KEY")
        self.__client = ElevenLabs(api_key=api_key)

    def generate_speech(self, text, voice_id="ljX1ZrXuDIIRVcmiVSyR"):
        audio_stream = self.__client.text_to_speech.convert(
            text=text,
            voice_id=voice_id
        )

        audio_data = b"".join(audio_stream)

        return audio_data