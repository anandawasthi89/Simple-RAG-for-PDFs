from fastapi import APIRouter, UploadFile, File
from src.core.Engine import Engine
from pydantic import BaseModel

class PDFQuery(BaseModel):
    question: str
    pdf_names: list[str]

class PDFSimpleQuery(BaseModel):
    question: str
    pdf_name: str

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

@router.post("/resolveQueryUsingMultiQuery")
def resolve_query_using_multiquery(request: PDFSimpleQuery):
    return {"answer": engine.resolve_query_using_multiquery(request.question, request.pdf_name)}

@router.post("/resolveQueryUsingRFP")
def resolveQueryUsingRFP(request: PDFSimpleQuery):
    return {"answer": engine.resolveQueryUsingRFP(request.question, request.pdf_name)}

@router.post("/resolveQueryUsingQueryDecomposition")
def resolveQueryUsingQueryDecomposition(request: PDFSimpleQuery):
    return {"answer": engine.resolveQueryUsingQueryDecomposition(request.question, request.pdf_name)}

@router.post("/resolveQueryUsingQueryDecomposition2")
def resolveQueryUsingQueryDecomposition2(request: PDFSimpleQuery):
    return {"answer": engine.resolveQueryUsingQueryDecomposition2(request.question, request.pdf_name)}

@router.post("/resolveQueryUsingStepBack")
def resolveQueryUsingStepBack(request: PDFSimpleQuery):
    return {"answer": engine.resolveQueryUsingStepBack(request.question, request.pdf_name)}

@router.post("/resolveQueryUsingHyDE")
def resolveQueryUsingHyDE(request: PDFSimpleQuery):
    return {"answer": engine.resolveQueryUsingHyDE(request.question, request.pdf_name)}