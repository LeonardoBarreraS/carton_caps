---
name: 2-4-invariant-detection
description: Derives domain invariants from state models, transitions, and constraints. Defines rules that must always hold to ensure domain correctness and consistency.
---

# Invariant Detection

## Purpose
This skill transforms **state models + constraints** into **domain invariants**.

It defines:
- valid states
- valid transitions
- forbidden transitions
- dependency rules
- value constraints

Invariants ensure that:

the domain can never enter an invalid state

---

## Core Principle

State models define possible evolution  
Constraints define limits  
Invariants enforce correctness  

Invariants = rules that must ALWAYS hold

They are non-negotiable truths of the domain.

---

## When to Use

Use this skill when:
- state models are defined
- constraints are identified
- process entities are known
- before aggregate design
- before domain modeling

---

## Strict Rules

### DO NOT:
- define entities
- define architecture
- define services or orchestration
- define implementation logic
- define UI or infrastructure validation

### ONLY DEFINE:
- rules
- constraints
- allowed transitions
- forbidden transitions
- domain correctness conditions

---

## Types of Invariants

### 1. State Invariants
Define what makes a state valid.

Examples:
- status must always be defined
- completed state requires result
- failed state must include failure reason

---

### 2. Transition Invariants
Define allowed and forbidden transitions.

Examples:

Allowed:
- created → running
- running → completed

Forbidden:
- completed → running
- failed → running

---

### 3. Dependency Invariants
Define ordering constraints between processes.

Examples:
- evaluation requires execution completed
- response requires analysis
- deployment requires validation

---

### 4. Consistency Invariants
Define logical correctness conditions.

Examples:
- score must be between 0 and 1
- result must exist if completed
- confidence cannot be negative

---

### 5. Cross-Entity Invariants (Conceptual)
Define rules across multiple entities (without implementing them).

Examples:
- task must be assigned before execution
- evaluation must reference a valid execution

---

## Execution Methodology

Follow this reasoning pipeline:

---

### Step 1 — Analyze State Model

From state model:

Ask:
- what states are valid?
- what must always be true in each state?

---

### Step 2 — Derive Transition Rules

From transitions:

Convert:
- valid transitions → allowed invariants
- invalid transitions → forbidden invariants

Example:

Invalid:
completed → running  

Invariant:
System must not transition from completed to running

---

### Step 3 — Derive Dependency Rules

From workflows and constraints:

Ask:
- what must happen before something else?

Example:
evaluation requires execution completed  

Invariant:
Evaluation cannot start before execution completes

---

### Step 4 — Derive Value Constraints

From value objects:

Ask:
- what values are valid?
- what ranges are allowed?

Example:
0 ≤ score ≤ 1

---

### Step 5 — Derive State Conditions

For each state:

Ask:
- what must be true in this state?

Example:
If state = completed → result must exist

---

### Step 6 — Normalize Invariants

Convert all invariants into:

atomic, explicit, testable rules

Format:
- must
- must not
- requires
- cannot

---

## Output Format (MANDATORY)

### Markdown

# Invariant Detection

## Process Entity: <Name>

### State Invariants
- ...
- ...

### Transition Invariants

#### Allowed
- State A → State B
- ...

#### Forbidden
- State X → State Y
- ...

### Dependency Invariants
- ...
- ...

### Consistency Invariants
- ...
- ...

---

## Cross-Entity Invariants (Optional)
- ...
- ...

---

### JSON

{
  "invariants": [
    {
      "process_entity": "",
      "state_invariants": [],
      "transition_invariants": {
        "allowed": [],
        "forbidden": []
      },
      "dependency_invariants": [],
      "consistency_invariants": [],
      "cross_entity_invariants": []
    }
  ]
}

---

## Completion Criteria

The skill is complete when:
- invariants are derived from state models
- valid and invalid transitions are defined
- dependencies are explicit
- value constraints are defined
- invariants are atomic and testable
- no implementation details are introduced
- JSON output is valid and structured

---

## Key Insight

This skill transforms:

State model → Domain correctness rules

It ensures:
- the system cannot enter invalid states
- transitions are controlled
- domain behavior is consistent

Without invariants:
- domain logic is unreliable
- systems become inconsistent
- errors propagate silently

Invariants are the foundation of domain integrity.

