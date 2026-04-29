# Analysis: Evaluating Query Decomposition and Synthesis Strategies in RAG Pipelines

## Executive Summary
This analysis evaluates the efficacy of two distinct RAG (Retrieval-Augmented Generation) strategies—**State-Based Accumulation** and **Full-History Collector Synthesis**—in the context of complex query decomposition. The objective was to determine which architecture yields more accurate, grounded, and synthesized responses for both literary and technical datasets.

---

## Methodology

### 1. State-Based Accumulation
* **Approach:** The output of each sub-question answer was stored as a cumulative "knowledge buffer" (state) and passed into the next sub-question retrieval and generation step.
* **Final Step:** The final state plus the original question was passed to the LLM for synthesis.

### 2. Full-History Collector Synthesis
* **Approach:** All sub-questions and their corresponding answers were collected as discrete findings.
* **Final Step:** All findings were passed as a consolidated context block alongside the original question to the LLM for synthesis.

---

## Comparative Performance Analysis

### Literary Dataset: *Pride and Prejudice*
| Metric | State-Based Accumulation | Full-History Collector Synthesis |
| :--- | :--- | :--- |
| **Score** | 6.5 / 10 | 9.2 / 10 |
| **Key Issues** | Introduced hallucinated content ("young Lucas"). | Excellent synthesis; grounded and coherent. |
| **Observation** | State compression led to loss of context-specific boundary control. | Full history provided the LLM with sufficient data to synthesize and maintain constraints. |

### Technical Dataset: *Attention Is All You Need*
| Metric | State-Based Accumulation | Full-History Collector Synthesis |
| :--- | :--- | :--- |
| **Score** | 7.5 / 10 | 8.5 / 10 |
| **Key Issues** | Incomplete technical explanation (missed Positional Encodings). | Improved structural narrative but still lacked technical precision. |
| **Observation** | Suffered from context window "forgetting" crucial architectural nuances. | Provided a clearer narrative flow but remained imprecise on specific mechanisms. |

---

## Critical Insights

### 1. The Synthesis Bottleneck
The experiment revealed that the final synthesis step is the most critical component of a RAG pipeline. While state-based accumulation is memory-efficient, it frequently leads to information dilution. The **Full-History Collector** approach proved superior as it allowed the synthesis model to cross-reference multiple findings simultaneously, reducing hallucinations.

### 2. Grounding and Boundary Control
A recurring challenge was the "Entity Strictness" problem. When the synthesis prompt lacked explicit constraints, the LLM tended to introduce extraneous information. Implementing strict instructions—specifically prohibiting information not found in the provided context—was essential to achieving scores above 9.0.

### 3. Technical Imprecision
In technical domains, RAG systems are prone to "thematic drift." When asked about specific mechanisms (e.g., maintaining word order in Transformers), the LLM preferred generic architectural concepts (Residual Connections/Normalization) over specific mechanisms (Positional Encodings). This indicates that even with high-quality synthesis, the **Retrieval phase** must be explicitly guided to surface specific technical components.



---

## Conclusion
The **Full-History Collector Synthesis** strategy consistently outperformed the State-Based Accumulation method in both literary and technical domains. By providing the synthesis LLM with the full set of sub-question findings, the system is better equipped to maintain grounding, resolve conflicts between sub-answers, and produce a unified response.

For future iterations, I recommend implementing a **Two-Tiered Retrieval Strategy**:
1.  **Decomposition & Parallel Retrieval:** Extract facts to address individual components of a complex query.
2.  **Guided Synthesis:** Utilize a prompt that explicitly demands specific technical mechanisms (e.g., forcing a search for "Positional Encoding" when discussing Transformer order) to bridge the gap between general synthesis and technical accuracy.

This pipeline architecture provides a robust framework for handling multi-hop reasoning tasks, ensuring that the model remains grounded in retrieved evidence while providing high-level analytical synthesis.