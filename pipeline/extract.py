import pdfplumber
import os

def extract_text_from_pdf(pdf_path):
    """Extract raw text from a PDF file."""
    text_content = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
    except Exception as e:
        print(f"Error parsing {pdf_path}: {e}")
        return ""
    
    return "\n".join(text_content)

def extract_all(pdf_dir, output_dir):
    """Extract text from all PDFs in the directory and save to text files."""
    os.makedirs(output_dir, exist_ok=True)
    if not os.path.exists(pdf_dir):
        print(f"PDF directory {pdf_dir} does not exist.")
        return []
        
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
    
    saved_files = []
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_dir, pdf_file)
        print(f"Extracting: {pdf_file}")
        raw_text = extract_text_from_pdf(pdf_path)
        
        if raw_text.strip():
            base_name = os.path.splitext(pdf_file)[0]
            output_file = os.path.join(output_dir, f"{base_name}.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(raw_text)
            saved_files.append(output_file)
        else:
            print(f"Warning: No text extracted from {pdf_file}")
            
    print(f"Extraction complete. {len(saved_files)} files saved to {output_dir}")
    return saved_files

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    pdf_dir = os.path.join(base_dir, "data", "pdfs")
    output_dir = os.path.join(base_dir, "data", "texts")
    extract_all(pdf_dir, output_dir)
