import os
from src.core.Chunker import Chunker
from src.core.EmbeddingService import EmbeddingService
from src.core.PDFLoader import PDFLoader
from src.core.VectorStore import VectorStore
from pathlib import Path
from langchain_ollama import ChatOllama


class Engine:
    def __init__(
        self,
        given_model_name="sentence-transformers/all-MiniLM-L6-v2",
        chunk_size=1000,
        chunk_overlap=200
    ):
        self.chunker = Chunker(chunk_size, chunk_overlap)
        self.embeddingService = EmbeddingService(given_model_name)

        base_path = Path(__file__).resolve().parents[2]
        data_path = base_path / "data"

        self.vectorStore = VectorStore(str(data_path), self.embeddingService)

        # LLM (phi via Ollama)
        self.llm = ChatOllama(
            model="phi3.5",
            temperature=0,
            # other params...
        )

    def process(self, data_file: str):
        pdf_loader = PDFLoader(data_file)
        combined_text = pdf_loader.load_pdf()

        chunks = self.chunker.create_chunks(combined_text)

        self.vectorStore.add_documents(chunks)

    def resolve_query(self, question: str):
        # 1. Retrieve relevant chunks
        docs = self.vectorStore.query(question)

        # Extract text content
        context = "\n\n".join([doc.page_content for doc in docs])

        # 2. Build prompt
        prompt = f"""\
        You are a helpful assistant. Answer the question based only on the context below.
        
        Context:
        {context}
        
        Question:
        {question}
        
        Answer:
        """

        # 3. Call LLM
        response = self.llm.invoke(prompt)

        return response