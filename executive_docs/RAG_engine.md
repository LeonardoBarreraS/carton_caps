# Carton Caps Conversational Assistant — RAG Engine Overview

> **RAG** (Retrieval-Augmented Generation) is the core AI mechanism of this system. It ensures every answer the assistant gives is grounded in real, retrieved knowledge — never invented by the language model from memory.

---

## Phase 1 — Ingestion (Offline, runs once)

> Loads knowledge into the vector store before the system goes live. Two independent pipelines run sequentially.

---

### Pipeline A — Product Catalog

- **Extract** — Products are read directly from the existing SQLite database (name, description, price).
- **Semantic enrichment** — An LLM rewrites each product row into a rich, searchable description that adds inferred labels: product category, meal occasions, dietary profile (kid-friendly, healthy, gluten-free), and budget tier — making each product a strong semantic search target, not just a table row.
- **Embed** — Each enriched product description is converted into a numerical vector using `text-embedding-3-small` (OpenAI).
- **Store** — The vector is stored in Qdrant's `product_catalog` collection alongside the original product metadata as a retrievable payload.

---

### Pipeline B — Referral Program Rules

- **Extract** — Referral program documents are loaded from PDF files stored in the `data/docs/` folder.
- **Semantic chunking** ⭐ — Instead of splitting text by character count or page breaks, an LLM reads the full document and identifies every **semantically self-contained unit**: individual rules, eligibility criteria, reward definitions, FAQ entries, and policy sections — each chunk stands alone and makes sense without reading anything else around it.
- **Embed** — Each semantic chunk is converted into a vector using the same `text-embedding-3-small` model.
- **Store** — The vector is stored in Qdrant's `referral_program_rules` collection with the chunk title, label, and source file as metadata.

> **Why semantic chunking matters:** A document split by character count would mix partial rules together, destroying their meaning. Semantic chunking preserves the integrity of each rule or FAQ — so when a user asks "how does the referral bonus work?", the system retrieves the exact, complete rule — not a fragment.

> **Critical alignment:** The **same embedding model** (`text-embedding-3-small`) is used at ingestion (write) and at query time (read). Using different models would cause the similarity search to return irrelevant results, since the vector spaces would not match.

---

## Phase 2 — Retrieval (Online, runs every conversation turn)

> Runs inside the AI pipeline every time a user sends a message that requires a product recommendation or referral guidance.

---

### The Retrieval Pipeline

```
User message
    │
    ▼
① Accumulate context          [Decision Intelligence]
   Preference signals extracted from the message and added to the growing DecisionContext.
    │
    ▼
② Evaluate context readiness  [Decision Intelligence]
   ─────────────────────────────────────────────────────────────────────────
   ► If context is insufficient → ask ONE clarifying question → retrieval skipped
   ─────────────────────────────────────────────────────────────────────────
    │
    ▼
③ Construct enriched query    [Decision Intelligence]
   A retrieval query is built from the full accumulated context (preferences, constraints, school, 
   past signals) — NEVER from the raw user message alone.
    │
    ▼
④ Route to correct source     [Decision Intelligence → Knowledge Retrieval]
   │── product intent   → queries the `product_catalog` collection
   └── referral intent  → queries the `referral_program_rules` collection
    │
    ▼
⑤ Semantic search             [Knowledge Retrieval / Qdrant]
   The query is embedded with `text-embedding-3-small` and the top-K most semantically 
   similar documents are returned as RetrievedEvidence.
    │
    ▼
⑥ ✅ EVALUATION GATE 1 — Context Quality   [Decision Intelligence]
   ┌─────────────────────────────────────────────────────────────────────────────┐
   │  context_recall_score    → Did retrieval find everything relevant?           │
   │  context_precision_score → Is what was retrieved actually relevant?          │
   │                                                                              │
   │  ► If recall score < threshold → query is REFINED and retrieval RETRIED      │
   │  ► Only evidence that passes both scores is injected into generation         │
   └─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
⑦ Generate grounded response  [Conversation Management / LLM]
   The language model (`gpt-4o`) receives the user message + retrieved evidence + 
   conversation context — and generates a response anchored to the retrieved content.
    │
    ▼
⑧ ✅ EVALUATION GATE 2 — Response Quality  [Conversation Management]
   ┌─────────────────────────────────────────────────────────────────────────────┐
   │  groundedness_score → Is every claim in the response traceable to           │
   │                       what was retrieved? (no hallucinations)               │
   │  relevance_score    → Does the response actually answer what the user asked?│
   │                                                                              │
   │  ► If either score < threshold → response is BLOCKED                        │
   │  ► A safe fallback message is returned instead                              │
   └─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
⑨ Deliver response + log metrics
   The validated response is returned to the user.
   All four scores (recall, precision, groundedness, relevance) are persisted 
   to `rag_metrics.sqlite` for every turn — enabling ongoing quality monitoring.
```

---

## The Four Quality Scores at a Glance

| Score | Stage | Question it answers | Action if it fails |
|-------|-------|--------------------|--------------------|
| `context_recall_score` | After retrieval | Did we find all the relevant content? | Refine query and retry retrieval |
| `context_precision_score` | After retrieval | Is everything we retrieved actually useful? | Combined with recall to gate injection |
| `groundedness_score` | After generation | Is the response based on retrieved data only? | Block response, return safe fallback |
| `relevance_score` | After generation | Does the response answer what was asked? | Block response, return safe fallback |
