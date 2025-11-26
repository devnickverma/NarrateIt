import fitz  # PyMuPDF
import os
import argparse
import shutil

def extract_images(pdf_path, output_dir="output/images"):
    """
    Converts PDF pages to high-resolution PNGs.
    """
    # Clean output directory if it exists to avoid stale files
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    try:
        doc = fitz.open(pdf_path)
        print(f"Opened '{pdf_path}', found {len(doc)} pages.")

        for i, page in enumerate(doc):
            # 300 DPI = 300 / 72 ~= 4.166
            # We use a matrix to scale the image
            zoom = 300 / 72
            mat = fitz.Matrix(zoom, zoom)
            
            # Get the pixmap (image)
            pix = page.get_pixmap(matrix=mat)
            
            # Save as page_001.png, page_002.png, etc.
            filename = f"page_{i+1:03d}.png"
            filepath = os.path.join(output_dir, filename)
            pix.save(filepath)
            print(f"Saved {filepath}")

        print("Extraction complete.")
        
    except Exception as e:
        print(f"Error processing PDF: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract images from PDF")
    parser.add_argument("pdf_path", help="Path to input PDF")
    args = parser.parse_args()
    
    extract_images(args.pdf_path)
