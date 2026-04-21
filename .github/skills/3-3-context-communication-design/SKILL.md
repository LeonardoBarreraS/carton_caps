---
name: 3-3-context-communication-design
description: Defines how bounded contexts (components) communicate using events, interfaces, and orchestration while preserving semantic isolation and preventing domain leakage.
---

# Context Communication Design

## Purpose
This skill defines **how components (bounded contexts) interact** without violating semantic boundaries.

It defines:
- communication mechanisms
- interaction patterns
- dependency direction
- translation between contexts

This ensures:

No context leaks its internal domain model into another.

---

## Core Principle

Contexts must NOT share:
- entities  
- value objects  
- aggregates  
- invariants  

Instead, they communicate via:

- events  
- interfaces  
- orchestration  

Communication is **semantic**, not structural.

---

## Critical Rule

NO DOMAIN SHARING BETWEEN CONTEXTS

If two contexts share:
- entities  
- invariants  
→ bounded context design is incorrect (return to Phase 2)

---

## When to Use

Use this skill when:
- bounded contexts are defined
- components are defined
- layered architecture exists
- cross-context workflows exist

This is the final step of Structural Design.

---

## Strict Rules

### DO NOT:
- share domain objects across contexts
- define cross-context invariants
- tightly couple components
- expose internal models

### ONLY DEFINE:
- communication mechanisms
- interaction direction
- translation strategies
- orchestration boundaries

---

## Communication Types

---

### 1. Event-Driven Communication (Preferred)

A context emits an event representing something that already happened.

Example:
OrderContext → OrderCreated  
PaymentContext reacts  

Characteristics:
- asynchronous  
- loosely coupled  
- scalable  
- no direct dependency  

Use when:
- reaction is optional  
- no immediate response needed  

---

### 2. Direct Interface Communication

One context calls another via an interface.

Example:
OrderContext → PaymentPort.authorize()  

Rules:
- interface is defined in caller context  
- implementation is in callee context  
- no domain objects are shared  

Characteristics:
- synchronous  
- stronger coupling  
- immediate response  

Use when:
- response is required  
- validation is immediate  

---

### 3. Application-Level Orchestration

Application layer coordinates multiple contexts.

Example:
CreateOrderUseCase:
- create order  
- request payment  
- notify user  

Characteristics:
- central coordination  
- no direct domain coupling  
- workflow-level control  

Use when:
- multiple contexts involved  
- sequence matters  

---

## Execution Methodology

Follow this reasoning pipeline:

---

### Step 1 — Identify Cross-Context Interactions

From workflows:

Ask:
Which workflows span multiple contexts?

Example:
Execution → Evaluation  
Evaluation → Deployment  

---

### Step 2 — Define Communication Direction

For each interaction:

Define:

Context A → Context B  

Rules:
- avoid bidirectional dependencies  
- maintain clear direction  

---

### Step 3 — Select Communication Type

Use:

Event-driven if:
- asynchronous  
- decoupled  
- optional reaction  

Direct interface if:
- synchronous  
- required response  
- immediate validation  

Orchestration if:
- multi-context coordination  
- ordered execution  

---

### Step 4 — Define Events

Events must:
- represent something that already happened  
- be immutable  
- be minimal  
- use domain language  

Format:

Event: <Name>  
Fields:
- ...  
Publisher: Context A  
Consumers: Context B  

Example:
ExecutionCompleted  
- execution_id  
- result  

---

### Step 5 — Define Interfaces (Ports)

For synchronous communication:

Define:

Interface (in caller context):
- method name  
- purpose  

Implementation:
- resides in callee context infrastructure  

Rules:
- no domain objects exchanged  
- only DTOs or primitives  

---

### Step 6 — Define Translators

When contexts have different models:

Define translation:

Context A model → Context B model  

Location:
- application layer  
- anti-corruption layer  

Purpose:
- prevent semantic leakage  

---

### Step 7 — Define Communication Map

Define all interactions:

Context A:
- publishes → Event X  
- calls → Interface Y  

Context B:
- consumes → Event X  
- implements → Interface Y  

---

### Step 8 — Validate Isolation

Ensure:
- no shared domain objects  
- no cross-context invariants  
- communication uses translation  
- dependencies are unidirectional  

If violated:
→ context boundaries are incorrect  

---

## Output Format (MANDATORY)

### Markdown

# Context Communication Design

## Communication Map

- Context A → Context B (event)
- Context B → Context C (interface)
- Context A → Context C (orchestration)

---

## Events

### Event: <Name>
- fields:
  - ...
- publisher: ...
- consumers:
  - ...

---

## Interfaces

### Interface: <Name>
- defined in: ...
- implemented in: ...
- methods:
  - ...

---

## Translators

- Source → Target
- Purpose: ...

---

## Communication Rules

- no shared domain models  
- no cross-context invariants  
- all communication explicit  

---

### JSON

{
  "communications": [
    {
      "from": "",
      "to": "",
      "type": "event | interface | orchestration"
    }
  ],
  "events": [
    {
      "name": "",
      "fields": [],
      "publisher": "",
      "consumers": []
    }
  ],
  "interfaces": [
    {
      "name": "",
      "defined_in": "",
      "implemented_in": "",
      "methods": []
    }
  ],
  "translators": [
    {
      "from": "",
      "to": "",
      "purpose": ""
    }
  ]
}

---

## Completion Criteria

The skill is complete when:
- all cross-context interactions are defined  
- communication types are correctly selected  
- events are defined and meaningful  
- interfaces are correctly placed  
- translators prevent semantic leakage  
- no domain objects are shared  
- dependencies are unidirectional  
- JSON output is valid and structured  

---

## Key Insight

This skill transforms:

Structural boundaries → Safe interaction model  

It ensures:
- contexts remain independent  
- communication is explicit  
- domain meaning is preserved  

If communication is incorrect:
- contexts become coupled  
- domain models leak  
- invariants break across boundaries  

This is where distributed systems either:
- remain coherent  
- or collapse into chaos

