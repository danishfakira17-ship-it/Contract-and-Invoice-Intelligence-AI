from app.tools.doc_intel import read_pdf

def run(pdf_path: str) -> dict:
    """Intake Agent: reads the file and returns raw text."""
    text = read_pdf(pdf_path)
    return {"agent": "intake", "text": text, "chars": len(text)}