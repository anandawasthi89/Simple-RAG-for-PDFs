import os
from pathlib import Path
from pypdf import PdfReader as PyPdfReader


class PDFLoader:
    def __init__(self, file_name: str):
        if not file_name:
            raise ValueError("File name cannot be empty")

        base_path = Path(__file__).resolve().parents[2]
        self.data_path = base_path / "data"
        self.file_path = self.data_path / file_name

        if not os.path.exists(str(self.file_path)):
            raise FileNotFoundError(f"{file_name} not found in data directory")
        else:
            print(f"{file_name} found in data directory")

    def load_pdf(self):
        try:
            reader = PyPdfReader(self.file_path)
            combined_text = []

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    combined_text.append(text)

            return "\n".join(combined_text)

        except Exception as e:
            raise RuntimeError(f"Failed to read PDF: {e}")