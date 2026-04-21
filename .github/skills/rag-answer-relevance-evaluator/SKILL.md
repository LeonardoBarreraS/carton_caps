---
name: rag-answer-relevance-evaluator
description: Evaluate whether a RAG answer actually solves the user's question. Use this when detecting misaligned answers, partial responses, or goal drift in RAG systems.
---

# RAG Answer Relevance Evaluator

This skill evaluates whether the **generated answer actually addresses the user's intent**.

This is not a retrieval metric.  
This is not a groundedness metric.  

This is an **intent alignment metric**.

Core Question:

Does the answer solve the user's problem?

Even if:

- retrieval is perfect  
- answer is grounded  

The system can still fail if the answer does not address the user's intent. :contentReference[oaicite:0]{index=0}

---

# When to use this skill

Use this skill when you need to:

- detect partially answered questions
- detect irrelevant responses
- evaluate intent alignment
- detect goal drift
- detect over-answering
- evaluate RAG usefulness
- score answer quality
- validate user satisfaction
- detect task mismatch

---

# Conceptual Model

Answer relevance measures **semantic alignment** between:

User Question (Q)  
Generated Answer (A)

The key idea:

If an answer is relevant, it should answer the same question.

This becomes a **bidirectional validation problem**.

---

# Reverse Question Technique

This is the core evaluation method.

Step 1 — Inputs

Q = original question  
A = generated answer  

---

Step 2 — Reverse Engineer Question

Use evaluator LLM to generate:

Q' = "What question would this answer respond to?"

---

Step 3 — Compare Questions

Compute semantic similarity:

similarity(Q, Q')

---

Step 4 — Compute Relevance Score

High similarity → high relevance  
Low similarity → misalignment

This tests:

"If this answer existed independently, what question would it answer?"

If that inferred question differs from original intent → failure. :contentReference[oaicite:1]{index=1}

---

# Evaluation Pipeline

## Step 1 — Capture Original Question

Example:

Q:
"What caused the drop in sales in Q2?"

---

## Step 2 — Generated Answer

A:
"Sales dropped by 15% in Q2."

---

## Step 3 — Reverse Question

Evaluator produces:

Q':
"What was the percentage drop in sales in Q2?"

---

## Step 4 — Compare

Original intent:
cause of drop

Answer intent:
amount of drop

Mismatch → low relevance

---

# Relevance Score

relevance = similarity(Q, Q')

Example:

Similarity = 0.42  
Relevance Score = 0.42

Low relevance.

---

# Failure Modes

## Partial Answer

Answer addresses only part of the question.

Question:
Why did revenue increase?

Answer:
Revenue increased by 12%

Missing: cause

---

## Task Mismatch

Answer performs wrong task.

Question:
Summarize document

Answer:
Explains methodology

---

## Over-answering

Answer expands beyond user intent.

Question:
List 3 benefits

Answer:
Long essay about topic

---

## Wrong Focus

Answer addresses related but different question.

Question:
How to reset SSO password?

Answer:
How to change account password

---

# Example Evaluation

Question:
"What caused the drop in sales in Q2?"

Answer:
"Sales dropped by 15% in Q2."

Reverse Question:
"What was the drop in sales in Q2?"

Comparison:

Original → cause  
Reverse → magnitude  

Relevance = low

Evaluation:

Faithful ✓  
Grounded ✓  
Relevant ✗

This is a **goal misalignment failure**. :contentReference[oaicite:2]{index=2}

---

# Alternative Scoring Method (Embedding Similarity)

Compute:

embedding(Q)  
embedding(Q')

Then:

cosine_similarity(Q, Q')

Score:

0–1

---

# Output Schema

{
  "original_question": "",
  "generated_answer": "",
  "reverse_question": "",
  "similarity_score": float,
  "relevance_score": float,
  "diagnosis": ""
}

---

# Best Practices

Use reverse-question evaluation

Evaluate semantic intent, not keywords

Penalize partial answers

Penalize wrong task responses

Penalize over-generation

Combine with groundedness for full evaluation

Track relevance over time

Use embedding similarity

---

# Tools & Frameworks

RAGAS  
- answer relevance metric  
- embedding similarity  

DeepEval  
- LLM-based relevance evaluators  

SentenceTransformers  
- semantic similarity scoring  

OpenAI Evals  
- custom evaluation pipelines  

LangSmith  
- query-answer alignment tracking

---

# Interpretation Guide

Score | Meaning
------|--------
1.0 | perfectly aligned
0.8+ | highly relevant
0.6–0.8 | mostly relevant
0.4–0.6 | partially relevant
0.2–0.4 | weak alignment
<0.2 | irrelevant answer

---

# Mental Model

Groundedness ensures:

answer ⊆ context

Context evaluation ensures:

context contains required knowledge

Answer relevance ensures:

answer solves the right problem

Three guarantees:

Retrieval → right knowledge  
Grounding → correct use of knowledge  
Relevance → correct problem solved

Answer relevance is the **goal alignment layer** of RAG systems.