---
name: 5-3-context-coordination
description: Coordinates execution across multiple bounded contexts by orchestrating use cases through coordinators or direct interactions, without enforcing event-driven architecture or violating context boundaries.
---

# Context Coordination 

This skill defines how the system coordinates **execution across multiple bounded contexts**.

It operates at the **highest level of the Application Layer**.

---

# Core Principle

Each bounded context is **semantically autonomous**.

But system behavior may require:

> executing a process that spans multiple contexts

This skill answers:

> "How do we coordinate multiple use cases across contexts?"

---

# Role in the Architecture

Context coordination:

- operates **above individual use cases**
- orchestrates **cross-context execution**
- connects **independent application layers**

It does NOT:

- define domain rules  
- redefine workflows  
- merge contexts  

It preserves **context boundaries** while enabling **system behavior**.

---

# Responsibilities

Context coordination must:

- orchestrate use cases across contexts  
- define execution sequence across contexts  
- manage cross-context flow  
- handle coordination state (optional)  
- determine interaction strategy  
- ensure correct ordering of actions  

Context coordination must NOT:

- implement domain logic  
- enforce invariants  
- mutate entities directly  
- depend on infrastructure implementations  

---

# Inputs

This skill requires:

- use cases from multiple bounded contexts  
- execution flows (from Skill 5.2)  
- system-level workflows (Phase 1)  

---

# Outputs

This skill produces:

- coordinators (application-level)
- cross-context execution flows
- coordination strategies
- optional coordination state models

---

# Communication Strategies

This skill supports multiple patterns.

## 1. Direct Use Case Invocation (Default)

One context invokes another context’s use case.

Example:

EvaluationContext  
→ AssignAgentUseCase (AgentContext)

Use when:

- synchronous execution is acceptable  
- coupling is manageable  

---

## 2. Coordinator (Recommended for complex flows)

A coordinator orchestrates multiple contexts.

Example:

ProcessRequestCoordinator

Flow:

1. EvaluateRequestUseCase  
2. AssignAgentUseCase  
3. ExecuteTaskUseCase  

Coordinator lives in the **application layer**.

---

## 3. Translator-based Interaction

Used when:

- contexts have different models  

A translator converts:

EvaluationResult → AssignmentInput  

Preserves semantic boundaries.

---

## 4. Event-Driven (Optional)

Used when:

- asynchronous execution required  
- decoupling needed  
- distributed systems  

Example:

TaskAssigned → NotificationHandler  

This is **optional**, not default.

---

# Step-by-Step Coordination

## Step 1 — Identify cross-context process

Example:

Evaluate → Assign → Execute  

---

## Step 2 — Identify involved contexts

- EvaluationContext  
- AgentContext  
- ExecutionContext  

---

## Step 3 — Choose coordination strategy

Options:

- direct call  
- coordinator  
- translator  
- event-driven  

Default: simplest valid option

---

## Step 4 — Define coordination flow

Example:

1. EvaluateRequestUseCase  
2. AssignAgentUseCase  
3. ExecuteTaskUseCase  

---

## Step 5 — Define coordinator (if needed)

Coordinator:

ProcessRequestCoordinator  

Responsibilities:

- call use cases  
- manage sequence  
- handle transitions  
- manage state (optional)  

---

# Coordinator Template

Coordinator: ProcessRequestCoordinator  

Contexts:

- Evaluation  
- Agent  
- Execution  

Flow:

1. EvaluateRequestUseCase  
2. AssignAgentUseCase  
3. ExecuteTaskUseCase  

---

# Example — Sequential Coordination

Flow:

EvaluationContext  
↓  
AgentContext  
↓  
ExecutionContext  

Execution:

- evaluate  
- assign  
- execute  

---

# Example — Coordinator-Based

Coordinator:

OrderFulfillmentCoordinator  

Flow:

1. CreateOrderUseCase  
2. ProcessPaymentUseCase  
3. ShipOrderUseCase  

---

# Coordination State (Optional)

Coordinator may track:

- Started  
- StepCompleted  
- Completed  

Used for:

- long-running processes  
- retries  
- failure handling  

---

# Dependency Direction

Coordinator depends on:

- use cases (from contexts)  
- ports (interfaces)  

Coordinator does NOT depend on:

- domain entities  
- infrastructure  
- controllers  

---

# Relationship with Other Skills

Use Case (5.1):

- defines entry points  

Execution Flow (5.2):

- defines behavior inside context  

Context Coordination (5.3):

- connects multiple contexts  

---

# Rules

Context coordination must:

- preserve context autonomy  
- orchestrate use cases  
- choose simplest communication strategy  
- avoid unnecessary complexity  

Context coordination must NOT:

- force event-driven design  
- merge contexts  
- introduce domain logic  
- bypass use cases  

---

# Goal

Enable **system-level behavior across bounded contexts** by:

- orchestrating use cases  
- coordinating execution flows  
- preserving semantic boundaries  

The system behaves as a **coherent whole**, while each context remains **independent and well-defined**.

