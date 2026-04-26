# Analysis: Evaluating RAG Retrieval Strategies

## Overview
This document details an experimental evaluation of Retrieval-Augmented Generation (RAG) pipelines, specifically focusing on the limitations of naive vector-based retrieval when applied to different types of source material. The objective was to analyze how query translation (MultiQuery) and context density affect model accuracy across distinct domains: narrative literature (*Pride and Prejudice*) and technical research (*Attention Is All You Need*).

## Methodology
The experiments utilized a MultiQuery translation strategy to expand the user's intent into five distinct retrieval queries. Retrieved context chunks were then fed into a Large Language Model (Phi-3.5) with strict instructions to answer based exclusively on the provided context.

## Experiment 1: Narrative Analysis (Pride and Prejudice)
The initial focus was on the qualitative analysis of literary themes, specifically identifying the antagonist in Jane Austen's *Pride and Prejudice*.

### Observations
- **k=1 Retrieval:** The model identified Lydia Bennet as the primary antagonist based on a retrieved chunk discussing her imprudent behavior.
- **k=5 Retrieval:** By increasing the context window, the model hallucinated a complex and incorrect backstory involving Mr. Darcy, Wickham, and father-driven jealousy.

### Findings
- **Context Starvation:** Naive vector search retrieved isolated dialogue snippets, lacking the "bird's-eye view" required for thematic interpretation.
- **Signal-to-Noise Ratio:** Increasing the chunk count ($k=5$) introduced excessive noise. The LLM attempted to synthesize incoherent narrative threads from unrelated paragraphs, leading to severe hallucinations.
- **Inference vs. Extraction:** When the literal answer to a thematic question is absent from the specific retrieved chunks, the model prioritizes its internal training weights over the prompt’s constraints, resulting in fabrications.

## Experiment 2: Technical Analysis (Attention Is All You Need)
The second experiment applied the same retrieval methodology to the foundational Transformer research paper.

### Observations
- **Result:** The system achieved high accuracy (9/10), providing a technically sound explanation of the Transformer architecture's advantages over Recurrent and Convolutional Neural Networks.

### Findings
- **Semantic Density:** Technical documents exhibit high keyword density. The retriever effectively matched the terminology in the question ("Transformer," "Attention") with relevant segments in the paper.
- **Explicit Content:** Unlike narrative literature, technical papers explicitly define their core thesis, allowing the retrieval of highly relevant, self-contained chunks that enable accurate generation without the need for global synthesis.

## LLM as judge
To ensure an objective assessment of the model's generated responses, a secondary, high-capability LLM (Gemini) was utilized as an automated "Judge." This approach allowed for the rapid evaluation of responses based on technical accuracy, logical consistency, and adherence to constraints.

## Conclusion and Strategic Implications
The results demonstrate that "more context" is not a universal solution for RAG pipelines.

1. **Domain Dependency:** Naive RAG is effective for technical, keyword-rich documentation but fails for abstract or narrative tasks where thematic synthesis is required.
2. **Retrieval Mismatch:** Simple vector-based chunking is insufficient for global understanding. Future iterations must explore advanced indexing strategies, such as:
   - **Summarization Chains:** Providing the model with high-level summaries alongside raw chunks.
   - **RAPTOR (Recursive Abstractive Processing for Tree-Organized Retrieval):** Building hierarchical trees to allow for retrieval at different levels of abstraction.
   - **Hybrid Search:** Combining vector similarity with keyword-based (BM25) search to improve retrieval accuracy.

This analysis highlights the critical need to match the retrieval strategy to the structure of the source material.
