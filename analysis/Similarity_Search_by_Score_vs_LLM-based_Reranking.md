# RAG Experiment: Similarity Search by Score vs LLM-based Reranking

## Objective
To evaluate whether **LLM-based reranking** improves answer quality over traditional **vector similarity search by score** in a basic RAG setup.

---

## Dataset
- **PDF 1:** *Little Women* — Louisa May Alcott  
- **PDF 2:** *Pride and Prejudice* — Jane Austen  

---

## Query
- **"may alcott vs jane austen"**

### Why this query is challenging
- Neither book references the other author.
- No direct comparison exists in source documents.
- Requires **cross-document reasoning + abstraction**, not just retrieval.
- No advanced RAG strategies (no metadata filtering, no query rewriting, no hybrid search).

---

## Approach

### 1. Baseline: Similarity Search (`similarity_search_with_score`)
- Retrieved **Top 3 chunks based on vector similarity score**
- Directly passed to LLM for answer generation

### 2. Improved: LLM-based Reranking
- Retrieved multiple chunks
- Used LLM to **rerank and retrieve top 3 relevant chunks based on query intent**
- Final answer generation

---

## Results

---

### Baseline Output (Similarity Search)

#### Retrieved Context (Top Chunks)
- Mostly **random narrative excerpts**
- Weak semantic alignment with query
- Included:
  - Dialogues from *Little Women*
  - Random passages from *Pride and Prejudice*
  - Only one high-level synopsis chunk

#### Final Answer
- "The context provided does not directly compare Alcott with Jane Austen..."

#### Analysis
- Retrieval failed to capture **comparative or high-level thematic content**
- LLM had **insufficient signal** to synthesize an answer
- Result: **Defensive / fallback response**

---

### LLM Reranking Output

#### Retrieved Context (After Reranking)
- Prioritized:
  - **Book summaries**
  - **High-level thematic descriptions**
- Included both:
  - Austen’s social satire and class themes
  - Alcott’s family and post-war themes

#### Final Answer
- "Jane Austen and Louisa May Alcott are two distinct authors... While both authors address women's experiences within societal expectations, they do so from different cultural perspectives and historical contexts."

#### Analysis
- LLM successfully:
  - Identified **relevant chunks across both books**
  - Extracted **themes and context**
  - Produced a **comparative answer despite no explicit comparison in data**
- Result: **Passable and meaningful answer**

---

## Key Observations

### 1. Similarity Search Limitation
- Embeddings favored **local textual similarity**, not **intent**
- Retrieved chunks were:
  - Fragmented
  - Contextually shallow
- Failed on **cross-document reasoning**

---

### 2. LLM Reranking Advantage
- Introduced **semantic understanding of query intent**
- Selected chunks that:
  - Represented **themes instead of raw text similarity**
- Enabled:
  - Better **context construction**
  - More **coherent generation**

---

### 3. Emergent Capability
Even with:
- No advanced RAG techniques
- No structured metadata
- No prompt engineering

LLM reranking enabled **implicit comparative reasoning**

---

## Conclusion

| Approach                     | Result Quality |
|----------------------------|---------------|
| Similarity Search          | Poor        |
| + LLM Reranking            | Significantly Better |

- LLM reranking transforms RAG from:
  - **"retrieve similar text"**
  - into **"retrieve useful context"**

- Particularly effective for:
  - Abstract queries
  - Cross-document reasoning
  - Non-explicit relationships

---

## Takeaway

- LLMs significantly improve the *selection* step.

---

