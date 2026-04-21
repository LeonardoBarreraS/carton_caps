---
name: 3-1-context-to-component-mapping
description: Maps bounded contexts into architectural components, defining implementation boundaries that preserve semantic integrity and enforce isolation of domain meaning.
---

# Context → Component Mapping

## Purpose
This skill transforms **bounded contexts (semantic boundaries)** into **architectural components (implementation boundaries)**.

It defines:
- component boundaries
- ownership of domain logic
- isolation of semantics
- dependency direction between components

This is the first step of **Structural Design**, where architecture is used to **protect meaning**, not create it.

---

## Core Principle

Bounded Context = Semantic Boundary  
Component = Implementation Boundary  

Architecture must reflect and preserve the semantic boundaries defined in Phase 2.

---

## Critical Rule

NO NEW DOMAIN SEMANTICS ARE CREATED IN THIS PHASE

This phase:
- maps meaning → structure  
- does NOT invent meaning  

If new entities, invariants, or workflows appear here:
→ Phase 2 is incomplete

---

## When to Use

Use this skill when:
- bounded contexts are defined
- aggregates are assigned to contexts
- invariants are isolated per context
- domain model is semantically complete

This skill comes before:
- Layered Architecture Generation  
- Context Communication Design  

---

## Strict Rules

### DO NOT:
- define new domain concepts
- modify aggregates or invariants
- define infrastructure or frameworks
- define APIs or technical details
- merge contexts arbitrarily

### ONLY DEFINE:
- components
- mapping from contexts → components
- ownership boundaries
- dependency direction

---

## Conceptual Model

Each bounded context is:
- a unit of meaning

Each component is:
- a unit of implementation that protects that meaning

A component must fully encapsulate its context.

---

## Mapping Strategy

### Default Mapping

1 bounded context → 1 component  

---

### Allowed Variations

Merge contexts ONLY if:
- they share the same language
- they share invariants
- they evolve together

Split context ONLY if:
- it contains independent subdomains
- invariants and lifecycle are separable

---

## Execution Methodology

Follow this reasoning pipeline:

---

### Step 1 — List Bounded Contexts

Input:
- contexts from Phase 2

Each context already defines:
- aggregates
- invariants
- domain language
- ownership

---

### Step 2 — Preserve Semantic Ownership

For each context, extract:

- what it owns
- what it decides
- what it controls

These must remain intact in the component.

---

### Step 3 — Define Components

Map each bounded context to a component.

Format:

Context → Component

Example:
Execution Context → execution-component  
Evaluation Context → evaluation-component  

---

### Step 4 — Define Component Responsibility

Each component must:

- own its domain model  
- contain its aggregates  
- enforce its invariants  

Each component must NOT:

- include other context logic  
- enforce cross-context invariants  

---

### Step 5 — Define Dependency Direction

Dependencies must reflect semantic needs:

Component A → Component B  
ONLY if A depends on B meaning

Rules:
- no bidirectional dependencies  
- no circular dependencies  
- no shared domain objects  
- dependencies must be minimal  

---

### Step 6 — Define Isolation Rules

Each component must:

- encapsulate its domain  
- expose only necessary interfaces (conceptually)  
- prevent internal leakage  

Forbidden:
- shared entities  
- shared value objects  
- shared aggregates  

---

### Step 7 — Define Module Structure (High-Level)

Define structural grouping:

/components  
/<component-a>  
/<component-b>  
/<component-c>  

Each component must be:
- independent  
- self-contained  
- aligned with one context  

---

### Step 8 — Validate Structural Integrity

Ensure:
- each component maps to one context  
- no invariant crosses components  
- no domain logic is shared  
- dependencies are acyclic  
- boundaries reflect semantic isolation  

If violated:
→ return to bounded context detection

---

## Output Format (MANDATORY)

### Markdown

# Context → Component Mapping

## Mapping

- Context: <Name> → Component: <component-name>
- Context: <Name> → Component: <component-name>

---

## Component Responsibilities

### <Component Name>
- owns: ...
- controls: ...
- enforces: ...

---

## Dependencies

- Component A → Component B
- Component B → Component C

---

## Structural Rules

- no shared domain models
- no shared invariants
- explicit dependencies only

---

## Module Structure

/components  
/<component-a>  
/<component-b>  
/<component-c>  

---

### JSON

{
  "mapping": [
    {
      "context": "",
      "component": ""
    }
  ],
  "components": [
    {
      "name": "",
      "owns": [],
      "controls": [],
      "enforces": []
    }
  ],
  "dependencies": [
    ["ComponentA", "ComponentB"]
  ],
  "module_structure": []
}

---

## Completion Criteria

The skill is complete when:
- each bounded context is mapped to a component
- semantic ownership is preserved
- dependencies are defined and acyclic
- no domain logic crosses components
- no invariant crosses components
- structure reflects semantic boundaries
- JSON output is valid and structured

---

## Key Insight

This skill transforms:

Semantic boundaries → Structural boundaries

It ensures:
- meaning is isolated
- domain integrity is preserved
- architecture reflects the domain

If this mapping is incorrect:
- semantics will leak
- coupling will increase
- system evolution will degrade

This is the first point where architecture can either:
- protect meaning  
- or silently destroy it

