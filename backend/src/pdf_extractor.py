# backend/src/pdf_extractor.py

import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract clean text from a PDF using PyMuPDF."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()
        return text.strip()

    except FileNotFoundError:
        raise FileNotFoundError(f"Error: The file '{pdf_path}' was not found.")
    except Exception as e:
        raise RuntimeError(f"An error occurred while reading the PDF: {e}")