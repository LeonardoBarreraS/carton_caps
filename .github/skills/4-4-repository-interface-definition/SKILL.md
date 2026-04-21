---
name: 4-4-repository-interface-definition
description: Defines repository interfaces (ports) in the domain layer that express persistence and retrieval requirements for aggregates, without introducing infrastructure or implementation details.
---

# 4.4 — Repository Interface Definition

## Purpose
Transform **aggregate persistence and retrieval needs** into **repository interfaces (ports)** within the domain layer.

It defines:
- how aggregates are retrieved  
- how aggregates are persisted  
- the minimal contract required by the domain  

This ensures that the domain can operate and enforce invariants **without depending on infrastructure**.

---

## Core Principle

Domain defines WHAT it needs  
Infrastructure defines HOW it is fulfilled  

Repositories are:
- abstractions  
- contracts  
- capability requirements  

NOT implementations.

---

## Critical Rule

NO INFRASTRUCTURE IS INTRODUCED IN THIS PHASE

This phase:
- defines interfaces only  
- does NOT define databases, queries, or external systems  

If implementation details appear:
→ you are in Phase 6, not Phase 4  

---

## When to Use

Use this skill when:
- aggregates are implemented (Phase 4.2)
- domain services are defined (Phase 4.3)
- the domain requires persistence or retrieval of aggregates

---

## Strict Rules

### DO NOT:
- implement repositories  
- reference databases, APIs, or frameworks  
- define queries or persistence logic  
- expose infrastructure concerns  

### ONLY DEFINE:
- repository interfaces  
- methods required by the domain  
- aggregate retrieval and persistence contracts  

---

## What is a Repository (Domain Perspective)

A repository is:
- a domain abstraction  
- a collection-like interface for aggregate roots  
- a mechanism to retrieve and persist aggregates  

It represents:

A domain-level collection of aggregates  

---

## Repository Scope

Repositories are defined:
- per aggregate root  
- NOT per entity  
- NOT per value object  

---

## Execution Methodology

---

### Step 1 — Identify Aggregate Needs

From aggregates:

Ask:
- does this aggregate need to be persisted?  
- does it need to be retrieved later?  

If YES:
→ define a repository  

---

### Step 2 — Define Repository per Aggregate Root

For each aggregate:

Define:

<AggregateName>Repository  

Example:
ExecutionRepository  
OrderRepository  

---

### Step 3 — Define Core Methods

Define only the minimal required operations:

Mandatory:
- save(aggregate)  
- getById(id)  

Optional (only if required by domain):
- findBy<Criteria>()  

Rules:
- methods must reflect domain needs  
- avoid unnecessary CRUD operations  

---

### Step 4 — Define Method Signatures

Inputs:
- aggregate root  
- identifiers  
- value objects  

Outputs:
- aggregate root  

Rules:
- no DTOs  
- no infrastructure types  

---

### Step 5 — Maintain Abstraction Purity

Ensure:
- no reference to storage mechanisms  
- no mention of SQL, NoSQL, APIs, etc.  

---

### Step 6 — Validate Minimality

Ensure:
- only required methods exist  
- no unnecessary exposure of operations  

---

## Output Format (MANDATORY)

### Markdown

# Repository Interface Definition

## Repository: <AggregateName>Repository

### Purpose
- ...

---

### Methods

#### save
- input: <Aggregate>
- output: void

#### getById
- input: <ID>
- output: <Aggregate>

---

### Optional Methods
- ...

---

### Constraints
- no infrastructure details  
- no implementation  
- aggregate root only  

---

### JSON

{
  "repositories": [
    {
      "name": "",
      "aggregate": "",
      "methods": [
        {
          "name": "",
          "inputs": [],
          "output": ""
        }
      ]
    }
  ]
}

---

## Completion Criteria

The skill is complete when:
- one repository per aggregate root is defined  
- methods reflect domain needs  
- only aggregate roots are handled  
- no infrastructure details are present  
- interfaces are minimal and precise  
- JSON output is valid and structured  

---

## Key Insight

Persistence need → Domain contract  

Repositories are:
- NOT about databases  
- NOT about implementation  

They are about:
- enabling the domain to function  
- preserving invariants across operations  
- maintaining independence from infrastructure  

Without repository interfaces:
- domain depends on infrastructure  
- invariants become fragile  
- system becomes tightly coupled  

Repositories allow the domain to remain pure while still being operable.

