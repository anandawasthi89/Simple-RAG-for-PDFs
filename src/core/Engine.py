from pathlib import Path
from fastapi import UploadFile
from langchain_ollama import ChatOllama

from src.core.Chunker import Chunker
from langchain_core.documents import Document
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
    
    def resolve_multiPDF_query(self, question: str, pdf_names: list[str]):
        all_docs = []

        for pdf_name in pdf_names:
            vectordb, _ = self.vector_store.load_or_create_collection(pdf_name)
            docs = vectordb.similarity_search_with_score(question, k=3)
            all_docs.extend(docs)
        
        print(all_docs)

        # Global ranking across PDFs
        ranked = sorted(all_docs, key=lambda x: x[1])  # Chroma: lower = better

        top_docs = [doc for doc, _ in ranked[:3]]
        print("DOC COUNT:", len(top_docs))
        context = "\n\n".join([doc.page_content for doc in top_docs])
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
    
    def resolve_multiPDF_query_llm(self, question: str, pdf_names: list[str]):
        all_docs = []

        for pdf_name in pdf_names:
            vectordb, _ = self.vector_store.load_or_create_collection(pdf_name)
            docs = vectordb.similarity_search_with_score(question, k=3)
            all_docs.extend(docs)

        print(f"all_docs: {all_docs}")

        top_docs = self.get_context_from_llm(all_docs,question)
        print(f"top_docs: {top_docs}")
        print("DOC COUNT:", len(top_docs))
        context = "\n\n".join([doc[0].page_content for doc in top_docs])
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
    
    def get_context_from_llm(self, docs: list[Document], question: str):
        chunkarr = [doc[0].page_content for doc in docs]

        formatted_chunks = "\n\n".join(
            [f"{i+1}. {chunk}" for i, chunk in enumerate(chunkarr)]
        )

        prompt = f"""
        You are a ranking assistant.

        Select the 3 most relevant chunks for answering the question.

        Return ONLY the numbers (comma-separated), nothing else.

        Question:
        {question}

        Chunks:
        {formatted_chunks}

        Answer:
        """

        response = self.llm.invoke(prompt)
        content = response.content.strip()

        # Example: "2,5,1"
        try:
            indices = [int(x.strip()) - 1 for x in content.split(",")]
            selected_docs = [docs[i] for i in indices if i < len(docs)]
        except:
            # fallback: take first 3
            selected_docs = sorted(docs, key=lambda x: x[1])[:3]

        return selected_docs
    
    def resolve_query_using_multiquery(self, question: str, pdf_names: str):
        generatedQueries = self.generate_multi_query(question)
        return self.generate_from_multiquery(generatedQueries,pdf_names, question)
        
    def generate_multi_query(self, question: str):
        prompt = f"""/
        You are an AI language model assistant. 
        Your task is to generate five different versions of the given user question to retrieve relevant documents from a vector database. 
        By generating multiple perspectives on the user question, your goal is to help the user overcome some of the limitations of the distance-based similarity search. Provide these alternative questions separated by newlines. 
        Original question: {question}
        note: Only generate the questions separated by new lines. no numbering, sequencing, etc/
        """

        response = self.llm.invoke(prompt)
        content = response.content.strip()
        return content.split("\n")

    def generate_from_multiquery(self, generatedQueries: list[str], pdf_name: str, question: str):
        print("PDF NAME:", pdf_name)
        all_doc=[]
        for query in generatedQueries:
            vectordb, _ = self.vector_store.load_or_create_collection(pdf_name)
            doc = vectordb.similarity_search(query, k=1)
            all_doc.extend(doc)
        print("DOC COUNT:", len(all_doc))
        context = "\n\n".join([doc.page_content for doc in all_doc])
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
    
    def resolveQueryUsingRFP(self, question: str, pdf_name: str):
        generatedQueries = self.generate_multi_query(question)
        ranked_docs = self.generate_ranked_docs_using_RFP(generatedQueries, pdf_name)

        context = "\n\n".join(ranked_docs)
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
    
    def resolveQueryUsingQueryDecomposition(self, question: str, pdf_name: str):
        decomposed_queries = self.generate_query_decomposition(question)
        current_answer = ""
        print(decomposed_queries)
        for query in decomposed_queries:
            current_answer = self.generate_sub_query(query, current_answer, pdf_name)
            print(current_answer)
        return self.generate_final_response(question, current_answer)
    
    def resolveQueryUsingQueryDecomposition2(self, question: str, pdf_name: str):
        decomposed_queries = self.generate_query_decomposition(question)
        all_context = {}
        print(decomposed_queries)
        for query in decomposed_queries:
            current_answer = self.resolve_query(query, pdf_name)
            all_context[query] = current_answer
        print(all_context)
        return self.generate_final_response2(question, all_context)
    
    def generate_final_response2(self, question: str, all_context: dict):
        
        context = "\n".join(
            f"--- [FINDING {i}] ---\nQuestion: {q}\nAnswer: {a}" 
            for i, (q, a) in enumerate(all_context.items(), 1)
        )

        print("CALLING LLM...")
        prompt = f"""
        You are an expert synthesizer. Your task is to provide a final, comprehensive answer to the original question by distilling the provided research findings.

        ---
        RESEARCH FINDINGS (from sub-question analysis):
        {context}
        ---

        ORIGINAL QUESTION:
        {question}

        ---
        INSTRUCTIONS:
        1. Synthesize: Integrate these findings into a unified, coherent response. Do not simply list or repeat the sub-answers.
        2. Grounding: Answer ONLY using the information provided in the RESEARCH FINDINGS. Do not rely on external knowledge.
        3. Logical Flow: Ensure the final response flows logically and addresses all components of the original question.
        4. If the provided findings are insufficient to answer the original question, state that clearly rather than hallucinating.

        Final Answer:
        """
        response = self.llm.invoke(prompt)
        return response.content

    def generate_final_response(self, question: str, context: str):
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
        
    def generate_query_decomposition(self, question: str):
        prompt = f"""/
        You are an expert AI assistant tasked with breaking down complex user queries into a sequential set of logical sub-questions. 

        Your goal is to decompose the following user question into 3-5 manageable sub-questions that can be answered one by one. 
        - Ensure that each sub-question relies only on information that could be retrieved independently or from the answers to previous sub-questions.
        - The sub-questions must follow a logical flow of reasoning.
        - Do not include the original question in the output.
        - Output ONLY the questions, separated by newlines. No numbering, no sequencing markers, no introduction, and no extra text.

        Original Question: {question}/
        """

        response = self.llm.invoke(prompt)
        content = response.content.strip()
        return content.split("\n")
    
    def generate_sub_query(self, question: str, current_answer, pdf_name):
        vectordb, _ = self.vector_store.load_or_create_collection(pdf_name)
        docs = vectordb.similarity_search(question, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])
        current_knowledge = f"""/
        ---
        CURRENT KNOWLEDGE STATE:
        {current_answer}/
        """ if current_answer != "" else ""

        prompt = f"""/
        You are an expert AI assistant. Your goal is to provide a concise answer to the current sub-question by integrating your existing knowledge of the topic with the new context provided.

        {current_knowledge}
        ---

        NEW RETRIEVED CONTEXT:
        {context}
        ---

        CURRENT SUB-QUESTION:
        {question}

        ---
        Instructions:
        1. Synthesize the 'NEW RETRIEVED CONTEXT' and 'CURRENT KNOWLEDGE STATE' to answer the 'CURRENT SUB-QUESTION'.
        2. If the answer is not in the context or state, state "Information not available."
        3. Output only the answer.

        Answer:
        """

        response = self.llm.invoke(prompt)
        content = response.content.strip()
        return content.split("\n")
    
    def generate_ranked_docs_using_RFP(self, generatedQueries: list[str], pdf_name: str, k=60):
        all_docs_ranked = {}
        for query in generatedQueries:
            vectordb, _ = self.vector_store.load_or_create_collection(pdf_name)
            docs = vectordb.similarity_search(query, k=10)
            for ind, doc in enumerate(docs):
                all_docs_ranked[doc.page_content] = all_docs_ranked.get(doc.page_content, 0) + 1/(k+ind+1)
            print(f"all_docs: {all_docs_ranked}")
        return sorted(all_docs_ranked, key=all_docs_ranked.get)[:3]
    
    def resolveQueryUsingStepBack(self, question: str, pdf_name: str):
        step_back_query = self.get_step_back_query(question)
        step_context = self.resolve_stepback_query(step_back_query,pdf_name)
        return self.resolve_combined_query(question,step_context,pdf_name)
    
    def get_step_back_query(self, question: str):
        print("CALLING LLM...")
        prompt = f"""/
        You are an expert AI assistant tasked with creating a stepback (more comprehensive) question for the below provided question. 

        Your goal is to ONLY provide one question from the following user question. 
        - Ensure that question is more comprehensive without changing the core meaning.
        - Do not include the original question in the output.
        - Output ONLY the question. No numbering, no sequencing markers, no introduction, and no extra text.

        Original Question: {question}/
        """
        response = self.llm.invoke(prompt)
        return response.content

    def resolve_stepback_query(self, question: str, pdf_name: str):
        print("PDF NAME:", pdf_name)
        vectordb, _ = self.vector_store.load_or_create_collection(pdf_name)
        docs = vectordb.similarity_search(question, k=5)
        print("DOC COUNT:", len(docs))
        context = "\n\n".join([doc.page_content for doc in docs])
        print("CONTEXT LENGTH:", len(context))
        print("CALLING LLM...")
        prompt = f"""/
        You are a helpful assistant. Answer using the world knowledge and from the context below.

        Context:
        {context}

        Question:
        {question}

        Answer:
        """
        response = self.llm.invoke(prompt)
        return response.content
    
    def resolve_combined_query(self, question: str, step_context, pdf_name: str):
        print("PDF NAME:", pdf_name)
        vectordb, _ = self.vector_store.load_or_create_collection(pdf_name)
        docs = vectordb.similarity_search(question, k=3)
        print("DOC COUNT:", len(docs))
        context = "\n\n".join([doc.page_content for doc in docs])
        print("CONTEXT LENGTH:", len(context))
        print("CALLING LLM...")
        prompt = f"""/
        You are a helpful assistant. Answer ONLY using the two contexts provided below.

        WiderContext:
        {step_context}

        Context:
        {context}

        Question:
        {question}

        Answer:
        """
        response = self.llm.invoke(prompt)
        return response.content
    
    def get_embedding_context(self, question: str):
        prompt = f"""/
        System: You are a professional search query optimizer. 
        Your goal is to rewrite the user's question into a search query that maximizes the chance of retrieving the correct answer from a document.

        Instructions:
        1. Do not answer the question.
        2. If the question is ambiguous, make the query specific to the context of a literary analysis.
        3. Return ONLY the search query.

        User Question: {question}

        Search Query:
        """
        response = self.llm.invoke(prompt)
        return response.content
    
    def resolveQueryUsingHyDE(self, question: str, pdf_name: str):
        embedding_context = self.get_embedding_context(question)
        print("embedding_context:", embedding_context)
        vectordb, _ = self.vector_store.load_or_create_collection(pdf_name)
        docs = vectordb.similarity_search(embedding_context, k=8)
        print("DOC COUNT:", len(docs))
        context = "\n\n".join([doc.page_content for doc in docs])
        print("CONTEXT LENGTH:", len(context))
        print("CALLING LLM...")
        prompt = f"""/
        System: You are an expert research assistant. 
        Your task is to answer the user's question using ONLY the provided context.

        Context: 
        {context}

        Question: 
        {question}

        Instructions:
        1. Use ONLY the information provided in the "Context" section.
        2. If the answer is not explicitly found in the context, you MUST state: "The provided document does not contain sufficient information to answer this question." 
        3. Do not use outside knowledge or make assumptions about characters or plots not mentioned in the context.
        4. Keep the answer concise and professional.
        5. Do not include phrases like "Based on the document."

        Answer:
        """
        response = self.llm.invoke(prompt)
        return response.content