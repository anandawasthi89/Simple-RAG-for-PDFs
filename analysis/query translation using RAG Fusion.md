# Analysis: Evaluating RAG Fusion Strategy

## Overview
Following the evaluation of basic MultiQuery RAG, this experiment implemented **RAG Fusion** to address retrieval limitations. The objective was to determine if reconciling multiple query paths via Reciprocal Rank Fusion (RRF) could improve context synthesis for both narrative literature and technical documentation.

## Methodology
- **Query Translation:** Each original question was expanded into five distinct sub-queries.
- **Retrieval:** Each sub-query performed a similarity search in the vector database with `k=10`, resulting in 50 candidate documents.
- **Ranking:** The candidate list was aggregated using the RRF algorithm with a constant `k=60` to calculate consensus scores.
- **Generation:** The top 3 ranked documents were passed to the LLM (Phi-3.5) as the final context.

## Experiment Results

### 1. Narrative Context (Pride and Prejudice)
- **Outcome:** The system failed to identify the main antagonist correctly, hallucinating trait misattributions (e.g., assigning Darcy's pride to Bingley) and misinterpreting character roles.
- **Analysis:** Despite the more sophisticated ranking, the system remained trapped by **context starvation**. The retrieved chunks were isolated snippets of dialogue or plot points. RRF successfully aggregated common documents across queries, but because *none* of the retrieved chunks contained a high-level summary of the novel's antagonist, the system could not synthesize an accurate response.

### 2. Technical Context (All You Need Is Attention)
- **Outcome:** The system achieved high accuracy (8/10), producing a precise technical explanation of Transformer architecture and performance benchmarks.
- **Analysis:** The RRF ranking correctly prioritized chunks containing specific technical data (e.g., BLEU scores, parallelization benefits). However, the model exhibited **pre-training leakage**, incorporating external knowledge (e.g., mentioning BERT) that was not present in the provided source text.

## Findings & Evaluation (LLM-as-a-Judge)

| Metric | Narrative (P&P) | Technical (Attention) |
| :--- | :--- | :--- |
| **Accuracy** | Low (2/10) | High (8/10) |
| **Reasoning** | Fragmented/Hallucinated | Technically Sound |
| **Constraint Adherence** | Failed (Forced Synthesis) | Mostly Successful |

*Note: The judge noted that RAG Fusion alone is insufficient to overcome the lack of global thematic context in literary works.*

## Conclusion
While RAG Fusion provides a superior ranking mechanism compared to naive MultiQuery by filtering out noise via consensus, it remains fundamentally constrained by the **quality of retrieved context**.

- **RAG Fusion is not a "Context Generator":** It organizes existing information but cannot create information that is not present in the raw chunks. 
- **The "Full Picture" Problem:** For narrative/abstract documents, the retrieval must be augmented by structural strategies (e.g., summaries, RAPTOR, or Knowledge Graphs) that represent global context.
- **Pre-training Bias:** Technical queries benefit from high-density keywords, but the system must be strictly governed via system prompts to prevent external knowledge leakage when absolute grounding is required.

These experiments confirm that RAG Fusion is an effective **reranking optimization** but should be viewed as one component in a broader, multi-layered RAG architecture.