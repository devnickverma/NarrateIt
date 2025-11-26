import fitz

def create_test_pdf(output_path="test.pdf"):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Hello World! This is Page 1.", fontsize=20)
    page = doc.new_page()
    page.insert_text((50, 50), "This is Page 2.", fontsize=20)
    doc.save(output_path)
    print(f"Created {output_path}")

if __name__ == "__main__":
    create_test_pdf()
