---
name: 1-4-constraint-identification
description: Identifies high-level system constraints that define limits, assumptions, and invalid behaviors before domain modeling. Establishes admissible behavior boundaries.
---

# Constraint Identification

## Purpose
This skill identifies **system-level constraints** that define:

- what the system must NOT do
- what conditions must hold
- what limits the system behavior

It complements behavior and workflows by defining:

**admissible vs non-admissible behavior**

This is the fourth step of Semantic Design.

---

## Core Principle

Behavior defines what CAN happen  
Constraints define what MUST NOT happen  

Constraints precede invariants.

They operate at a **system level**, not at a domain-object level.

---

## When to Use

Use this skill when:
- Goal & Scope Definition is completed
- Behavior Definition is completed
- Workflow Modeling is completed
- before domain modeling
- before invariant detection

---

## Strict Rules

### DO NOT:
- define domain invariants (entity-level rules)
- define detailed state transitions
- define entities or domain objects
- define architecture or implementation
- define validation logic or code

### ONLY DEFINE:
- system constraints
- invalid behaviors
- assumptions
- operational limits

---

## Types of Constraints

### 1. Behavioral Constraints
Define what the system must NOT do.

Examples:
- The system must not process invalid input
- The system must not produce undefined output
- The system must not skip required steps

---

### 2. Input Constraints
Define conditions inputs must satisfy.

Examples:
- Input must be non-empty
- Input must follow expected format
- Required parameters must be present

---

### 3. Output Constraints
Define expectations on outputs.

Examples:
- Output must be structured
- Output must be complete
- Output must match request intent

---

### 4. Dependency Constraints
Define ordering or prerequisite conditions.

Examples:
- Evaluation requires prior processing
- Response requires analysis
- Execution requires valid input

---

### 5. Operational Constraints (Optional)
Define system-level limits.

Examples:
- The system must respond within a time limit
- The system must handle limited input size
- The system must avoid redundant processing

---

## Execution Methodology

Follow this reasoning pipeline:

---

### Step 1 — Analyze Behaviors

From defined behaviors:

Ask:
What could go wrong?

Identify:
- invalid actions
- incomplete behaviors
- incorrect usage

---

### Step 2 — Analyze Workflows

From workflows:

Ask:
What transitions must NOT happen?

Examples:
- skipping steps
- reversing flow
- executing out of order

---

### Step 3 — Identify Preconditions

Ask:
What must be true BEFORE execution?

Examples:
- valid input required
- required data must exist

---

### Step 4 — Identify Postconditions

Ask:
What must be true AFTER execution?

Examples:
- output must exist
- result must be consistent

---

### Step 5 — Identify Assumptions

Define system assumptions about:
- environment
- inputs
- external dependencies

Examples:
- external service is available
- input source is reliable

---

### Step 6 — Normalize Constraints

Convert all findings into:

clear, atomic, testable statements

Format:
- The system must not ...
- The system must ...
- The system requires ...

---

## Output Format (MANDATORY)

### Markdown

# Constraint Identification

## Behavioral Constraints
- The system must not ...
- The system must not ...

## Input Constraints
- The system requires ...
- Input must ...

## Output Constraints
- The system must produce ...
- Output must ...

## Dependency Constraints
- The system requires ...
- Process A must precede Process B

## Operational Constraints (Optional)
- The system must ...

## Assumptions
- The system assumes ...
- The system depends on ...

---

### JSON

{
  "constraints": {
    "behavioral": [],
    "input": [],
    "output": [],
    "dependency": [],
    "operational": []
  },
  "assumptions": []
}

---

## Completion Criteria

The skill is complete when:
- invalid behaviors are identified
- input/output conditions are defined
- dependencies are clarified
- assumptions are explicit
- constraints are atomic and testable
- no domain-level invariants are introduced
- JSON output is valid and structured

---

## Key Insight

This skill transforms:

Behavioral space → Constrained behavioral space

It defines the limits of the system before domain modeling.

This ensures:
- fewer contradictions in later phases
- stronger invariant detection
- clearer domain boundaries

Constraints are the first layer of system correctness.

