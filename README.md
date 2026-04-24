# RAG - Basic PDF Reader

A lightweight Retrieval-Augmented Generation (RAG) API for querying PDF documents with local embeddings, persistent vector storage, and an Ollama-hosted LLM.

## Overview

This project is backend for document question answering. It ingests PDFs, splits them into chunks, stores embeddings in ChromaDB, retrieves the most relevant context for a query, and generates answers using a local language model through Ollama.

The goal of this project is to demonstrate the core building blocks of a practical RAG pipeline in a simple, inspectable codebase.

## What This Project Does

- Uploads or scans local PDF files for ingestion
- Extracts raw text from PDF documents
- Splits text into retrievable chunks
- Generates embeddings with `sentence-transformers/all-MiniLM-L6-v2`
- Stores vectors persistently in ChromaDB
- Retrieves relevant chunks for a user query
- Uses `phi3.5` via Ollama to answer from retrieved context
- Exposes the workflow through FastAPI endpoints

## Architecture

The current flow is:

1. PDF is uploaded through the API or discovered in the local `data/` folder.
2. `pypdf` extracts document text.
3. LangChain text splitters create chunks.
4. Hugging Face embeddings are generated for each chunk.
5. Chroma stores the embedded chunks in a persistent local collection.
6. A query runs similarity search against the selected PDF collection.
7. Retrieved context is passed to an Ollama-served LLM for final answer generation.

## Tech Stack

- `FastAPI` for the API layer
- `LangChain` for orchestration utilities
- `pypdf` for PDF parsing
- `sentence-transformers` for embeddings
- `ChromaDB` for persistent vector storage
- `Ollama` for local LLM inference

## Project Structure

```text
src/
├── controller/
│   └── RAGController.py
├── core/
│   ├── Chunker.py
│   ├── EmbeddingService.py
│   ├── Engine.py
│   ├── PDFLoader.py
│   ├── Sanitisers.py
│   └── VectorStore.py
└── main.py
```

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/pdf/checkPDFsAvailable` | List ingested PDF collections |
| `POST` | `/pdf/uploadPDF` | Upload and ingest a PDF |
| `GET` | `/pdf/refreshNewPDFsFromLocal` | Ingest PDFs found in `data/` |
| `GET` | `/pdf/resolveQuery` | Ask a question against a selected PDF |

## Local Setup

### 1. Create and activate a virtual environment

```bash
python3 -m venv myvenv
source myvenv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Ollama and pull the required model

```bash
ollama pull phi3.5
ollama serve
```

### 4. Run the FastAPI application

```bash
uvicorn src.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Example Usage

### Upload a PDF

```bash
curl -X POST "http://127.0.0.1:8000/pdf/uploadPDF" \
  -F "file=@data/your-file.pdf"
```

### Ask a question

```bash
curl "http://127.0.0.1:8000/pdf/resolveQuery?question=What%20is%20the%20main%20topic%3F&pdf_name=your-file.pdf"
```

## Why This Project Matters

This repository demonstrates practical understanding of:

- RAG system design fundamentals
- retrieval pipelines for unstructured documents
- local-first LLM workflows
- API-based productization of AI systems
- modular backend design for future extensibility

## V1 Shortcomings

### Known / Observed Shortcomings

- [ ] retrieval quality drops on complex or multi-part questions.
- [ ] queries only on single pdf at a time.
- [ ] chunking and retrieval parameters are static and cannot properly handle complex PDFs like with headers, footers, picture, etc.
- [ ] no token limiting. can cause slowness/unresponsivness.
- [ ] prompt is basic and lacks stronger guardrails against hallucination.
- [ ] duplicate detection is collection-name based, not content based.
- [ ] limited error handling and validation for malformed PDFs.
- [ ] no automated tests yet.
- [ ] no authentication, rate limiting, or production hardening.

## Author

**Anand Awasthi**

