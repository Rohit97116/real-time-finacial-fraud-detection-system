import pdfplumber
import pytesseract
from pdf2image import convert_from_path


def extract_text_from_pdf(file_path):
    text_content = ""

    # Step 1: Try normal text extraction first.
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content += text + "\n"
    except Exception as e:
        print("Text extraction error:", e)

    # Step 2: If too little text was extracted, try OCR fallback.
    if len(text_content.strip()) < 100:
        print("Detected image-based PDF -> Using OCR...")
        try:
            images = convert_from_path(file_path)
            for img in images:
                ocr_text = pytesseract.image_to_string(img)
                text_content += ocr_text + "\n"
        except Exception as e:
            print("OCR extraction error:", e)

    # Step 3: Final safety.
    if not text_content.strip():
        print("No text extracted from PDF.")
        return ""

    print("Text extraction successful.")
    return text_content
