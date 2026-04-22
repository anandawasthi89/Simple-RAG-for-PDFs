from pathlib import Path
from fastapi import UploadFile
from pypdf import PdfReader


class PDFLoader:
    def __init__(self, data_path: Path):
        self.data_path = data_path

    def load_pdf(self, file_name: str):
        try:
            file_path = self.data_path / file_name
            reader = PdfReader(file_path)

            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""

            return text

        except Exception as e:
            raise RuntimeError(f"Failed to read PDF: {e}")

    def stream_pdf(self, file: UploadFile):
        try:
            pdf_name = file.filename

            reader = PdfReader(file.file)

            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""

            return text, pdf_name

        except Exception as e:
            raise RuntimeError(f"Failed to stream PDF: {e}")