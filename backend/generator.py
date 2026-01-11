import os
import time
import logging
import glob
import shutil
import json
import concurrent.futures
import fitz  # PyMuPDF
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image
from deepgram import DeepgramClient
from pydub import AudioSegment
import subprocess
import random
import re

# Load environment variables from the parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_genai_client():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")
    return genai.Client(api_key=api_key)

def extract_images(pdf_path, output_dir):
    """Converts PDF pages to high-resolution PNGs."""
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    try:
        doc = fitz.open(pdf_path)
        logging.debug(f"Opened '{pdf_path}', found {len(doc)} pages.")

        image_paths = []
        for i, page in enumerate(doc):
            zoom = 300 / 72
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            filename = f"page_{i+1:03d}.png"
            filepath = os.path.join(output_dir, filename)
            pix.save(filepath)
            image_paths.append(filepath)
            logging.debug(f"Saved {filepath}")
        
        return sorted(image_paths)
    except Exception as e:
        logging.error(f"Error extracting images: {e}")
        return []

def generate_script_for_page(image_path, custom_prompt, page_num):
    """Generates a structured JSON script using Gemini for a single page."""
    client = get_genai_client()
    # Use JSON mode for structured output
    # Model configuration is now passed during generation
    
    # Enhanced prompt for logical flow and JSON structure
    full_prompt = f"""
    {custom_prompt}

    CRITICAL INSTRUCTION:
    1. **Analyze Panel Flow:** You **must** analyze the panel layout and dialogue placement to determine the **logically intended reading order** for maximum dramatic impact. The flow must be natural and cinematic.
    2. **Structured Output:** Output a **JSON Object** with a single key "script_segments" containing an array of objects.
    3. **Natural Speech Style (MANDATORY):** 
       - Write like a real person thinking and reacting in real-time.
       - Use natural hesitation and fillers where appropriate: "umm", "hmm", "uh", "oh...", "huh".
       - Use punctuation to control pacing: "," for short pauses, "..." for hesitation.
       - SHORT sentences. Informal phrasing.
       - **NO SSML TAGS.** Do not use `<break>` tags. Use text-based pacing ("...") instead.

    JSON Schema Requirement:
    {{
      "script_segments": [
        {{
          "type": "narration",
          "text": "The villagers gaze up at the castle... uh, they look completely terrified by that shadow."
        }},
        {{
          "type": "dialogue",
          "speaker": "The Hero",
          "text": "...Are you ready to face him? Hah, I know I'm not."
        }}
      ]
    }}

    **"Best Narrator" Checklist (REQUIRED for every page):**
    1. **Opening Hook:** Start every page with a **Narration segment** that sets the scene.
    2. **Facial Analysis:** Before reading a character's dialogue, insert a **Narration segment** describing their **emotion**.
    3. **Action Segregation:** Insert a **Narration segment** *between* dialogue blocks if there is a scene transition.
    4. **Closing Scene:** End the script with a final **Narration segment** describing the cliffhanger or transition.
    """
    
    MAX_RETRIES = 3
    RETRY_DELAY = 10  # Seconds
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            img = Image.open(image_path)
            logging.debug(f"Sending Page {page_num} to Gemini (Attempt {attempt+1})...")
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[full_prompt, img],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            # Parse JSON
            script_data = json.loads(response.text)
            logging.info(f"Script generated for Page {page_num}")
            return script_data
            
        except Exception as e:
            # Check for Rate Limit (429) or Overloaded (503)
            # The python library wraps the error, but we look for "429" in the string
            if "429" in str(e) or "Resource exhausted" in str(e):
                if attempt < MAX_RETRIES:
                    wait_time = RETRY_DELAY * (2 ** attempt)  # Exponential Backoff: 10s, 20s, 40s
                    # Add jitter
                    wait_time += random.uniform(0, 5)
                    logging.debug(f"Rate Limit hit for Page {page_num}. Retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    logging.error(f"Failed to generate script for Page {page_num} after {MAX_RETRIES} retries: {e}")
                    return None
            else:
                logging.error(f"Error generating script for Page {page_num}: {e}")
                return None

def split_text_for_tts(text, max_chars=1500):
    """Splits text into chunks respecting sentence boundaries to avoid 2000 char limit."""
    if len(text) <= max_chars:
        return [text]
        
    chunks = []
    # Split by sentence endings (.?!) followed by space
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    current_chunk = ""
    for sentence in sentences:
        # Check if adding this sentence exceeds limit
        if len(current_chunk) + len(sentence) + 1 <= max_chars:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
            
            # Safety for extremely long sentences (rare but possible)
            if len(current_chunk) > max_chars:
                chunks.append(current_chunk[:max_chars])
                current_chunk = current_chunk[max_chars:]

    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks

def generate_audio_for_segment(text, output_filename, voice_model):
    """Generates audio for a single segment using Deepgram, with chunking support."""
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise ValueError("DEEPGRAM_API_KEY not found.")

    # Map short IDs to full Deepgram model tags
    voice_map = {
        "asteria": "aura-asteria-en",
        "orion": "aura-orion-en",
        "luna": "aura-luna-en",
        "hyperion": "aura-orion-en"
    }
    
    model_tag = voice_map.get(voice_model, voice_model)
    MAX_RETRIES = 3
    RETRY_DELAY = 5

    # Split text if too long
    text_chunks = split_text_for_tts(text)
    temp_files = []
    combined_audio = AudioSegment.empty()

    success_all = True

    try:
        deepgram = DeepgramClient(api_key=api_key)
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)

        for i, chunk in enumerate(text_chunks):
            if not chunk.strip():
                continue
            
            chunk_file = f"{output_filename}_part{i}.mp3"
            chunk_success = False

            for attempt in range(MAX_RETRIES + 1):
                try:
                    # Wrap text in <speak> tag for SSML processing
                    ssml_text = f"<speak>{chunk}</speak>"
                    
                    response = deepgram.speak.v1.audio.generate(
                        text=ssml_text,
                        model=model_tag
                    )
                    
                    with open(chunk_file, "wb") as f:
                        for byte_chunk in response:
                            if byte_chunk:
                                f.write(byte_chunk)
                    
                    chunk_audio = AudioSegment.from_file(chunk_file)
                    combined_audio += chunk_audio
                    temp_files.append(chunk_file)
                    chunk_success = True
                    break # Success, move to next chunk
                    
                except Exception as e:
                    if attempt < MAX_RETRIES:
                        wait_time = RETRY_DELAY * (2 ** attempt) + random.uniform(0, 2)
                        logging.debug(f"Chunk {i} failed (Attempt {attempt+1}). Retrying in {wait_time:.1f}s... Error: {e}")
                        time.sleep(wait_time)
                    else:
                        logging.error(f"Failed to generate audio chunk {i} after retries: {e}")
            
            if not chunk_success:
                success_all = False
                break
        
        if success_all:
            combined_audio.export(output_filename, format="mp3")
            return len(combined_audio) / 1000.0
        else:
            return None

    except Exception as e:
        logging.error(f"Audio generation wrapper failed: {e}")
        return None
    finally:
        # Cleanup temp chunks
        for f in temp_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass

def process_page_audio(page_data, page_num, audio_dir, voice_model):
    """Processes all audio segments for a single page."""
    if not page_data or "script_segments" not in page_data:
        logging.warning(f"Page {page_num}: Missing 'script_segments' key in JSON.")
        return None

    segments = page_data["script_segments"]
    full_text = ""
    
    for seg in segments:
        text = seg.get("text", "")
        # Concatenate text. Gemini is now responsible for inserting <break> tags for pauses.
        # We add a space just in case, but the SSML tags will handle the timing.
        full_text += f"{text} "
    
    audio_filename = os.path.join(audio_dir, f"page_{page_num:03d}.mp3")
    duration = generate_audio_for_segment(full_text, audio_filename, voice_model)
    
    if duration:
        logging.info(f"Audio synthesized for Page {page_num}")
        return {
            "image": None, # Will be filled later
            "audio": audio_filename,
            "duration": duration
        }
    return None

def create_video(segments, output_filename):
    """Stitches images and audio into a video using FFmpeg."""
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    # Use absolute paths for list files to avoid CWD issues
    base_dir = os.path.dirname(output_filename)
    images_txt = os.path.join(base_dir, "images_list.txt")
    audios_txt = os.path.join(base_dir, "audios_list.txt")
    
    with open(images_txt, "w") as f_img, open(audios_txt, "w") as f_aud:
        for segment in segments:
            img_path = segment['image'].replace("\\", "/")
            aud_path = segment['audio'].replace("\\", "/")
            f_img.write(f"file '{img_path}'\n")
            f_img.write(f"duration {segment['duration']}\n")
            f_aud.write(f"file '{aud_path}'\n")
        
        if segments:
            last_img = segments[-1]['image'].replace("\\", "/")
            f_img.write(f"file '{last_img}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", images_txt,
        "-f", "concat", "-safe", "0", "-i", audios_txt,
        # RESIZE TO 1080p HEIGHT (maintain aspect ratio, width divisible by 2)
        # 13k pixels causes x264 memory crash.
        "-vf", "scale=-2:1080,format=yuv420p",
        "-c:v", "libx264",
        "-crf", "24",  # Optimization: CRF 24 for balance of size/quality
        "-preset", "medium",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        output_filename
    ]
    
    try:
        logging.debug(f"Running FFmpeg...")
        # Capture output=True captures stdout/stderr, but if it fails, we need to log e.stderr
        subprocess.run(cmd, check=True, capture_output=True)
        logging.info(f"Video created: {output_filename}")
        
        # Cleanup only on success
        if os.path.exists(images_txt): os.remove(images_txt)
        if os.path.exists(audios_txt): os.remove(audios_txt)
        return True
    except subprocess.CalledProcessError as e:
        # DECODE stderr to see the real error
        error_msg = e.stderr.decode('utf-8', errors='replace') if e.stderr else "No stderr captured"
        logging.error(f"FFmpeg failed with return code {e.returncode}")
        logging.error(f"FFmpeg Error Output:\n{error_msg}")
        return False

def run_narration_pipeline(pdf_path: str, voice_model: str, custom_prompt: str, output_dir: str, progress_callback=None) -> str:
    """
    Executes the full video generation pipeline with granular progress tracking.
    """
    def report_progress(percent, message):
        if progress_callback:
            progress_callback(percent, message)
            
    logging.info(f"--- Starting Pipeline for {pdf_path} ---")
    report_progress(5, "INITIALIZING PROTOCOL... Checking file and settings...")
    
    # Setup directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.join(base_dir, "../temp_processing")
    images_dir = os.path.join(temp_dir, "images")
    audio_dir = os.path.join(temp_dir, "audio")
    
    # Step 1: Extract Images
    report_progress(10, "STEP 1/4: Analyzing visual data (PDF to Images)...")
    images = extract_images(pdf_path, images_dir)
    if not images:
        raise Exception("Failed to extract images from PDF.")
    
    total_pages = len(images)
    report_progress(15, f"Analysis Complete. Found {total_pages} pages.")

    # Step 2: Sequential Script Generation (Strict Rate Limiting for Free Tier)
    report_progress(20, "STEP 2/4: Generating witty scripts (Sequentially)...")
    page_scripts = [None] * total_pages
    
    for i, img_path in enumerate(images):
        current_percent = 20 + int((i / total_pages) * 40) # 20% to 60%
        report_progress(current_percent, f"Scripting Page {i+1}/{total_pages}...")
        
        logging.info(f"Processing Page {i+1}/{total_pages}...")
        try:
            # Generate script
            data = generate_script_for_page(img_path, custom_prompt, i+1)
            page_scripts[i] = data
            
            # CRITICAL: Strict delay to respect 15 RPM limit (60s / 15 = 4s).
            if i < total_pages - 1: # Don't sleep after the last page
                time.sleep(5)
                
        except Exception as e:
            logging.error(f"Script generation failed for page {i+1}: {e}")

    # Step 3: Sequential Audio Generation (Strict Rate Limiting for Deepgram)
    report_progress(60, "STEP 3/4: Synthesizing voiceover (Sequentially)...")
    final_segments = [None] * total_pages
    
    for i, script_data in enumerate(page_scripts):
        current_percent = 60 + int((i / total_pages) * 30) # 60% to 90%
        report_progress(current_percent, f"Voicing Page {i+1}/{total_pages}...")
        
        if script_data:
            try:
                result = process_page_audio(script_data, i+1, audio_dir, voice_model)
                if result:
                    result["image"] = images[i]
                    final_segments[i] = result
            except Exception as e:
                logging.error(f"Audio generation failed for page {i+1}: {e}")
            
            # Throttle Deepgram slightly to be safe? 
            # Deepgram handles concurrency better but we saw 429s. 
            # Let's add a small 1s delay just to be safe.
            time.sleep(1)
        else:
            logging.warning(f"No script for page {i+1}, skipping audio.")
    
    # Filter out None segments
    valid_segments = [s for s in final_segments if s is not None]
    
    if not valid_segments:
        raise Exception("No segments were successfully generated.")

    # Step 4: Video Assembly
    report_progress(90, "STEP 4/4: Stitching final video output...")
    output_filename = f"{os.path.splitext(os.path.basename(pdf_path))[0]}_narrated.mp4"
    final_video_path = os.path.join(output_dir, output_filename)
    
    success = create_video(valid_segments, final_video_path)
    
    if not success:
        raise Exception("Video assembly failed.")
        
    report_progress(100, "GENERATION COMPLETE! Video ready.")
    logging.info(f"Pipeline Complete. Video saved to {final_video_path}")
    return output_filename
