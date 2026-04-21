---
name: 1-2-behavior-definition
description: Converts system framing into structured system behaviors, capabilities, and use cases. Defines WHAT the system must do without specifying workflow, domain, or implementation.
---

# Behavior Definition

## Purpose
This skill transforms system framing into a **structured behavioral specification**.

It defines:
- what the system must do
- what capabilities it exposes
- how actors interact with it

This is the second step of Semantic Design.

---

## Core Principle

Goal defines WHY  
Behavior defines WHAT  
Workflow defines HOW (later)

This skill defines **WHAT the system does**, not:
- how it executes
- how it is structured
- what internal concepts exist

---

## When to Use

Use this skill when:
- Goal & Scope Definition is completed
- system objective is clear
- inputs/outputs are defined
- before workflow modeling
- before domain modeling

---

## Strict Rules

### DO NOT:
- define workflows or sequences
- define entities or domain concepts
- define architecture
- define classes, APIs, or infrastructure
- define state transitions

### ONLY DEFINE:
- system behaviors
- capabilities
- use cases
- actor interactions

---

## Execution Methodology

Follow this reasoning pipeline strictly:

---

### Step 1 — Extract Core Capabilities

From:
- system objective
- inputs/outputs

Ask:
What must the system be able to do?

Each capability must:
- represent a meaningful action
- produce an observable outcome

Examples:
- analyze input
- generate response
- evaluate result
- store data
- retrieve information

---

### Step 2 — Map Actor Interactions

From defined actors:

Ask:
What can each actor request or trigger?

Define interactions as:

Actor → system action

Examples:
- User submits input
- User requests result
- External system provides data
- System calls AI model

---

### Step 3 — Define Use Cases

Transform capabilities into externally observable behaviors.

#### Format:
The system must ...

#### Rules:
- must be observable
- must be meaningful externally
- must not include implementation details

#### Good:
- The system must analyze input data
- The system must generate a response

#### Bad:
- The system must create Analyzer class
- The system must call API X

---

### Step 4 — Ensure Behavioral Completeness

Check for missing behaviors:

#### Lifecycle:
- create / start
- process / update
- complete / finalize

#### Error Handling:
- invalid input
- failed processing
- retry

#### Support:
- retrieve results
- inspect state
- re-run process

Add missing behaviors if needed.

---

### Step 5 — Structure Behaviors

Group behaviors into:

#### Core Behaviors
Primary system value

#### Actor Interactions
External triggers

#### Support Behaviors
Auxiliary functionality

#### Optional Behaviors
Non-essential features

---

### Step 6 — Define Behavioral Dependencies

Define relationships between behaviors:

Format:
Behavior A requires Behavior B

Purpose:
- ensure logical consistency
- prepare workflow modeling
- detect missing prerequisites

---

## Output Format (MANDATORY)

### Markdown

# Behavior Definition

## Capabilities
- ...
- ...

## Use Cases

### Core Behaviors
- The system must ...
- The system must ...

### Actor Interactions
- The user can ...
- The system can ...
- External system can ...

### Support Behaviors
- The system must ...

### Optional Behaviors
- The system may ...

## Behavioral Dependencies
- Behavior A requires Behavior B
- ...

---

### JSON

{
  "capabilities": [],
  "use_cases": {
    "core": [],
    "actor_interactions": [],
    "support": [],
    "optional": []
  },
  "dependencies": []
}

---

## Completion Criteria

The skill is complete when:
- all core behaviors are identified
- use cases are clearly defined
- actor interactions are mapped
- missing behaviors are detected and added
- dependencies are defined
- no workflow or sequencing is introduced
- JSON output is valid and structured

---

## Key Insight

This skill transforms:

System framing → Behavioral space

It defines everything the system can do, without defining:
- order
- structure
- implementation

This ensures:
- completeness before workflow modeling
- clarity before domain modeling
- reduced ambiguity for downstream skills

