---
name: 1-1-goal-scope-definition
description: Defines the system objective, boundaries, actors, inputs/outputs, high-level workflow, and constraints from a problem statement. Establishes the semantic foundation of the system.
---

# Goal & Scope Definition

## Purpose
This skill transforms an unstructured problem into a **formal system framing artifact**.

It defines the system as a **black-box transformation**:
INPUT → SYSTEM → OUTPUT

This is the first and mandatory step before:
- requirements
- workflows
- domain modeling
- architecture

---

## Core Principle
A system must be defined by:
- its purpose (WHY)
- its boundary (INSIDE vs OUTSIDE)
- its interactions (WHO + WHAT)
- its behavior skeleton (WORKFLOW)
- its constraints (LIMITS)

---

## When to Use
Use this skill when:
- starting a new system
- receiving a vague problem description
- requirements are unclear
- before any design or modeling

---

## Strict Rules

### DO NOT:
- define entities
- define domain concepts
- define architecture
- define invariants
- define implementation details
- define detailed workflows

### ONLY DEFINE:
- purpose
- boundary
- actors
- inputs/outputs
- high-level workflow
- constraints

---

## Execution Methodology

Follow this reasoning pipeline strictly:

---

### Step 1 — Define System Objective

Extract the core transformation.

#### Mandatory format:
SYSTEM transforms X → Y

Also include:
The system is responsible for ...

#### Validation:
- X = observable input
- Y = observable output
- avoid vague wording

---

### Step 2 — Define System Boundary

Separate:

#### Inside the System:
- decisions
- transformations
- system behavior

#### Outside the System:
- users
- external systems (APIs, LLMs, DBs)
- UI
- data sources

---

### Step 3 — Identify Actors

#### Primary Actor:
- initiates system behavior

#### Secondary Actors:
- support execution

Classify secondary actors as:
- external_system
- data_source
- service

---

### Step 4 — Define Inputs and Outputs

#### Inputs:
- commands
- events
- data
- prompts

#### Outputs:
- responses
- decisions
- state changes
- events

---

### Step 5 — Define High-Level Workflow

Define minimal semantic pipeline:

step → step → step

#### Rules:
- each step = meaningful transformation
- no technical steps
- no implementation details
- no micro-steps

---

### Step 6 — Identify System Constraints

Define high-level constraints:

#### Types:
- Behavioral: what must NOT happen
- Input: required input conditions
- Output: expected output conditions
- Operational (optional): limits, latency, frequency

---

## Output Format (MANDATORY)

### 1. Markdown

# Goal & Scope Definition

## System Objective
SYSTEM transforms X → Y  
The system is responsible for ...

## System Boundary
### Inside
- ...
### Outside
- ...

## Actors
### Primary Actor
- ...
### Secondary Actors
- ... (type: external_system | data_source | service)

## Inputs
- ...

## Outputs
- ...

## High-Level Workflow
step → step → step

## Constraints
- ...
- ...

---

### 2. JSON

{
  "objective": {
    "transformation": "X -> Y",
    "description": "..."
  },
  "boundary": {
    "inside": [],
    "outside": []
  },
  "actors": {
    "primary": [],
    "secondary": [
      {
        "name": "",
        "type": "external_system | data_source | service"
      }
    ]
  },
  "inputs": [],
  "outputs": [],
  "workflow": [],
  "constraints": []
}

---

## Completion Criteria

The skill is complete when:
- objective is explicit and testable
- boundary is clearly defined
- actors are classified
- inputs/outputs are concrete
- workflow is minimal and semantic
- constraints are identified
- JSON is valid and structured

