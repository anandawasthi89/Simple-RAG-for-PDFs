from langchain_community.vectorstores import Chroma
from src.core.Sanitisers import normalize_pdf_name
import chromadb


class MemVectorStore:
    def __init__(self, embedding_service):
        self.embedding_function = embedding_service.embeddings_model
        self.client = chromadb.Client()
        self.vectordb = Chroma(
            client=self.client,
            collection_name="mem_collection",
            embedding_function=self.embedding_function,
        )