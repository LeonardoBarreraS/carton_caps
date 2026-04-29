# Carton Caps — AI Conversational Assistant
## Executive Summary

---

## What Carton Caps Is

Carton Caps is a school fundraising commerce platform that turns everyday grocery shopping into school donations. Parents buy products, choose a school, and a portion of every purchase flows directly to that school's fundraising fund. A referral program amplifies impact: when a parent invites another, both earn bonuses and the school's funding grows.

---

## The Business Problem

The platform works — but engagement is low. Users often don't know what to buy, don't understand how referrals generate donations, and lose motivation without clear guidance. The result: fewer purchases, fewer referrals, and lower fundraising outcomes for schools.

The platform lacks a mechanism to actively guide user decisions.

---

## The Solution: An AI Conversational Assistant

A stateful, context-aware AI chat agent that acts as a personal shopping guide and fundraising coach — embedded directly into the Carton Caps app.

The assistant:

- Learns each parent's preferences across the conversation
- Recommends products from the real catalog, personalized to the user and connected to their school
- Explains how the referral program works, clearly and accurately
- Asks focused clarifying questions when it needs more context to make a good recommendation

Every response is grounded in verified platform data — the assistant never fabricates products, prices, or referral rules.

---

## The Core Technical Challenge: Two Sources, Two Data Types

The assistant must answer two fundamentally different types of questions from two incompatible data sources:

| | Product Recommendations | Referral Guidance |
|---|---|---|
| **Source** | SQLite relational database | PDF policy documents |
| **Data type** | Structured rows (name, price, description) | Unstructured natural language (rules, FAQs, eligibility) |
| **Challenge** | Raw product rows are not semantically searchable | Rules split by page break lose their meaning |
| **Solution** | LLM enrichment: each product row is rewritten into a rich, searchable description before indexing | Semantic chunking: an LLM identifies self-contained rule units, preserving each rule's integrity |

Both sources are transformed into vector embeddings and stored in a semantic search engine (Qdrant). At query time, the assistant builds an enriched query from the user's full accumulated context — not just the raw message — and retrieves from the relevant source based on detected intent.

This architecture is called **Retrieval-Augmented Generation (RAG)**: the language model never answers from memory; it only responds with information it has explicitly retrieved.

---

## Business Impact

| Lever | How the assistant acts |
|---|---|
| **Purchase volume** | Guides indecisive users to products that match their family's needs |
| **Referral activation** | Explains the mechanics clearly, reducing confusion and drop-off |
| **Engagement** | Maintains a personalized, evolving conversation that improves with every message |
| **Donations** | Every additional purchase and referral translates directly into school funding |

---

## One-Sentence Summary

A context-aware AI assistant that retrieves verified product and program information from two heterogeneous data sources to guide parents toward purchases and referrals that increase school fundraising.
