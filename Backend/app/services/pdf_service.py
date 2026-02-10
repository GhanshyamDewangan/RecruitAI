
import io
from pypdf import PdfReader

class PDFService:
    def extract_text(self, file_content: bytes) -> tuple[str, int]:
        pdf = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
        return text, len(pdf.pages)

pdf_service = PDFService()
