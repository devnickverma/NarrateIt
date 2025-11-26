from video_maker import create_video
import os
import shutil

def test_video_maker():
    # Setup test assets
    os.makedirs("output/audio", exist_ok=True)
    
    # Use existing images from extractor test
    img1 = "output/images/page_001.png"
    img2 = "output/images/page_002.png"
    
    if not os.path.exists(img1) or not os.path.exists(img2):
        print("Error: Images not found. Run extractor.py first.")
        return

    # Create dummy audio files (copy test_voice.mp3 if exists, else fail)
    src_audio = "output/audio/test_voice.mp3"
    if not os.path.exists(src_audio):
        print("Error: test_voice.mp3 not found. Run test_voice.py first.")
        return
        
    aud1 = "output/audio/test_1.mp3"
    aud2 = "output/audio/test_2.mp3"
    shutil.copy(src_audio, aud1)
    shutil.copy(src_audio, aud2)
    
    # Define segments
    # Assuming test_voice.mp3 is ~5.28s
    segments = [
        {"image": img1, "audio": aud1, "duration": 5.28},
        {"image": img2, "audio": aud2, "duration": 5.28}
    ]
    
    print("Creating test video...")
    create_video(segments, "output/test_video.mp4")

if __name__ == "__main__":
    test_video_maker()
