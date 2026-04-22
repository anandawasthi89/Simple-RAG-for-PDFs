from fastapi import APIRouter, UploadFile, File
from src.core.Engine import Engine

router = APIRouter()
engine = Engine()


@router.get("/checkPDFsAvailable")
def check_pdfs():
    return engine.get_available_pdfs()


@router.post("/uploadPDF")
def upload_pdf(file: UploadFile = File(...)):
    return engine.ingest_pdf(file)


@router.get("/refreshNewPDFsFromLocal")
def refresh_pdfs():
    return engine.refresh_data_pdfs()


@router.get("/resolveQuery")
def resolve_query(question: str, pdf_name: str):
    return {"answer": engine.resolve_query(question, pdf_name)}