from typing import List
from langchain_huggingface import HuggingFaceEmbeddings

class EmbeddingService:
    def __init__(self, given_model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.embeddings_model = HuggingFaceEmbeddings(model_name=given_model_name)

    def embed_documents(self, texts: List[str]):#just a helpful wrapper fuction, not actually being used right now.
        return self.embeddings_model.embed_documents(texts)

    def embed_query(self, query: str):#just a helpful wrapper fuction, not actually being used right now.
        return self.embeddings_model.embed_query(query)