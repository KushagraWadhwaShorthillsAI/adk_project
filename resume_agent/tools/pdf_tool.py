import os
import pdfplumber
from pathlib import Path
from typing import Dict, Union

def find_pdf_file(filename_or_path: str) -> Path:
    """
    Attempts to locate a file by checking multiple common locations 
    and performing a recursive search if necessary.
    """
    target = Path(filename_or_path)
    
    if target.is_absolute() and target.exists():
        return target

    search_roots = [Path.cwd(), Path.cwd().parent]
    target_name = target.name 

    common_subdirs = ["uploads", "data", "temp", "tmp", "files", "artifacts"]
    
    for root in search_roots:
        if (root / target_name).exists():
            return root / target_name
            
        for subdir in common_subdirs:
            candidate = root / subdir / target_name
            if candidate.exists():
                return candidate

    print(f"DEBUG: Performing deep search for {target_name}...")
    for root, dirs, files in os.walk(Path.cwd()):
        if target_name in files:
            return Path(root) / target_name

    return None

def read_resume_pdf(pdf_path: str) -> Dict[str, Union[str, int, bool]]:
    """
    Reads and extracts text from a PDF file path. 
    Call this tool to extract text from uploaded resume PDFs.
    
    Args:
        pdf_path (str): The file path or filename (e.g., "resume.pdf").
    """
    print(f"\n{'='*60}")
    print(f"🔧 TOOL CALLED: read_resume_pdf")
    print(f"📄 Input: pdf_path='{pdf_path}'")
    print(f"{'='*60}\n")
    
    if not pdf_path:
        return {"error": "No file path provided."}

    found_path = find_pdf_file(pdf_path)

    if not found_path:
        cwd_files = [f.name for f in Path.cwd().glob("*.pdf")]
        upload_files = []
        if (Path.cwd() / "uploads").exists():
            upload_files = [f.name for f in (Path.cwd() / "uploads").glob("*.pdf")]
            
        return {
            "error": (
                f"Could not locate '{pdf_path}'. "
                f"I searched recursively in {Path.cwd()}. "
                f"Current directory contains PDFs: {cwd_files}. "
                f"Uploads folder contains: {upload_files}. "
                "Please check the file name."
            )
        }

    if found_path.suffix.lower() != ".pdf":
        return {"error": "File is not a PDF. Please upload a .pdf file."}

    extracted_text = ""
    page_count = 0

    try:
        with pdfplumber.open(found_path) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"

        if not extracted_text.strip():
            return {"error": "The PDF was opened, but no text could be extracted (it might be an image scan)."}

        truncated = False
        if len(extracted_text) > 15000:
            extracted_text = extracted_text[:15000]
            truncated = True

        result = {
            "text": extracted_text,
            "pages": page_count,
            "truncated": truncated,
            "status": "success",
            "source_path": str(found_path)
        }
        
        print(f"\n{'='*60}")
        print(f"✅ TOOL COMPLETED: read_resume_pdf")
        print(f"📊 Output: Extracted {len(extracted_text)} chars from {page_count} pages")
        print(f"📁 Source: {found_path}")
        print(f"{'='*60}\n")
        
        return result

    except Exception as e:
        error_result = {"error": f"Technical extraction failure: {str(e)}"}
        print(f"\n{'='*60}")
        print(f"❌ TOOL FAILED: read_resume_pdf")
        print(f"Error: {str(e)}")
        print(f"{'='*60}\n")
        return error_result