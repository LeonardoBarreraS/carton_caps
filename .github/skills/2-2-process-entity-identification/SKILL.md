---
name: 2-2-process-entity-identification
description: Identifies and formalizes process entities from workflows, defining their lifecycle, states, and transitions at a conceptual level. Establishes stateful domain processes before structural modeling.
---

# Process Entity Identification

## Purpose
This skill transforms **workflows** into **process entities with explicit lifecycle**.

It defines:
- which workflows become domain processes
- lifecycle structure (states)
- transitions between states

This is a **refinement step of the domain ontology**, introducing **stateful process modeling**.

---

## Core Principle

Workflows describe transitions  
Process entities own those transitions  

A process entity is:
- a domain concept
- with identity
- with lifecycle
- with state transitions

---

## When to Use

Use this skill when:
- workflows are defined
- domain concepts are extracted
- before state model extraction (or in conjunction)
- before invariant detection
- before aggregate design

---

## Strict Rules

### DO NOT:
- define implementation (methods, code)
- define domain services
- define repositories
- define architecture
- define orchestration logic
- define infrastructure interactions

### ONLY DEFINE:
- process entities
- states
- transitions (conceptual)
- lifecycle meaning

---

## What is a Process Entity

A process entity:
- represents a workflow
- has identity
- has state
- evolves over time
- enforces lifecycle progression

Examples:
- Execution
- TrainingRun
- Evaluation
- Analysis

---

## Execution Methodology

Follow this reasoning pipeline:

---

### Step 1 — Select Candidate Workflows

From workflows:

Ask:
Which workflows represent:
- multi-step processes
- progression over time
- meaningful lifecycle

Only select workflows that:
- are not trivial
- involve state evolution

---

### Step 2 — Define Process Entity

For each selected workflow:

Define:
- entity name (semantic, not technical)
- what it represents

Example:
Workflow: submit → analyze → evaluate → respond  
Process Entity: Execution

---

### Step 3 — Extract States

From workflow steps:

Convert steps into **states**, not actions.

Example:
submit → analyze → respond  

States:
- created
- analyzing
- completed

Rules:
- states represent conditions, not actions
- must be finite and discrete

---

### Step 4 — Define Transitions

Define allowed transitions between states:

Format:
State A → State B

Example:
created → analyzing  
analyzing → completed  

Rules:
- transitions must be valid progressions
- no skipping unless explicitly allowed

---

### Step 5 — Identify Multiple Process Entities

Systems may have:
- primary process entity (core workflow)
- secondary process entities (supporting workflows)

Example:
- Execution (primary)
- Evaluation (secondary)

---

### Step 6 — Define Lifecycle Semantics

For each process entity, define:

- what starts the lifecycle
- how it progresses
- what completes it
- possible terminal states

---

### Step 7 — Validate Process Entity

A valid process entity must:
- represent a workflow
- have multiple states
- have transitions
- reflect real system behavior

Do NOT create if:
- single-step action
- stateless operation
- pure calculation

---

## Output Format (MANDATORY)

### Markdown

# Process Entity Identification

## Primary Process Entities

### Name: <Process Name>
Represents:
...

States:
- ...
- ...
- ...

Transitions:
- State A → State B
- State B → State C

Lifecycle Description:
...

---

## Secondary Process Entities

### Name: <Process Name>
Represents:
...

States:
- ...
- ...

Transitions:
- ...

Lifecycle Description:
...

---

### JSON

{
  "process_entities": [
    {
      "name": "",
      "type": "primary | secondary",
      "represents": "",
      "states": [],
      "transitions": [
        ["stateA", "stateB"]
      ],
      "lifecycle_description": ""
    }
  ]
}

---

## Completion Criteria

The skill is complete when:
- workflows are mapped to process entities
- each process entity has defined states
- transitions are explicitly defined
- lifecycle is clearly described
- trivial workflows are excluded
- no implementation details are introduced
- JSON output is valid and structured

---

## Key Insight

This skill transforms:

Workflow → Stateful process model

It introduces **time and evolution into the domain**, defining:

- how processes progress
- how state changes
- how behavior becomes lifecycle

This prepares:
- invariant detection
- aggregate design
- domain modeling

Process entities are the backbone of dynamic systems.

