---
name: 4-2-aggregate-implementation
description: Encodes aggregates as consistency boundaries in the domain layer, integrating entities (including process entities), invariants, and lifecycle behavior under the control of the aggregate root.
---

# 4.2 — Aggregate Implementation

## Purpose
Transform **aggregates (consistency boundaries)** into **domain-layer code structures** that:

- enforce invariants  
- control all state mutations  
- integrate lifecycle behavior (process entities)  
- guarantee consistency  

This ensures that all domain behavior is executed **safely within well-defined boundaries**.

---

## Core Principle

Aggregate = Consistency boundary  
Root = Control point  
All behavior (including lifecycle) must go through the root  

---

## Critical Rule

NO NEW SEMANTICS ARE CREATED IN THIS PHASE

This phase:
- encodes aggregates defined in Phase 2.5  
- integrates state models (Phase 2.3) and invariants (Phase 2.4)  
- does NOT introduce new entities, rules, or boundaries  

If new behavior appears:
→ Phase 2 is incomplete  

---

## When to Use

Use this skill when:
- aggregates are defined (Phase 2.5)
- invariants are defined (Phase 2.4)
- state models are defined (Phase 2.3)
- entities and value objects are encoded (Phase 4.1)

---

## Strict Rules

### DO NOT:
- introduce infrastructure (databases, frameworks, external systems)
- define application orchestration
- expose internal entities directly
- allow mutations outside the aggregate root

### ONLY DEFINE:
- aggregate root
- internal structure
- invariant enforcement
- lifecycle behavior (if applicable)
- controlled state transitions

---

## Conceptual Model

### Aggregate
A cluster of domain objects that must remain consistent.

---

### Aggregate Root
The only entry point that:
- controls all mutations  
- enforces invariants  
- protects the consistency boundary  

---

### Internal Objects
- entities (including process entities)  
- value objects  

Rules:
- cannot be modified externally  
- only accessible through the root  

---

## Lifecycle Integration (CRITICAL)

Process behavior must be implemented inside the aggregate.

---

### Case 1 — Process Entity = Aggregate Root

If the process defines the main lifecycle:

- it becomes the root  
- it contains the state  
- it implements transitions  

Example:

Execution Aggregate  
Root: Execution  

Methods:
- start()  
- complete()  
- fail()  

---

### Case 2 — Process Entity inside Aggregate

If lifecycle is part of a broader structure:

- process entity is internal  
- root controls transitions  
- root enforces invariants  

Example:

Order Aggregate  
Root: Order  

Contains:
- PaymentProcess  

Rules:
- no direct external access to process entity  
- root delegates but controls behavior  

---

### Decision Rule

IF process entity defines the main lifecycle  
→ make it the aggregate root  

ELSE  
→ keep it internal and controlled by the root  

---

## Execution Methodology

### Step 1 — Select Aggregate
From Phase 2.5:

Choose one aggregate.

---

### Step 2 — Define Aggregate Root

Define:
- root entity  

Ensure:
- it controls lifecycle  
- it enforces invariants  
- it is the only entry point  

---

### Step 3 — Define Internal Structure

Assign:

Entities:
- ...

Value Objects:
- ...

Process Entities (if applicable):
- ...

Rules:
- all objects belong exclusively to the aggregate  
- no external references to internal state  

---

### Step 4 — Integrate Lifecycle Behavior

From state models:

Define:
- state attribute  
- transition methods  

Rules:
- transitions follow the defined state model  
- transitions are invoked through the root  

---

### Step 5 — Enforce Invariants

From Phase 2.4:

Embed invariants into:
- root methods  
- transition logic  

Rules:
- invariants must always hold  
- violations must block execution  

---

### Step 6 — Enforce Access Control

Ensure:
- all mutations go through the root  
- no direct modification of internal entities  

Forbidden:
- public setters bypassing root  
- external mutation  

---

### Step 7 — Define Consistency Boundary

Ensure:
- all invariants are enforced inside the aggregate  
- no invariant depends on external aggregates  

If violated:
→ return to Phase 2.5  

---

### Step 8 — Validate Aggregate Integrity

Ensure:
- root controls all behavior  
- lifecycle is correctly integrated  
- invariants are always enforced  
- no external mutation exists  

---

## Output Format (MANDATORY)

### Markdown

# Aggregate Implementation

## Aggregate: <Name>

### Root
- <Root Entity>

---

### Internal Structure

Entities:
- ...
- ...

Value Objects:
- ...

Process Entities:
- ...

---

### Lifecycle Behavior

State:
- attribute: ...
- values:
  - ...
  - ...

Transitions (methods):
- ...
- ...

---

### Invariants Enforced
- ...
- ...

---

### Access Rules
- all mutations through root  
- no direct access to internal entities  

---

### Consistency Boundary
- description of what remains consistent  

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
      "state": {
        "attribute": "",
        "values": []
      },
      "transitions": [],
      "invariants": [],
      "consistency_boundary": ""
    }
  ]
}

---

## Completion Criteria

The skill is complete when:
- aggregate root is clearly defined  
- internal structure is correctly assigned  
- lifecycle behavior is integrated  
- invariants are enforced  
- all mutations go through root  
- no external access to internal state exists  
- no invariant crosses aggregate boundaries  
- JSON output is valid and structured  

---

## Key Insight

Consistency + Lifecycle → Controlled domain behavior  

Aggregates ensure:
- invariants are always preserved  
- lifecycle is controlled  
- domain remains consistent  

If implemented incorrectly:
- invariants break  
- lifecycle becomes inconsistent  
- system behavior becomes unreliable  

Aggregates are the core enforcement mechanism of the domain.

