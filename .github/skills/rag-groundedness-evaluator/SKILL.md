---
name: rag-groundedness-evaluator
description: Evaluate whether a RAG answer is strictly grounded in retrieved context. Use this when validating hallucinations, claim traceability, and evidence consistency in RAG systems.
---

# RAG Groundedness / Faithfulness Evaluation

This skill evaluates whether a generated answer is **strictly supported by the retrieved context**.

Groundedness is not about factual correctness in the real world.  
It is about **epistemic traceability**: every claim must be supported by retrieved evidence.

A response can be:

- Correct but ungrounded (hallucination that happens to be true)
- Incorrect but grounded (retrieved source is wrong but faithfully used)

Groundedness is the **first guarantee** in a RAG system:
Retrieval → Grounded generation → Relevant answer

---

# When to use this skill

Use this skill when you need to:

- Detect hallucinations in RAG outputs
- Verify claims against retrieved context
- Evaluate LLM answer faithfulness
- Score groundedness for RAG evaluation
- Build evaluation pipelines for RAG systems
- Validate compliance-sensitive outputs
- Implement LLM-as-judge groundedness scoring

---

# Conceptual Model

Groundedness evaluates:

Are all claims in the answer supported by retrieved context?

This becomes a **claim verification pipeline**:

Answer → Claims → Evidence → Entailment → Score

Groundedness = epistemic constraint on generation

---

# Evaluation Pipeline

## Step 1 — Claim Extraction

Decompose the answer into atomic factual statements.

Example:

Answer:
"The revenue grew 20% in Q1 due to expansion in LATAM"

Claims:

Claim 1: Revenue grew 20% in Q1  
Claim 2: Growth due to LATAM expansion

Each claim must be independently verifiable.

---

## Step 2 — Evidence Entailment Check

For each claim:

Check whether the retrieved context supports it.

This is a Natural Language Inference (NLI) problem:

Claim vs Retrieved Context

Possible outcomes:

- Supported
- Contradicted
- Not found

Only "Supported" counts as grounded.

---

## Step 3 — Groundedness Score

Compute:

groundedness = supported_claims / total_claims

Example:

Claims: 4  
Supported: 3  

Score = 3 / 4 = 0.75

---

# Failure Modes

## Hallucination Leakage

Model introduces knowledge not in context.

Example:

Context:
"Revenue increased due to pricing adjustments"

Answer:
"Revenue increased due to LATAM expansion"

→ hallucinated cause

---

## Over-Generalization

Model extends beyond available evidence.

Context:
"Revenue increased in Brazil"

Answer:
"Revenue increased across LATAM"

→ unsupported generalization

---

## Compression Artifacts

Summarization distorts meaning.

Context:
"Revenue increased 5% in Q1"

Answer:
"Revenue increased significantly"

→ semantic distortion

---

# Example Evaluation

User Question:
Why did revenue increase last quarter?

Retrieved Context:
"Revenue increased due to pricing changes in Europe."

Generated Answer:
"Revenue increased due to pricing changes and LATAM expansion."

Claims:

1. Revenue increased due to pricing changes
2. Revenue increased due to LATAM expansion

Evaluation:

Claim 1 → Supported  
Claim 2 → Not supported  

Groundedness = 1 / 2 = 0.5

---

# LLM-as-Judge Template

Input:

Question  
Retrieved Context  
Generated Answer  

Task:

1. Extract claims
2. Verify each claim
3. Compute groundedness score
4. Return structured evaluation

Output schema:

{
  "claims": [],
  "supported": [],
  "unsupported": [],
  "score": float
}

---

# Best Practices

- Evaluate at claim level, not whole answer
- Use atomic factual statements
- Do not check real-world correctness
- Only use retrieved context as truth source
- Penalize missing evidence
- Penalize hallucinated causes
- Penalize added details not in context

---

# Tools & Frameworks

RAGAS  
- Built-in groundedness metric  
- Claim extraction + verification  

DeepEval  
- Faithfulness evaluators  
- CI/CD integration  

LangSmith  
- Trace-based groundedness evaluation  

TruLens  
- Feedback functions for grounding  

LlamaIndex  
- Built-in groundedness scoring  

---

# Interpretation Guide

Score | Meaning
------|--------
1.0 | Fully grounded
0.8+ | Mostly grounded
0.5–0.8 | Partial hallucination
0.2–0.5 | Major hallucination
<0.2 | Unreliable answer

---

# Mental Model

Retriever → provides knowledge  
Generator → produces claims  
Groundedness → validates claims  

Groundedness ensures:

answer ⊆ retrieved context

If not → hallucination

This is the **epistemic safety layer** of RAG systems.