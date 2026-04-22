from langchain_community.vectorstores import Chroma
from src.core.Sanitisers import normalize_pdf_name
import chromadb


class VectorStore:
    def __init__(self, data_path, embedding_service):
        self.data_path = data_path
        self.embedding_function = embedding_service.embeddings_model
        self.client = chromadb.PersistentClient(path=data_path)

    def get_available_collections(self):
        return [c.name for c in self.client.list_collections()]

    def load_or_create_collection(self, pdf_name: str):
        collection_name = normalize_pdf_name(pdf_name)

        exists = collection_name in self.get_available_collections()

        vectordb = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embedding_function,
        )

        return vectordb, not exists  # created = not exists

    def add_documents(self, vectordb, chunks: list[str], pdf_name: str):
        vectordb.add_texts(
            chunks,
            metadatas=[{"source": pdf_name}] * len(chunks)
        )