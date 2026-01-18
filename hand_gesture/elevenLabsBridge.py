import os
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

class ElevenLabsBridge:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("ELEVEN_LABS_API_KEY")
        self.__client = ElevenLabs(api_key=api_key)

    def generate_speech(self, text, voice_id="BFqnCBsd6RMkjVDRZzb"):
        response = self.__client.text_to_speech.with_raw_response.convert(
            text=text,
            voice_id=voice_id
        )
        # Access character cost from headers
        char_cost = response.headers.get("x-character-count")
        request_id = response.headers.get("request-id")
        audio_data = response.data
        return audio_data
