from google import genai
import os
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

def get_genai_client():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")
    return genai.Client(api_key=api_key)

def generate_script(image_path):
    """
    Sends an image to Gemini and gets a witty narration script.
    """
    client = get_genai_client()
    
    # model = genai.GenerativeModel('gemini-2.5-flash') - REMOVED
    
    system_prompt = """You are a natural, conversational manga narrator making a video for fans. Look at this manga page. Read the panels in the correct Japanese order (Right-to-Left).
    
    Your Task:
    1. Narrate the visual action briefly between dialogue (e.g., "Naruto looks at Sasuke... looking like he's about to explode.")
    2. Read the dialogue with character labels (e.g., "Sasuke says... argument")
    3. MANDATORY SPEECH STYLE:
       - Write like a real person thinking and reacting in real-time.
       - Use natural hesitation and fillers: "umm", "hmm", "uh", "oh...", "huh".
       - Use punctuation to control pacing: "," for short pauses, "..." for hesitation.
       - SHORT sentences. Informal phrasing.
       - Output only plain text. No markdown.
    """
    
    try:
        img = Image.open(image_path)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[system_prompt, img]
        )
        return response.text
    except Exception as e:
        print(f"Error generating script: {e}")
        return None

if __name__ == "__main__":
    # Test with a dummy image if available, or just print a message
    print("Narrator module ready. Import `generate_script` to use.")
