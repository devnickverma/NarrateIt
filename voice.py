import os
from dotenv import load_dotenv
from deepgram import DeepgramClient
from pydub import AudioSegment

load_dotenv()

def generate_audio(text, output_filename="output/audio/temp.mp3"):
    """
    Generates audio from text using Deepgram and saves it to a file.
    Returns the duration of the audio in seconds.
    """
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise ValueError("DEEPGRAM_API_KEY not found in environment variables.")

    try:
        deepgram = DeepgramClient(api_key=api_key)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
        
        # Call the generate method
        response = deepgram.speak.v1.audio.generate(
            text=text,
            model="aura-orion-en"
        )
        
        with open(output_filename, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)
        
        # Calculate duration using pydub
        audio = AudioSegment.from_file(output_filename)
        duration_seconds = len(audio) / 1000.0
        
        return duration_seconds

    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

if __name__ == "__main__":
    print("Voice module ready. Import `generate_audio` to use.")
