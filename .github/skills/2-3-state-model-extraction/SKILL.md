---
name: 2-3-state-model-extraction
description: Defines the explicit state model of process entities, including state space and transition structure. Establishes the formal lifecycle representation required for invariant detection and aggregate design.
---

# State Model Extraction

## Purpose
This skill transforms **process entities** into **explicit state models**.

It defines:
- the complete state space
- valid transitions between states
- invalid transitions
- lifecycle structure (initial → terminal)

This is a **critical semantic step** that makes system evolution **explicit and unambiguous**.

---

## Core Principle

Process entities define that something evolves  
State models define how it evolves  

A correct domain requires:
- explicit state space
- controlled transitions
- finite lifecycle

---

## When to Use

Use this skill when:
- process entities are identified
- workflows are defined
- before invariant detection
- before aggregate design

---

## Strict Rules

### DO NOT:
- define methods or implementation
- define domain services
- define architecture
- define infrastructure
- define orchestration logic

### ONLY DEFINE:
- states
- state space
- transitions
- lifecycle structure

---

## What is a State Model

A state model is a **formal representation of lifecycle**:

It defines:
- all possible states
- all allowed transitions
- all forbidden transitions
- lifecycle boundaries

This is equivalent to a **finite state machine (conceptually)**.

---

## Execution Methodology

Follow this reasoning pipeline:

---

### Step 1 — Select Process Entity

Select one process entity at a time.

Example:
Execution

---

### Step 2 — Define State Space

List all possible states.

#### Rules:
- states must be finite
- states must be mutually exclusive
- states must represent conditions (not actions)

#### Example:
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

#### Bad:
- processing_data
- api_called

#### Good:
- processing
- executing

---

### Step 4 — Define Valid Transitions

Define allowed transitions.

#### Format:
State A → State B

#### Example:
created → running  
running → evaluating  
evaluating → completed  
running → failed  

#### Rules:
- transitions must represent valid progression
- avoid implicit transitions
- avoid skipping unless explicitly required

---

### Step 5 — Define Invalid Transitions

Explicitly define forbidden transitions.

#### Example:
completed → running  
failed → evaluating  
created → completed  

These will later become invariants.

---

### Step 6 — Identify Initial and Terminal States

#### Initial State:
- where lifecycle starts

#### Terminal States:
- where lifecycle ends (no further transitions)

#### Example:
Initial: created  
Terminal: completed, failed  

---

### Step 7 — Validate State Model

Ensure:
- all states are reachable
- transitions are coherent
- no contradictory transitions exist
- lifecycle has clear start and end
- no ambiguous or redundant states

---

## Output Format (MANDATORY)

### Markdown

# State Model Extraction

## Process Entity: <Name>

### States
- ...
- ...
- ...

### Initial State
- ...

### Terminal States
- ...
- ...

### Valid Transitions
- State A → State B
- State B → State C

### Invalid Transitions
- State X → State Y
- ...

---

## State Model Description
- describes lifecycle
- explains progression logic
- clarifies meaning of transitions

---

### JSON

{
  "state_models": [
    {
      "process_entity": "",
      "states": [],
      "initial_state": "",
      "terminal_states": [],
      "valid_transitions": [
        ["stateA", "stateB"]
      ],
      "invalid_transitions": [
        ["stateX", "stateY"]
      ],
      "description": ""
    }
  ]
}

---

## Completion Criteria

The skill is complete when:
- all states are explicitly defined
- initial state is defined
- terminal states are defined
- valid transitions are defined
- invalid transitions are explicitly listed
- lifecycle is coherent and finite
- no implementation details are introduced
- JSON output is valid and structured

---

## Key Insight

This skill transforms:

Process entity → Formal state machine

It eliminates ambiguity by making:
- state explicit
- transitions controlled
- lifecycle finite

This is essential for:
- invariant detection
- aggregate design
- domain correctness

Without a state model, domain logic becomes inconsistent and unreliable.

