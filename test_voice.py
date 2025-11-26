from voice import generate_audio
import os

def test_voice():
    text = "Hello! This is a test of the Manga Narrator voice system. I hope it sounds energetic and fun!"
    output_file = "output/audio/test_voice.mp3"
    
    print(f"Generating audio for text: '{text}'")
    duration = generate_audio(text, output_file)
    
    if duration:
        print(f"Audio saved to {output_file}")
        print(f"Duration: {duration:.2f} seconds")
    else:
        print("Audio generation failed.")

if __name__ == "__main__":
    test_voice()
