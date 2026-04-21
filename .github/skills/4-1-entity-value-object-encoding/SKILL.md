---
name: 4-1-entity-value-object-encoding
description: Encodes domain entities and value objects into pure domain-layer code structures, preserving semantics, state, and invariants without introducing infrastructure or application concerns.
---

# 4.1 — Entity & Value Object Encoding

## Purpose
Transform **domain concepts (entities and value objects)** into **code-level structures inside the domain layer**, preserving:

- identity
- state
- invariants
- semantic meaning

This is the **first step of Phase 4: Domain Materialization**.

---

## Core Principle

Semantic concepts → Code structures (1:1 mapping)

The code must:
- reflect the domain language
- enforce invariants
- remain independent of infrastructure and application layers

---

## Critical Rule

NO NEW SEMANTICS ARE CREATED IN THIS PHASE

This phase:
- encodes existing domain definitions  
- does NOT introduce new attributes, rules, or behaviors  

If something “new” appears:
→ Phase 2 is incomplete

---

## When to Use

Use this skill when:
- entities and value objects are defined (Phase 2.1)
- state models are defined (Phase 2.3)
- invariants are defined (Phase 2.4)
- aggregates are defined (Phase 2.5)
- architecture boundaries are defined (Phase 3)

---

## Strict Rules

### DO NOT:
- introduce infrastructure concerns (databases, APIs, frameworks)
- define application logic or orchestration
- modify or reinterpret invariants
- add attributes not defined in the semantic model

### ONLY DEFINE:
- entities (identity + mutable state)
- value objects (immutable meaning)
- attributes
- invariant enforcement at object level

---

## Conceptual Mapping

### Entity

An entity becomes:

- a class/object
- with a unique identity
- with mutable state
- with controlled state transitions

---

### Value Object

A value object becomes:

- an immutable structure
- self-validating
- equality by value (not identity)
- no lifecycle

---

## Execution Methodology

---

### Step 1 — Select Concept

From Phase 2.1:

Choose:
- one entity OR one value object

Process incrementally.

---

### Step 2 — Encode Identity (Entities Only)

Define:
- unique identifier
- identity field

Rules:
- identity is immutable
- equality is based on identity

---

### Step 3 — Encode Attributes (State)

From semantic definitions:

Define:
- all attributes exactly as modeled

Rules:
- no missing attributes
- no extra attributes
- names must match domain language

---

### Step 4 — Encode Value Objects

For each value object:

Define:
- immutable attributes
- constructor validation

Rules:
- no setters
- validation occurs at creation
- equality based on all attributes

---

### Step 5 — Enforce Invariants

From Phase 2.4:

Embed invariants into:

- constructors (creation rules)
- methods (transition rules)

Examples:
- invalid state → reject creation
- invalid transition → block operation

---

### Step 6 — Define Local Behavior

Entities may include behavior ONLY if:

- it modifies its own state
- it does not involve other aggregates
- it preserves invariants

DO NOT include:
- orchestration logic
- cross-aggregate coordination

---

### Step 7 — Enforce Immutability Rules

- value objects → fully immutable  
- entity identity → immutable  
- entity state → mutable only via controlled methods  

---

### Step 8 — Validate Semantic Fidelity

Ensure:
- code matches semantic definitions exactly
- no technical artifacts distort meaning
- invariants are correctly enforced

If mismatch:
→ return to Phase 2

---

## Output Format (MANDATORY)

### Markdown

# Entity & Value Object Encoding

## Entities

### Entity: <Name>

#### Identity
- ...

#### Attributes
- ...
- ...

#### Invariants Enforced
- ...
- ...

#### Behaviors
- ...
- ...

---

## Value Objects

### Value Object: <Name>

#### Attributes
- ...
- ...

#### Validation Rules
- ...
- ...

#### Immutability
- enforced

---

### JSON

{
  "entities": [
    {
      "name": "",
      "identity": "",
      "attributes": [],
      "invariants": [],
      "behaviors": []
    }
  ],
  "value_objects": [
    {
      "name": "",
      "attributes": [],
      "validation_rules": []
    }
  ]
}

---

## Completion Criteria

The skill is complete when:
- all entities are encoded with identity and state
- all value objects are immutable and validated
- invariants are enforced within objects
- no infrastructure or application logic is present
- code reflects semantic model exactly
- JSON output is valid and structured

---

## Key Insight

Ontology → Executable Domain Structures

This is the first irreversible step where:
- meaning becomes code  
- invariants become enforceable  
- concepts become concrete objects  

If done incorrectly:
- semantic drift occurs  
- invariants break  
- domain integrity collapses  

This is where the domain becomes executable truth.

