from pathlib import Path
from fastapi import UploadFile
from langchain_ollama import ChatOllama

from src.core.Chunker import Chunker
from src.core.Sanitisers import normalize_pdf_name
from src.core.EmbeddingService import EmbeddingService
from src.core.PDFLoader import PDFLoader
from src.core.VectorStore import VectorStore


class Engine:
    def __init__(
        self,
        given_model_name="sentence-transformers/all-MiniLM-L6-v2",
        chunk_size=1000,
        chunk_overlap=200
    ):
        self.chunker = Chunker(chunk_size, chunk_overlap)
        self.embedding_service = EmbeddingService(given_model_name)

        base_path = Path(__file__).resolve().parents[2]
        self.data_path = base_path / "data"

        self.pdf_loader = PDFLoader(self.data_path)
        self.vector_store = VectorStore(str(self.data_path), self.embedding_service)

        self.llm = ChatOllama(
            model="phi3.5",
            temperature=0
        )

    def get_available_pdfs(self):
        collections = self.vector_store.get_available_collections()
        return [c.replace("PDF_", "", 1) for c in collections]

    def ingest_pdf(self, file: UploadFile):
        text, file_name = self.pdf_loader.stream_pdf(file)
        return self.process_text(text, file_name)

    def load_pdf(self, file_name: str):
        text = self.pdf_loader.load_pdf(file_name)
        return self.process_text(text, file_name)

    def process_text(self, text: str, pdf_name: str):
        chunks = self.chunker.create_chunks(text)
        vectordb, created = self.vector_store.load_or_create_collection(pdf_name)
        if not created:
            return {"status": "already exists", "pdf": pdf_name}
        self.vector_store.add_documents(vectordb, chunks, pdf_name)
        return {
            "status": "ingested",
            "pdf": pdf_name,
            "chunks": len(chunks)
        }

    def resolve_query(self, question: str, pdf_name: str):
        print("PDF NAME:", pdf_name)
        vectordb, _ = self.vector_store.load_or_create_collection(pdf_name)
        docs = vectordb.similarity_search(question, k=3)
        print("DOC COUNT:", len(docs))
        context = "\n\n".join([doc.page_content for doc in docs])
        print("CONTEXT LENGTH:", len(context))
        print("CALLING LLM...")
        prompt = f"""/
        You are a helpful assistant. Answer ONLY from the context below.

        Context:
        {context}

        Question:
        {question}

        Answer:
        """
        response = self.llm.invoke(prompt)
        return response.content

    def refresh_data_pdfs(self):
        # 1. Get all PDF files from folder
        pdf_files = [
            f for f in self.data_path.iterdir()
            if f.is_file() and f.suffix.lower() == ".pdf"
        ]

        if not pdf_files:
            return {"status": "no_pdfs_found"}

        # 2. Existing collections
        existing_collections = set(self.vector_store.get_available_collections())

        ingested = []
        skipped = []
        failed = []

        # 3. Process each file
        for pdf_file in pdf_files:
            collection_name = normalize_pdf_name(pdf_file.name)

            if collection_name in existing_collections:
                skipped.append(pdf_file.name)
                continue

            try:
                result = self.load_pdf(pdf_file.name)
                ingested.append({
                    "pdf": pdf_file.name,
                    "chunks": result.get("chunks", 0)
                })
            except Exception as e:
                failed.append({
                    "pdf": pdf_file.name,
                    "error": str(e)
                })

        return {
            "status": "completed",
            "ingested_count": len(ingested),
            "skipped_count": len(skipped),
            "failed_count": len(failed),
            "ingested": ingested,
            "skipped": skipped,
            "failed": failed
        }