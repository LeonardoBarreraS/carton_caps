---
name: 2-5-aggregate-design
description: Defines aggregates and consistency boundaries from entities, state models, and invariants. Establishes transactional and consistency boundaries of the domain.
---

# Aggregate Design

## Purpose
This skill transforms **entities + state models + invariants** into **aggregates**.

It defines:
- consistency boundaries
- aggregate roots
- invariant enforcement scope
- controlled state mutation boundaries

Aggregates ensure that:

All invariants are preserved under controlled state changes.

---

## Core Principle

Entities define what exists  
State models define how they evolve  
Invariants define what must hold  
Aggregates enforce all of the above  

An aggregate is:
- a consistency boundary
- a unit of correctness
- a unit of state integrity

---

## When to Use

Use this skill when:
- domain concepts are defined
- process entities are defined
- state models are explicit
- invariants are identified
- before bounded context detection
- before domain implementation

---

## Strict Rules

### DO NOT:
- define repositories or persistence
- define infrastructure or frameworks
- define application logic or orchestration
- define APIs or controllers
- define technical transactions

### ONLY DEFINE:
- aggregates
- aggregate roots
- contained entities/value objects
- consistency boundaries
- invariant enforcement scope

---

## What is an Aggregate

An aggregate is:
- a cluster of domain objects
- with a single entry point (aggregate root)
- that enforces invariants
- and controls all mutations inside it

---

## Key Concepts

### Aggregate Root
- the main entity
- the only entry point for modifications
- enforces invariants

### Consistency Boundary
- defines what must always be consistent
- all invariants inside boundary must hold

### Internal Objects
- entities and value objects inside aggregate
- cannot be modified externally

---

## Execution Methodology

Follow this reasoning pipeline:

---

### Step 1 — Identify Invariant Scope

From invariants:

Ask:
Which concepts must remain consistent together?

Group entities that share invariants.

Example:
Execution + Result must be consistent  
→ same aggregate

---

### Step 2 — Define Aggregate Boundaries

Group:
- entities
- value objects
- process entities

Into consistency clusters.

Each cluster becomes an aggregate.

Rules:
- strong consistency inside
- weak consistency outside

---

### Step 3 — Select Aggregate Root

Choose one entity as root.

Criteria:
- central in lifecycle
- controls state changes
- referenced externally

Example:
Execution Aggregate → Root: Execution

---

### Step 4 — Assign Internal Components

Define what belongs inside aggregate:

- entities
- value objects
- process entities (if applicable)

Rules:
- no external direct access
- all changes go through root

---

### Step 5 — Assign Invariants to Aggregates

For each aggregate:

Define:
- which invariants it enforces
- which states it protects

Example:
Execution Aggregate enforces:
- valid state transitions
- result must exist when completed

---

### Step 6 — Validate Boundary Integrity

Ensure:
- no invariant spans multiple aggregates
- no shared mutable state between aggregates

If invariant crosses boundary:
→ aggregates are incorrectly defined

---

### Step 7 — Validate Aggregate Design

A valid aggregate must:
- enforce all its invariants
- have a clear root
- have a clear boundary
- be independent from other aggregates

---

## Output Format (MANDATORY)

### Markdown

# Aggregate Design

## Aggregates

### Aggregate: <Name>

#### Root
- ...

#### Contains

Entities:
- ...
- ...

Value Objects:
- ...

Process Entities:
- ...

#### Enforced Invariants
- ...
- ...

#### Consistency Boundary
- description of what must remain consistent

---

## Aggregate Relationships

- Aggregate A references Aggregate B (by identifier only)
- Aggregate C depends on Aggregate A (no shared state)

---

### JSON

{
  "aggregates": [
    {
      "name": "",
      "root": "",
      "entities": [],
      "value_objects": [],
      "process_entities": [],
      "invariants": [],
      "consistency_boundary": ""
    }
  ],
  "relationships": []
}

---

## Completion Criteria

The skill is complete when:
- aggregates are clearly defined
- each aggregate has a root
- consistency boundaries are explicit
- invariants are assigned correctly
- no invariant crosses aggregates
- aggregates do not share mutable state
- JSON output is valid and structured

---

## Key Insight

This skill transforms:

Domain concepts + invariants → Consistency boundaries

It defines:
- where correctness is enforced
- how state changes are controlled
- how the domain maintains integrity

Without aggregates:
- invariants cannot be reliably enforced
- state becomes inconsistent
- system behavior becomes unstable

Aggregates are the core unit of domain correctness.

