import pdfplumber

def extract_text_from_pdf(pdf_path):
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"
    except Exception as e:
        print(f"[PDF解析錯誤] {e}")
        return None
    return full_text.strip()
