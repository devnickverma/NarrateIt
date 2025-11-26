import os
import subprocess

def create_video(segments, output_filename="output/final_video.mp4"):
    """
    Stitches images and audio into a video.
    segments: List of dicts with keys 'image', 'audio', 'duration'.
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    # Create demuxer files
    images_txt = "images_list.txt"
    audios_txt = "audios_list.txt"
    
    with open(images_txt, "w") as f_img, open(audios_txt, "w") as f_aud:
        for segment in segments:
            # Escape paths for FFmpeg
            img_path = segment['image'].replace("\\", "/")
            aud_path = segment['audio'].replace("\\", "/")
            
            f_img.write(f"file '{img_path}'\n")
            f_img.write(f"duration {segment['duration']}\n")
            
            f_aud.write(f"file '{aud_path}'\n")
        
        # Add the last image again to prevent the last frame from being skipped/shortened
        # This is a known quirk of the concat demuxer for images
        if segments:
            last_img = segments[-1]['image'].replace("\\", "/")
            f_img.write(f"file '{last_img}'\n")

    # FFmpeg command
    # -f concat -safe 0 -i images_list.txt -f concat -safe 0 -i audios_list.txt -c:v libx264 -c:a aac -pix_fmt yuv420p -shortest output.mp4
    cmd = [
        "ffmpeg",
        "-y", # Overwrite output
        "-f", "concat",
        "-safe", "0",
        "-i", images_txt,
        "-f", "concat",
        "-safe", "0",
        "-i", audios_txt,
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        "-shortest", # End when the shortest input ends (usually audio matches video roughly, but good safety)
        output_filename
    ]
    
    print(f"Running FFmpeg: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(f"Video created: {output_filename}")
        
        # Cleanup temp files
        if os.path.exists(images_txt):
            os.remove(images_txt)
        if os.path.exists(audios_txt):
            os.remove(audios_txt)
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg failed: {e}")
        return False

if __name__ == "__main__":
    print("Video Maker module ready. Import `create_video` to use.")
