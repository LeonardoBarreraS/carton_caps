---
name: rag-context-evaluator
description: Evaluate retrieval context quality in a RAG system using recall and precision. Use this when diagnosing retriever failures, missing knowledge, noisy context, or poor chunking.
---

# RAG Context Evaluator

This skill evaluates whether the **retrieved context is appropriate** for answering a user query.

It measures the **retriever quality**, not the generator.

Core question:

Did we retrieve the right information in the right proportion?

This skill evaluates two dimensions:

- Recall (coverage of relevant knowledge)
- Precision (relevance of retrieved chunks)

If retrieval fails, generation cannot recover.  
Retriever quality is a **hard bottleneck** in RAG systems. :contentReference[oaicite:0]{index=0}

---

# When to use this skill

Use this skill when you need to:

- Debug poor RAG answers
- Evaluate retriever performance
- Diagnose missing knowledge
- Detect noisy context
- Tune chunking strategy
- Tune embedding model
- Tune top-k retrieval
- Improve hybrid search
- Evaluate context window efficiency

---

# Conceptual Model

Retriever = semantic information filter

User Query  
↓  
Retriever  
↓  
Context Chunks  
↓  
Generator  

Context evaluation verifies:

- Did we retrieve everything needed? (Recall)
- Did we retrieve only relevant chunks? (Precision)

---

# Dimension 1 — Recall (Coverage)

Recall measures:

Did we retrieve all relevant information needed to answer the question?

This detects **missing context**.

Low recall means:

- critical facts missing
- incomplete answers
- hallucination risk increases
- generator forced to guess

---

## Recall Evaluation Procedure

Step 1 — Identify Required Information

Determine what information is necessary to answer the query.

Example:

Query:
How do I reset enterprise SSO password?

Required knowledge:

- SSO reset steps
- enterprise-specific instructions
- authentication requirements

---

Step 2 — Inspect Retrieved Chunks

Check whether required information appears.

Retrieved:

Chunk 1 — general password reset  
Chunk 2 — account recovery  
Chunk 3 — MFA troubleshooting  

Missing:

SSO-specific documentation

---

Step 3 — Compute Recall

recall = relevant_retrieved / relevant_required

Example:

Required facts: 3  
Retrieved facts: 1  

Recall = 1 / 3 = 0.33

---

# Recall Failure Modes

## Missing Domain-Specific Knowledge

General embeddings fail in specialized domains.

Example:

Legal query → generic embeddings  
Result → missing legal clauses

---

## Top-k Too Small

Retriever returns insufficient context.

k=2  
But answer requires 5 chunks

---

## Chunking Too Small

Information fragmented across chunks.

Meaning lost across boundaries.

---

## Metadata Filtering Errors

Retriever filters out required documents.

Example:

filter = "public only"  
but answer requires "internal docs"

---

# Dimension 2 — Precision (Context Quality)

Precision measures:

Of retrieved chunks, how many are actually relevant?

This detects **noisy context**.

Low precision causes:

- cognitive overload
- hallucination increase
- attention dilution
- lost-in-the-middle effect

---

## Precision Evaluation Procedure

Step 1 — Inspect Retrieved Chunks

Example:

Query:
What are termination clauses?

Retrieved:

Chunk 1 — termination clause ✔  
Chunk 2 — termination clause ✔  
Chunk 3 — introduction ✖  
Chunk 4 — legal definitions ✖  
Chunk 5 — payment terms ✖  

---

Step 2 — Label Relevant vs Irrelevant

Relevant: 2  
Irrelevant: 3  

---

Step 3 — Compute Precision

precision = relevant_chunks / total_chunks

Precision = 2 / 5 = 0.4

---

# Precision Failure Modes

## Too Large Top-k

Too many irrelevant chunks retrieved.

k=20  
Only 3 relevant

---

## Weak Embedding Similarity

Semantic mismatch between query and documents.

---

## Poor Chunking Strategy

Chunks too large include mixed topics.

---

## Missing Reranking

Retriever returns approximate matches without ordering.

---

# Lost in the Middle Syndrome

Transformer attention is not uniform:

- beginning gets attention
- end gets attention
- middle gets degraded

Irrelevant chunks reduce visibility of relevant ones.

This is a **precision failure causing reasoning degradation**. :contentReference[oaicite:1]{index=1}

---

# Combined Context Score

You can combine recall and precision:

context_score = (recall + precision) / 2

Or weighted:

context_score = (0.6 * recall) + (0.4 * precision)

Use recall weight higher for safety-critical systems.

---

# Example Evaluation

Query:
How do I reset enterprise SSO password?

Retrieved:

1 general password reset ✔  
2 MFA troubleshooting ✖  
3 billing issue ✖  
4 SSO reset documentation ✔  

Required knowledge:

- SSO reset steps
- enterprise requirements

Evaluation:

Recall:

Retrieved relevant: 1  
Required: 2  

Recall = 0.5

Precision:

Relevant: 2  
Total: 4  

Precision = 0.5

Context Score = 0.5

Diagnosis:

Missing SSO detail + noisy context

---

# Output Schema

{
  "recall": float,
  "precision": float,
  "missing_information": [],
  "irrelevant_chunks": [],
  "diagnosis": "",
  "context_score": float
}

---

# Best Practices

Optimize recall first, then precision

Use hybrid search (vector + keyword)

Tune top-k dynamically

Use rerankers after retrieval

Use domain-specific embeddings

Use semantic chunking

Add metadata filters

Use query rewriting

---

# Tools & Frameworks

RAGAS  
- context precision metric  
- recall evaluation  

TruLens  
- chunk-level relevance scoring  

Haystack  
- retriever evaluation pipelines  

LlamaIndex  
- retrieval debugging tools  

FAISS  
- low-level retrieval control  

Weaviate / Pinecone / Chroma  
- vector retrieval tuning  

Elasticsearch / OpenSearch  
- hybrid retrieval  

Cohere Rerank  
- post-retrieval ranking

---

# Interpretation Guide

Recall | Meaning
------|--------
1.0 | all required info retrieved
0.7+ | acceptable coverage
0.4–0.7 | missing important context
<0.4 | retrieval failure

Precision | Meaning
---------|--------
1.0 | all chunks relevant
0.7+ | good signal-to-noise
0.4–0.7 | noisy context
<0.4 | severe noise

---

# Mental Model

Recall ensures:

required knowledge ⊆ retrieved context

Precision ensures:

retrieved context ⊆ relevant knowledge

Good RAG retrieval requires both:

high recall + high precision

Retriever guarantee:

"I fetched the right knowledge"