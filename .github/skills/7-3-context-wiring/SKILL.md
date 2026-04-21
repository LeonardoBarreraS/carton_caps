---
name: 7-3-context-wiring
description: Connects use cases and coordinators across bounded contexts by defining invocation paths and interaction links, without introducing business logic, workflows, or orchestration behavior.
---

# Context Wiring (Phase 7.3)

This skill connects **bounded contexts** at the system level.

It transforms:

- independent application modules (contexts)

into:

- a connected system

---

# Core Principle

Context wiring answers:

> "How are use cases across bounded contexts connected?"

It does NOT define:

- workflows  
- execution logic  
- business rules  

It only defines:

> how components are linked

---

# Role in the Architecture

Context wiring:

- belongs to the **Shell Layer**  
- operates above individual contexts  
- connects application layers across contexts  

It ensures:

> system-level connectivity without breaking context boundaries

---

# Responsibilities

Context wiring must:

- connect use cases across contexts  
- wire coordinators to use cases  
- define invocation paths between contexts  
- connect translators (if needed)  

Context wiring must NOT:

- define workflows  
- orchestrate behavior  
- implement domain logic  
- mutate entities  

---

# Inputs

This skill requires:

- use cases (Phase 5.1)  
- coordinators (Phase 5.3)  
- bounded contexts (Phase 3)  

---

# Outputs

This skill produces:

- context-to-context connections  
- coordinator wiring definitions  
- invocation paths  

---

# Communication Patterns

This skill supports multiple interaction patterns.

## Direct Invocation (Default)

One use case calls another across contexts.

Example:

EvaluationContext  
→ AssignAgentUseCase (AgentContext)  

---

## Coordinator-Based Connection

Coordinator links multiple use cases.

Example:

ProcessRequestCoordinator  

Connected to:

- EvaluateRequestUseCase  
- AssignAgentUseCase  
- ExecuteTaskUseCase  

---

## Translator-Based Connection

Used when contexts differ semantically.

Example:

EvaluationResult  
→ Translator  
→ AssignmentInput  

---

## Event-Based Connection

Used when messaging is present.

Example:

TaskAssigned → NotificationHandler  

This depends on messaging adapters (Phase 6.3).

---

# Step-by-Step Wiring

## Step 1 — Identify contexts

Example:

- EvaluationContext  
- AgentContext  
- ExecutionContext  

---

## Step 2 — Identify cross-context interactions

From existing use cases and coordinators.

Example:

EvaluateRequestUseCase  
→ AssignAgentUseCase  

---

## Step 3 — Choose interaction pattern

Options:

- direct invocation  
- coordinator  
- translator  
- event-based  

Choose simplest valid option.

---

## Step 4 — Define connections

Examples:

evaluate_use_case → assign_agent_use_case  

or:

coordinator → use cases  

---

# Example

Contexts:

- Evaluation  
- Agent  
- Execution  

Coordinator:

ProcessRequestCoordinator  

Connections:

- coordinator → EvaluateRequestUseCase  
- coordinator → AssignAgentUseCase  
- coordinator → ExecuteTaskUseCase  

---

# Folder Structure

/shell  
    /wiring  
        context_wiring.py  

---

# Dependency Direction

Shell wiring depends on:

- use cases  
- coordinators  
- translators  
- messaging adapters (if present)  

Contexts remain:

- independent  
- isolated  

---

# Rules

Context wiring must:

- preserve context boundaries  
- connect use cases, not entities  
- remain simple and explicit  
- choose minimal coupling  

Context wiring must NOT:

- define workflows  
- orchestrate execution  
- introduce domain logic  
- enforce coordination logic  

---

# Goal

Connect **independent bounded contexts** by:

- linking use cases  
- wiring coordinators  
- defining interaction paths  

Context wiring enables the system to behave as a **coherent whole**, while preserving the autonomy and integrity of each bounded context.

