---
name: 2-1-domain-concept-extraction
description: Extracts domain concepts (entities, value objects, and process entities) from behaviors and workflows. Establishes the core ontology of the system without defining structure or implementation.
---

# Domain Concept Extraction

## Purpose
This skill transforms **behaviors and workflows** into a **domain ontology**.

It identifies:
- entities (state holders)
- value objects (pure meaning)
- process entities (lifecycle-driven concepts)
- domain language

This is the first step of Semantic Modeling.

---

## Core Principle

Workflows define what changes  
Concepts define what exists  

Behavior → Concepts

This skill defines **ontology**, not structure.

---

## When to Use

Use this skill when:
- workflows are defined
- behaviors are defined
- constraints are identified
- before state modeling
- before invariant detection
- before aggregate design
- before bounded context detection

---

## Strict Rules

### DO NOT:
- define aggregates
- define repositories
- define services
- define architecture
- define invariants
- define relationships between entities
- define implementation

### ONLY DEFINE:
- entities
- value objects
- process entities
- domain language

---

## Concept Types

### Entities
Objects that:
- have identity
- evolve over time
- hold mutable state
- participate in workflows

Examples:
- Request
- Execution
- Task
- Session

---

### Value Objects
Objects that:
- represent pure meaning
- are immutable
- have no identity
- validate themselves

Examples:
- Score
- Status
- Confidence
- Prompt
- Result

---

### Process Entities
Special entities that:
- represent workflows
- have lifecycle
- evolve through transitions
- encapsulate long-running processes

Examples:
- Execution
- TrainingRun
- Evaluation
- Analysis

---

## Execution Methodology

Follow this reasoning pipeline:

---

### Step 1 — Analyze Workflows

From workflows:

Ask:
- what changes over time?
- what evolves?
- what progresses?

These are candidates for entities.

---

### Step 2 — Identify Stateful Concepts

A concept is an entity if it:
- has lifecycle
- has state
- transitions between states
- persists across steps

Examples:
- Execution progresses
- Request is created and completed
- Evaluation evolves

---

### Step 3 — Identify Process Entities

If a workflow:
- has multiple steps
- has lifecycle
- represents a process

Then create a process entity.

Example:
submit → analyze → respond  
→ Process Entity: Execution

---

### Step 4 — Identify Value Objects

Look for:
- descriptive values
- immutable data
- semantic meaning

Examples:
- Score
- Confidence
- Result
- Status

---

### Step 5 — Extract Domain Language

Identify key domain terms used consistently.

These form the ubiquitous language.

Examples:
- Execution
- Evaluation
- Result
- Request
- Response

---

### Step 6 — Validate Concepts

Each concept must satisfy:

#### Entity
- has identity
- has lifecycle

#### Value Object
- immutable
- no identity

#### Process Entity
- represents workflow
- has transitions

Remove:
- technical terms
- redundant concepts
- implementation artifacts

---

## Output Format (MANDATORY)

### Markdown

# Domain Concept Extraction

## Process Entities
- Name: ...
  Description: ...
- Name: ...
  Description: ...

---

## Entities
- Name: ...
  Description: ...
- Name: ...
  Description: ...

---

## Value Objects
- Name: ...
  Description: ...
- Name: ...
  Description: ...

---

## Domain Language
- ...
- ...
- ...

---

### JSON

{
  "process_entities": [
    {
      "name": "",
      "description": ""
    }
  ],
  "entities": [
    {
      "name": "",
      "description": ""
    }
  ],
  "value_objects": [
    {
      "name": "",
      "description": ""
    }
  ],
  "domain_language": []
}

---

## Completion Criteria

The skill is complete when:
- process entities are identified
- entities are identified
- value objects are identified
- domain language is extracted
- concepts are consistent with workflows
- no structural or architectural decisions are made
- JSON output is valid and structured

---

## Key Insight

This skill transforms:

Behavioral system → Ontological system

It defines what exists in the system before defining:
- how it is structured
- how it is implemented

This is the foundation of domain-driven design.

Everything that follows depends on the correctness of this ontology.

