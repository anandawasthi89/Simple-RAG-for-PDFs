# Analysis of RAG Query Translation (Step-Back Strategy)

This document provides an analysis of two RAG generation cases that utilized a "Step-Back" query translation strategy, evaluated using an LLM-as-a-judge framework.

## Case 1: Relationship Analysis in Literature
- **Question:** "how would you describe the relation between Elizabeth Bennet and Fitzwilliam Darcy?"
- **Document:** `pride-and-prejudice-jane-austen.pdf`
- **Result:** Score 2.75/5
- **Observations:**
    - The model exhibited significant hallucinations regarding character identities (confusing Jane Bennet with Georgiana Darcy).
    - The model attempted to link thematic elements ("patronage in the church") that were not supported by the core context.
    - **Failure Mode:** While the "Step-Back" strategy is intended to provide broader context, the model likely suffered from high internal bias (confusing the book plot with its own training data) and failed to ground the response specifically in the provided document chunks.

## Case 2: Comparative Architecture Analysis
- **Question:** "key differences between different Transformers"
- **Document:** `all_attention.pdf`
- **Result:** Score 3.25/5
- **Observations:**
    - The model correctly identified hyper-parameter differences within the *original* Transformer architecture but failed to address the broader landscape of "Transformer variants" (e.g., Encoder-only vs. Decoder-only).
    - **Failure Mode:** The retrieval scope was likely too narrow. Because the RAG system only had access to the original "Attention Is All You Need" paper, it could not answer the user's intent to compare *different* modern architectures.

## Comparative Findings

| Feature | Case 1 (Literature) | Case 2 (Technical) |
| :--- | :--- | :--- |
| **Primary Issue** | Hallucination/Mixing external data | Scope constraint/Lack of relevant data |
| **Strategy Success**| Low: "Step-back" triggered noise | Moderate: "Step-back" triggered hyper-parameter focus |
| **Improvement Path**| Implement grounded citation/verification | Expand corpus to include comparative literature |

## Conclusion
The "Step-Back" strategy shows promise in theory but presents clear risks in practice:

1.  **Over-Generalization:** In both cases, the step-back prompt caused the model to reach for "general knowledge" rather than relying on the source document.
2.  **Corpus Dependency:** A step-back strategy is only as good as the documents provided. If the corpus is singular (as in both cases), the "step-back" often leads to a recursive analysis of the same narrow text, which may not be the intent of the user.
3.  **Recommendations:**
    - **For RAG Reliability:** Implement a "Strict Faithfulness" constraint (System Prompting) requiring explicit citations.
    - **For Retrieval:** Ensure the document corpus matches the level of abstraction requested by the user. If asking for comparisons, the retrieval must return comparative documentation, not just foundational papers.
    - **Verification:** Introduce a secondary validation step that checks generated names and classifications against the retrieved context before displaying the output to the user.