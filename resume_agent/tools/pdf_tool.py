import pdfplumber
from pathlib import Path
from typing import Dict


def read_resume_pdf(pdf_path: str) -> Dict:
    """
    Reads and extracts text from an uploaded resume PDF.
    Designed for ADK Web UI uploads.
    """

    if not pdf_path:
        raise ValueError("PDF path not provided by agent.")

    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"Resume PDF not found at {pdf_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Uploaded file is not a PDF.")

    extracted_text = ""
    page_count = 0

    try:
        with pdfplumber.open(path) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"

        if not extracted_text.strip():
            raise ValueError("PDF contains no extractable text.")

        truncated = False
        if len(extracted_text) > 15000:
            extracted_text = extracted_text[:15000]
            truncated = True

        return {
            "text": extracted_text,
            "pages": page_count,
            "truncated": truncated
        }

    except Exception as e:
        raise RuntimeError(f"PDF extraction failed: {str(e)}")
