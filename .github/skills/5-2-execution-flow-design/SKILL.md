---
name: 5-2-execution-flow-design
description: Defines the execution flow inside application-layer use cases, specifying the sequence, coordination, and control logic required to execute domain behavior without introducing domain rules or infrastructure details.
---

# Execution Flow Design (Refined)

This skill defines the **execution flow inside use cases**.

It transforms:

- use cases (Phase 5.1)
- domain model (Phase 4)

into:

- concrete execution logic

---

# Core Principle

Execution flow answers:

> "How is this use case executed step by step?"

It defines:

- sequence  
- coordination  
- control logic  

It does NOT define:

- domain rules  
- invariants  
- business meaning  

Those belong to the **Domain Layer**.

It does NOT implement:

- IO operations  
- database logic  
- external API calls  

Those belong to the **Infrastructure Layer**.

---

# Role in the Architecture

Execution flow lives:

- **inside a use case**
- or as an internal application service (optional)

It is NOT:

- a standalone domain concept  
- a replacement for workflows from analysis  

It is the **operational realization** of behavior.

---

# Responsibilities

Execution flow must:

- define step-by-step execution  
- coordinate aggregates  
- invoke domain methods  
- call domain services  
- control sequence and transitions  
- handle branching logic  
- interact with ports (abstractly)  
- define when side effects occur  

Execution flow must NOT:

- implement domain rules  
- enforce invariants  
- mutate state directly outside domain methods  
- depend on infrastructure implementations  

---

# Inputs

This skill requires:

- use cases (from Skill 5.1)
- domain entities and aggregates
- domain services
- process entities (if present)

---

# Outputs

This skill produces:

- execution flow definitions
- sequencing logic
- control structures (conditions, loops, branching)
- coordination between aggregates
- interaction points with ports

---

# Step-by-Step Design

## Step 1 — Identify involved domain elements

Example:

Entities:
- Document  
- ProcessingExecution  

Services:
- EvaluationPolicy  

---

## Step 2 — Identify required transitions

From domain:

- document.analyze()  
- document.validate()  
- document.approve()  

These define **what can happen**.

---

## Step 3 — Define execution sequence

Example:

1. load document  
2. start execution  
3. analyze  
4. validate  
5. approve  
6. complete  

---

## Step 4 — Define control logic

Example:

- if analysis fails → stop  
- if validation fails → reject  
- else → approve  

This defines **when transitions occur**, not their validity.

---

## Step 5 — Define coordination

Execution flow may:

- coordinate multiple aggregates  
- invoke domain services  
- update process entities  

Example:

- select agent (domain service)  
- assign task  
- update execution state  

---

## Step 6 — Define interaction with ports

Execution flow determines:

- when persistence happens  
- when external services are invoked  

Examples:

- save entity via repository  
- call LLMService  
- send notification  

These are **port interactions**, not implementations.

---

# Execution Flow Template

Use Case: ProcessDocumentUseCase  

Execution Flow:

1. receive command  
2. load document  
3. start processing execution  
4. analyze document  
5. if analysis fails → stop  
6. validate document  
7. if validation fails → reject  
8. approve document  
9. persist state  
10. notify result  
11. return response  

---

# Example — Multi-Aggregate Flow

Workflow:

Assign Task  

Execution Flow:

1. load task  
2. load agents  
3. select best agent (domain service)  
4. assign task  
5. update agent workload  
6. save task  
7. emit notification  

---

# Control Structures

Execution flow may include:

- conditional branching  
- sequential steps  
- retries (optional)  
- error handling (application-level)  

But NOT:

- domain validation logic  
- invariant enforcement  

---

# Dependency Direction

Execution flow depends on:

- domain  
- ports (interfaces)

Execution flow does NOT depend on:

- infrastructure implementations  
- controllers  
- frameworks  

---

# Relationship with Use Case

Use Case (Skill 5.1):

- defines intent  
- defines dependencies  

Execution Flow (this skill):

- defines behavior  
- defines sequence  

Relationship:

UseCase  
└── Execution Flow  

---

# Rules

Execution flow must:

- orchestrate domain behavior  
- define sequence of operations  
- coordinate aggregates  
- invoke domain services  
- interact through ports  

Execution flow must NOT:

- contain domain rules  
- enforce invariants  
- depend on infrastructure  
- redefine domain semantics  

---

# Goal

Define **how use cases execute behavior** by:

- sequencing domain interactions  
- coordinating entities and services  
- controlling execution logic  

The Application Layer becomes a **process execution engine**, where execution flows operationalize system behavior without redefining domain meaning.

