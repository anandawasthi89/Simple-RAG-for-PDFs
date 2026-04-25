from fastapi import APIRouter, UploadFile, File
from src.core.Engine import Engine
from pydantic import BaseModel

class PDFQuery(BaseModel):
    question: str
    pdf_names: list[str]

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

@router.post("/resolveMultiPDFQuery")
def resolve_multiPDF_query(request: PDFQuery):
    return {"answer": engine.resolve_multiPDF_query(request.question, request.pdf_names)}

@router.post("/resolveMultiPDFQueryUsingLLM")
def resolve_multiPDF_query_llm(request: PDFQuery):
    return {"answer": engine.resolve_multiPDF_query_llm(request.question, request.pdf_names)}

