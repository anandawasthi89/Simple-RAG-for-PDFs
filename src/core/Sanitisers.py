import re

def sanitize_collection_name(file_name: str) -> str:
    # remove extension
    name = file_name.rsplit(".", 1)[0]

    # replace invalid chars (including spaces) with underscore
    name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)

    # ensure starts/ends with alphanumeric
    name = name.strip("._-")

    return f"PDF_{name}"

def normalize_pdf_name(pdf_name: str) -> str:
    # If already prefixed, don't add again
    if pdf_name.startswith("PDF_"):
        return pdf_name
    return "PDF_" + pdf_name