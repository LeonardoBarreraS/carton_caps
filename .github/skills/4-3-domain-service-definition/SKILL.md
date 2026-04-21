---
name: 4-3-domain-service-definition
description: Encodes domain services as pure domain-layer constructs that encapsulate domain logic not belonging to a single aggregate, ensuring invariant preservation and semantic clarity without introducing orchestration or infrastructure concerns.
---

# 4.3 — Domain Service Definition

## Purpose
Transform **domain logic that does not belong to a single aggregate or entity** into **domain services** within the domain layer.

It defines:
- cross-aggregate domain logic  
- domain computations  
- invariant-preserving operations  

This ensures that:

All domain logic is **correctly placed, cohesive, and semantically explicit**.

---

## Core Principle

Entities & Aggregates → own local behavior  
Domain Services → handle cross-entity domain logic  

A domain service exists ONLY when logic:

- cannot be assigned to a single aggregate  
- still belongs to the domain (not application)  

---

## Critical Rule

NO NEW SEMANTICS ARE CREATED IN THIS PHASE

This phase:
- encodes domain logic already identified in Phase 2  
- does NOT introduce new rules, workflows, or behaviors  

If new domain rules appear:
→ Phase 2 is incomplete  

---

## When to Use

Use this skill when:
- aggregates are implemented (Phase 4.2)
- invariants are defined (Phase 2.4)
- domain logic spans multiple aggregates or entities
- logic cannot be placed inside an aggregate root

---

## Strict Rules

### DO NOT:
- implement application workflows or orchestration  
- call external systems or infrastructure  
- manage persistence or transactions  
- violate aggregate boundaries  

### ONLY DEFINE:
- pure domain logic  
- cross-aggregate operations (conceptually)  
- domain-level computations  

---

## What is a Domain Service

A domain service is:

- stateless  
- deterministic  
- expressed in domain language  
- independent of infrastructure  

---

## When to Create a Domain Service

Create a domain service ONLY if:

The logic:
- involves multiple aggregates  
OR  
- does not naturally belong to a single entity  

Otherwise:
→ place logic inside the aggregate root  

---

## Execution Methodology

---

### Step 1 — Identify Candidate Logic

From Phase 2:

Ask:
- does this logic belong to one aggregate?  

If NO:
→ candidate for domain service  

---

### Step 2 — Validate Correct Placement

Ensure:
- logic cannot be placed in an entity or aggregate  
- logic is NOT orchestration  

If it is orchestration:
→ belongs to Application Layer (Phase 5)

---

### Step 3 — Define Service Responsibility

Define:
- a clear domain purpose  
- operation name using domain language  

Examples:
- computeScore  
- validateExecution  
- compareResults  

---

### Step 4 — Define Inputs and Outputs

Inputs:
- entities or value objects  

Outputs:
- value objects or domain results  

Rules:
- no DTOs  
- no infrastructure types  

---

### Step 5 — Encode Domain Logic

Implement:
- domain rules  
- computations  
- validations  

Ensure:
- invariants are respected  
- no side effects outside domain  

---

### Step 6 — Enforce Statelessness

Ensure:
- no internal state  
- no persistence  
- no hidden dependencies  

---

### Step 7 — Validate Boundaries

Ensure:
- no direct modification of multiple aggregates  
- no invariant violation across aggregates  

---

## Output Format (MANDATORY)

### Markdown

# Domain Service Definition

## Service: <Name>

### Purpose
- ...

---

### Inputs
- ...
- ...

---

### Output
- ...

---

### Domain Rules Applied
- ...
- ...

---

### Invariants Preserved
- ...
- ...

---

### Constraints
- stateless  
- no infrastructure  
- no orchestration  

---

### JSON

{
  "domain_services": [
    {
      "name": "",
      "purpose": "",
      "inputs": [],
      "output": "",
      "rules": [],
      "invariants": []
    }
  ]
}

---

## Completion Criteria

The skill is complete when:
- domain services are defined only where necessary  
- logic cannot be assigned to aggregates  
- services are stateless and pure  
- invariants are preserved  
- no orchestration or infrastructure is introduced  
- JSON output is valid and structured  

---

## Key Insight

Unassigned domain logic → Explicit domain services  

This skill ensures:
- proper placement of domain logic  
- avoidance of overloaded aggregates  
- clarity of responsibilities  

Without domain services:
- logic becomes scattered  
- aggregates become bloated  
- domain loses coherence  

Domain services maintain the integrity of domain logic across boundaries.

