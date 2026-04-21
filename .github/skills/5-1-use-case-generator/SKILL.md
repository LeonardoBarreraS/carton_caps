---
name: 5-1-use-case-generator
description: Generates application-layer use cases as execution entry points that orchestrate domain behavior through defined ports, without containing domain logic or infrastructure details.
---

# Use Case Generator (Refined)

This skill generates **Application Layer use cases**.

It transforms:

- conceptual workflows (Phase 1)
- domain model (Phase 4)

into:

- executable application entry points

---

# Core Principle

A use case answers:

> "Execute this process"

It does NOT define:

- business rules  
- invariants  
- domain meaning  

Those belong to the **Domain Layer**.

It does NOT implement:

- database access  
- API calls  
- messaging  

Those belong to the **Infrastructure Layer**.

---

# Role of the Use Case

The use case is:

- an **entry point** into the system  
- a **process executor**  
- a **coordinator of domain behavior**  
- a **transaction boundary**  

It is the **bridge between intent and execution**.

---

# Key Responsibilities

A use case must:

- receive a request (command)
- load required domain objects
- invoke domain behavior
- coordinate domain services
- orchestrate execution flow
- interact with external systems via **ports**
- persist state via **repository interfaces**
- return a response

A use case must NOT:

- implement domain rules
- validate invariants
- mutate state arbitrarily
- depend on infrastructure implementations
- contain framework or protocol logic

---

# Inputs

This skill requires:

- domain entities and aggregates
- domain services
- process entities (if any)
- conceptual workflows (from Phase 1)

---

# Outputs

This skill produces:

- Use Case classes (Application Services)
- Commands (input DTOs)
- Response DTOs (optional)
- Port definitions (interfaces)
- Dependency definitions

---

# Step-by-Step Generation

## Step 1 — Identify system action

From workflows, extract:

one **actionable intent**

Example:

Process Document  
Assign Task  
Evaluate Request  

---

## Step 2 — Define use case name

Rule:

Verb + Domain Concept + UseCase

Examples:

ProcessDocumentUseCase  
AssignTaskUseCase  
EvaluateRequestUseCase  

---

## Step 3 — Define command (input)

Command represents:

user or system intent

Example:

ProcessDocumentCommand  
- document_id  
- user_id  

Commands are:

- immutable  
- simple data carriers  
- free of behavior  

---

## Step 4 — Define dependencies (PORTS)

Use case defines what it needs from outside.

These are **interfaces**, not implementations.

Examples:

- DocumentRepository  
- NotificationService  
- LLMService  
- EventPublisher  

These are **ports**.

---

## Step 5 — Define execution responsibility

The use case defines:

- which domain objects are involved  
- which transitions are triggered  
- which services are invoked  

It does NOT define rules — only execution.

---

## Step 6 — Define execution flow (high-level)

Example:

1. receive command  
2. load aggregate  
3. invoke domain behavior  
4. call domain services  
5. persist changes  
6. trigger external interactions via ports  
7. return response  

This is **execution flow**, not domain logic.

---

# Use Case Template

UseCase: ProcessDocumentUseCase  

Input:  
ProcessDocumentCommand  
- document_id  

Dependencies (Ports):  
- DocumentRepository  
- LLMService  
- NotificationService  

Execution Flow:

1. load document  
2. analyze document (via LLMService)  
3. invoke domain validation  
4. update document state  
5. save document  
6. notify result  
7. return response  

---

# Dependency Direction

Use case depends on:

- Domain Layer  
- Ports (interfaces)

Use case does NOT depend on:

- Infrastructure implementations  
- Controllers / APIs  
- Frameworks  
- Databases  

---

# Interaction Flow

Shell  
↓  
Use Case  
↓  
Domain  
↓  
Ports (interfaces)  
↓  
Infrastructure (implementation)  

Return:

Domain result  
↓  
Use Case  
↓  
Response DTO  
↓  
Shell  

---

# Rules

Use cases must:

- orchestrate domain behavior  
- define execution entry points  
- use ports for all external interaction  
- remain framework-independent  

Use cases must NOT:

- contain domain rules  
- enforce invariants  
- depend on infrastructure  
- implement IO logic  

---

# Goal

Create **pure application-layer entry points** that:

- execute domain behavior  
- define system actions  
- declare external needs via ports  
- remain independent from technical implementation  

The Application Layer becomes a **process execution engine**, not a source of domain meaning.

