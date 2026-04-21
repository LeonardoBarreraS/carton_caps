---
name: 2-6-bounded-context-detection
description: Identifies semantic boundaries in the domain by grouping concepts, aggregates, and processes into bounded contexts with clear ownership and independent meaning.
---

# Bounded Context Detection

## Purpose
This skill transforms **aggregates + domain concepts + invariants** into **bounded contexts**.

It defines:
- semantic boundaries
- ownership of meaning
- separation of domain models
- context-level responsibilities

Bounded contexts ensure that:

Each part of the system has a **consistent and independent meaning**.

---

## Core Principle

Different parts of the system have different meanings  
These meanings must be isolated  

A bounded context is:
- a semantic boundary
- a consistency of language
- a unit of ownership
- a boundary of independent evolution

---

## When to Use

Use this skill when:
- aggregates are defined
- domain concepts are known
- invariants are defined
- before architecture design
- before component mapping

---

## Strict Rules

### DO NOT:
- define architecture layers
- define modules or components
- define repositories or infrastructure
- define APIs or communication mechanisms

### ONLY DEFINE:
- contexts
- ownership
- grouping of domain concepts
- semantic boundaries

---

## What is a Bounded Context

A bounded context defines:
- a domain language
- a set of aggregates
- entities and value objects
- invariants
- processes
- ownership of meaning

Each context must be:
- internally consistent
- externally decoupled

---

## Execution Methodology

Follow this reasoning pipeline:

---

### Step 1 — Group Concepts by Meaning

From:
- entities
- value objects
- process entities
- aggregates

Group concepts that share the same meaning.

Example:
Execution + Result + Request → Execution context  
Evaluation + Score → Evaluation context  

---

### Step 2 — Identify Ownership

For each group:

Ask:
Who owns this meaning?

Define:
- what the context decides
- what it controls
- what it is responsible for

Ownership defines the boundary.

---

### Step 3 — Detect Language Differences

If the same term has different meanings:
→ split contexts

Example:
"Result" in execution ≠ "Result" in evaluation

This implies:
different contexts

---

### Step 4 — Detect Invariant Boundaries

If invariants differ:
→ separate contexts

Rule:
Each context must enforce its own invariants independently.

---

### Step 5 — Validate Aggregate Alignment

Ensure:
- each aggregate belongs to exactly one context
- no aggregate spans multiple contexts

If an aggregate spans contexts:
→ context definition is incorrect

---

### Step 6 — Define Context Responsibilities

For each context define:
- what it owns
- what it decides
- what it exposes (conceptually)

---

### Step 7 — Define Context Map

Define relationships between contexts.

Format:
Context A → Context B

Meaning:
- A depends on B
- A interacts with B

Rules:
- avoid bidirectional dependencies
- keep relationships minimal

---

### Step 8 — Validate Context Independence

Each context must:
- have its own language
- have its own invariants
- evolve independently

If not:
→ contexts are incorrectly defined

---

## Output Format (MANDATORY)

### Markdown

# Bounded Context Detection

## Contexts

### Context: <Name>

#### Owns
- ...

#### Aggregates
- ...
- ...

#### Entities
- ...
- ...

#### Value Objects
- ...
- ...

#### Process Entities
- ...
- ...

#### Invariants
- ...
- ...

#### Responsibilities
- ...
- ...

---

## Context Map

- Context A → Context B
- Context B → Context C

---

## Context Relationships Description
- explanation of interactions
- dependency reasoning

---

### JSON

{
  "contexts": [
    {
      "name": "",
      "owns": [],
      "aggregates": [],
      "entities": [],
      "value_objects": [],
      "process_entities": [],
      "invariants": [],
      "responsibilities": []
    }
  ],
  "context_map": [
    ["ContextA", "ContextB"]
  ],
  "description": ""
}

---

## Completion Criteria

The skill is complete when:
- contexts are clearly identified
- ownership is defined
- aggregates are correctly assigned
- invariants are isolated per context
- no aggregate spans multiple contexts
- context relationships are defined
- contexts are semantically independent
- JSON output is valid and structured

---

## Key Insight

This skill transforms:

Domain model → Semantic boundaries

It defines:
- where meaning changes
- where models must be separated
- how the system is divided conceptually

Without bounded contexts:
- domain models become inconsistent
- meanings overlap and conflict
- system evolution becomes chaotic

Bounded contexts are the foundation of scalable domain design.

