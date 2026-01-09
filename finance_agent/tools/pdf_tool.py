import pdfplumber
import os

def read_pdf_file(pdf_path: str):
    """
    Reads the text content of a PDF file.
    Use this to read Prospectuses, Summaries, or Analyst Reports.
    
    Args:
        pdf_path: The absolute path to the PDF file.
        
    Returns:
        The extracted text from the PDF (truncated to 50,000 characters if too long).
    """
    if not os.path.exists(pdf_path):
        return f"Error: File not found at {pdf_path}"
    
    extracted_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Simple iteration over all pages
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
                    
        if not extracted_text:
            return "No text found in the PDF."
            
        # Truncate to protect LLM context window (approx 2k-3k tokens)
        if len(extracted_text) > 10000:
            return extracted_text[:10000] + "\n... [Text Truncated to 10k chars for Agent capability] ..."
            
        return extracted_text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"
