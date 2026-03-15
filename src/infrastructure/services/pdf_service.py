import io
from pypdf import PdfReader

class PDFService:
    def extract_text(self, file_bytes: bytes) -> str:
        """
        Extracts text from a PDF file (given as bytes).
        """
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""
