---
name: 2-3-state-model-extraction
description: Defines explicit state models for process entities and identifies state and transitions in all relevant domain entities, establishing a complete and unambiguous representation of system evolution.
---

# 2.3 — State Model Extraction

## Purpose
Transform **process entities** into **explicit state models**, and extend state reasoning to **all domain entities that evolve over time**.

It defines:
- complete state space  
- valid transitions  
- invalid transitions  
- lifecycle boundaries  
- state-dependent constraints  

This ensures that:

System evolution is **explicit, controlled, and semantically consistent**.

---

## Core Principle

Process entities define that something evolves  
State models define how it evolves  

All entities may have state  
Process entities make it explicit  

---

## Critical Insight

State modeling exists at two levels:

### Level 1 — Explicit State Machines (Primary)
Applied to:
- process entities  

Defines:
- full lifecycle  
- finite states  
- explicit transitions  

---

### Level 2 — Implicit State Structures (Secondary)
Applied to:
- entities and aggregates  

Defines:
- state attributes  
- allowed transitions  
- invariant-driven constraints  

These may not be full state machines, but they still:
- evolve over time  
- must remain valid  

---

## When to Use

Use this skill when:
- process entities are identified  
- domain concepts are defined  
- workflows are modeled  
- before invariant detection  
- before aggregate design  

---

## Strict Rules

### DO NOT:
- define methods or implementation  
- define aggregates or architecture  
- define domain services  
- introduce infrastructure or orchestration  

### ONLY DEFINE:
- states  
- state space  
- transitions  
- lifecycle structure  
- state constraints  

---

## What is a State Model

A state model is a formal representation of:
- possible states  
- allowed transitions  
- forbidden transitions  
- lifecycle boundaries  

Conceptually:
- finite state machine (for process entities)  
- constrained state space (for entities)  

---

## Execution Methodology

---

## PART A — Process Entity State Modeling (PRIMARY)

### Step 1 — Select Process Entity
Select one process entity.

Example:
Execution  

---

### Step 2 — Define State Space
List all possible states.

Rules:
- finite  
- mutually exclusive  
- represent conditions (not actions)  

Example:
- created  
- running  
- evaluating  
- completed  
- failed  

---

### Step 3 — Normalize States
Ensure:
- no duplicated meaning  
- consistent naming  
- no technical terminology  

---

### Step 4 — Define Valid Transitions
Format:
State A → State B  

Rules:
- represent valid progression  
- avoid implicit transitions  
- avoid skipping unless required  

---

### Step 5 — Define Invalid Transitions
Explicitly list forbidden transitions.

These will later become invariants.  

---

### Step 6 — Identify Lifecycle Boundaries
Define:
- initial state  
- terminal states  

---

### Step 7 — Validate State Machine
Ensure:
- all states are reachable  
- transitions are coherent  
- lifecycle is finite  
- no ambiguity exists  

---

## PART B — Entity State Identification (SECONDARY)

### Step 8 — Identify Stateful Entities
From domain concepts:

Detect entities that:
- change over time  
- have state-dependent behavior  

---

### Step 9 — Identify State Attributes
For each entity:

Define:
- attributes that represent state  

Examples:
- status  
- phase  
- condition flags  

---

### Step 10 — Identify Implicit Transitions
Define how state changes occur.

Examples:
- draft → confirmed  
- active → inactive  

---

### Step 11 — Identify State Constraints
Define conditions that must hold in specific states.

Examples:
- completed → result must exist  
- cancelled → no further changes allowed  

---

### Step 12 — Validate Entity State Consistency
Ensure:
- no invalid state combinations  
- transitions align with domain rules  
- constraints are enforceable  

---

## Output Format (MANDATORY)

### Markdown

# State Model Extraction

## Process Entity: <Name>

### States
- ...
- ...

### Initial State
- ...

### Terminal States
- ...

### Valid Transitions
- State A → State B

### Invalid Transitions
- State X → State Y

---

## Entity State Definitions

### Entity: <Name>

#### State Attributes
- ...

#### Possible States
- ...

#### Allowed Transitions
- ...

#### State Constraints
- ...

---

## State Model Description
- describes lifecycle logic  
- explains transitions  
- clarifies constraints  

---

### JSON

{
  "process_state_models": [
    {
      "process_entity": "",
      "states": [],
      "initial_state": "",
      "terminal_states": [],
      "valid_transitions": [],
      "invalid_transitions": []
    }
  ],
  "entity_states": [
    {
      "entity": "",
      "state_attributes": [],
      "states": [],
      "transitions": [],
      "constraints": []
    }
  ]
}

---

## Completion Criteria

The skill is complete when:
- all process entities have explicit state machines  
- all relevant entities have defined state structures  
- transitions are explicitly defined or constrained  
- lifecycle boundaries are clear  
- invalid transitions are identified  
- no ambiguity exists in system evolution  
- JSON output is valid and structured  

---

## Key Insight

State is universal  
Process entities make it explicit  
Aggregates enforce it  
Invariants protect it  

This skill transforms:

System evolution → Formal, controlled state structure  

Without this:
- transitions remain implicit  
- invariants become unclear  
- domain becomes inconsistent  

State modeling is the foundation of domain correctness.
