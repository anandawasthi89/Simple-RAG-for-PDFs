from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from src.core.Sanitisers import normalize_pdf_name
import chromadb


class MemVectorStore:
    def __init__(self, embedding_service):
        self.embedding_function = embedding_service.embeddings_model
        self.client = chromadb.Client()

    def add_documents(self, chunks: list[Document]):
        vector_db = Chroma(
            client=self.client,
            collection_name="mem_collection",
            embedding_function=self.embedding_function,
        )
        return vector_db

