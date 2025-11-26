import os
import argparse
import glob
from extractor import extract_images
from narrator import generate_script
from voice import generate_audio
from video_maker import create_video

def main():
    parser = argparse.ArgumentParser(description="MangaNarrator: Convert Manga PDF to Read-Along Video")
    parser.add_argument("pdf_path", help="Path to the input Manga PDF")
    args = parser.parse_args()
    
    pdf_path = args.pdf_path
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file '{pdf_path}' not found.")
        return

    print(f"Processing '{pdf_path}'...")
    
    # Phase 1: Image Extraction
    print("\n--- Phase 1: Extracting Images ---")
    extract_images(pdf_path)
    
    # Get sorted list of images
    image_dir = "output/images"
    images = sorted(glob.glob(os.path.join(image_dir, "*.png")))
    
    if not images:
        print("No images extracted. Exiting.")
        return
    
    segments = []
    
    # Phase 2 & 3: Script & Audio Generation
    print("\n--- Phase 2 & 3: Generating Script and Audio ---")
    for i, img_path in enumerate(images):
        print(f"Processing Page {i+1}/{len(images)}: {img_path}")
        
        # Generate Script
        print("  Generating script...")
        script = generate_script(img_path)
        if not script:
            print("  Failed to generate script. Skipping page.")
            continue
            
        print(f"  Script: {script[:50]}...") # Print first 50 chars
        
        # Generate Audio
        print("  Generating audio...")
        audio_filename = f"output/audio/page_{i+1:03d}.mp3"
        duration = generate_audio(script, audio_filename)
        
        if duration:
            print(f"  Audio saved. Duration: {duration:.2f}s")
            segments.append({
                "image": img_path,
                "audio": audio_filename,
                "duration": duration
            })
        else:
            print("  Failed to generate audio. Skipping page.")
    
    if not segments:
        print("No segments created. Exiting.")
        return
        
    # Phase 4: Video Assembly
    print("\n--- Phase 4: Assembling Video ---")
    output_video = "output/final_video.mp4"
    success = create_video(segments, output_video)
    
    if success:
        print(f"\nSUCCESS! Video saved to: {output_video}")
    else:
        print("\nVideo assembly failed.")

if __name__ == "__main__":
    main()
