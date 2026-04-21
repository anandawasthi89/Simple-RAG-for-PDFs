from langchain_community.vectorstores import Chroma

class VectorStore:
    def __init__(self, data_path, embedding_service):
        self.vectordb = Chroma(
            persist_directory=data_path,
            embedding_function=embedding_service.embeddings_model
        )

    def add_documents(self, chunks: list[str]):
        self.vectordb.add_texts(chunks)

    def query(self, question: str, k=3):
        return self.vectordb.similarity_search(question, k=k)