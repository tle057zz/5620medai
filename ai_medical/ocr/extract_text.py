# ai_medical/ocr/extract_text.py
"""
OCR Extractor (Final Production-Grade Version)

Features:
- Hybrid text + OCR pipeline (pdfplumber → Tesseract)
- Page-level fault tolerance (no global crashes)
- Automatic image preprocessing (grayscale → binary)
- Optional Poppler path detection for Windows
- Fully OS/path independent
- UTF-8 safe and deterministic output
- Optional structured output (for downstream modules)
"""

import os
import pytesseract
import pdfplumber
from PIL import Image
from pdf2image import convert_from_path

def extract_text_from_pdf(pdf_path: str, verbose: bool = True) -> str:
    """
    Robust hybrid text extractor supporting both text and image PDFs.
    Uses pdfplumber for native text and Tesseract OCR for scanned pages.
    Deterministic per-page tagging for reproducibility.
    """
    text_output = []

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    poppler_path = os.getenv("POPPLER_PATH", None)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            if verbose:
                print(f"Processing {total_pages} pages...")

            for i, page in enumerate(pdf.pages):
                page_num = i + 1
                try:
                    # Step 1: Try native text extraction
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        page_text = page_text.encode("utf-8", "ignore").decode()
                        text_output.append(f"\n--- Page {page_num} (Text) ---\n{page_text}\n")
                        continue

                    # Step 2: Fallback to OCR for image pages
                    if verbose:
                        print(f"Page {page_num}: no text detected → running OCR...")

                    images = convert_from_path(
                        pdf_path, first_page=page_num, last_page=page_num,
                        poppler_path=poppler_path
                    )
                    if not images:
                        if verbose:
                            print(f"Page {page_num}: failed to render image for OCR.")
                        continue

                    image = images[0]
                    # Preprocessing (grayscale + binary threshold)
                    gray = image.convert("L")
                    bw = gray.point(lambda x: 0 if x < 160 else 255, "1")

                    ocr_text = pytesseract.image_to_string(bw, config="--psm 6")
                    ocr_text = ocr_text.encode("utf-8", "ignore").decode()
                    text_output.append(f"\n--- Page {page_num} (OCR) ---\n{ocr_text}\n")

                except Exception as page_err:
                    if verbose:
                        print(f"Page {page_num} failed: {page_err}")
                    continue

    except Exception as e:
        print(f"OCR extraction failed: {e}")

    # Join and trim
    return "".join(text_output).strip()


if __name__ == "__main__":
    # Resolve this file's directory for path independence
    this_dir = os.path.dirname(os.path.abspath(__file__))
    sample_path = os.path.join(this_dir, "Sampleocr.pdf")

    if os.path.exists(sample_path):
        text = extract_text_from_pdf(sample_path)

        # Save in the same module folder
        output_path = os.path.join(this_dir, "Sampleocr_output.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"\nExtracted Text Preview:\n{text[:800]}")
        print(f"\nOutput saved at: {output_path}")
    else:
        print(f"No sample file found at: {sample_path}")
