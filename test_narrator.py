from narrator import generate_script
import os

def test_narrator():
    image_path = "output/images/page_001.png"
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found. Run extractor.py first.")
        return

    print(f"Generating script for {image_path}...")
    script = generate_script(image_path)
    print("\n--- Generated Script ---\n")
    print(script)
    print("\n------------------------\n")

if __name__ == "__main__":
    test_narrator()
