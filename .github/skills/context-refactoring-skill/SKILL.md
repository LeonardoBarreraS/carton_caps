---
name: context-refactoring-skill
description: Detects when bounded contexts should be split, merged, or redefined and refactors architecture accordingly.
---

# Context Refactoring Skill

This skill refactors bounded contexts.

It evolves system semantics.

It detects when contexts must:

- split
- merge
- move concepts
- redefine boundaries
- extract subdomains

This skill preserves domain meaning over time.

---

# When to use this skill

Use this skill when:

- domain grows
- contexts become large
- meanings diverge
- coupling increases
- invariants become unclear
- workflows cross contexts

This is Phase 8 — Evolution.

---

# Core Principle

Bounded contexts define:

semantic ownership

When meaning changes:

contexts must evolve

Architecture must follow domain meaning.

---

# Signals Context Must Be Split

Split when:

- unrelated entities in same context
- multiple responsibilities
- different workflows
- conflicting invariants
- separate language emerging
- high internal coupling

Example:

User context contains:

authentication  
billing  
profile  

This should split.

---

# Split Example

Before:

UserContext

Entities:

User  
AuthSession  
Subscription  
Invoice  

After:

IdentityContext  
BillingContext  

---

# Signals Context Must Be Merged

Merge when:

- same domain language
- shared invariants
- constant cross-calls
- same lifecycle
- tightly coupled entities

Example:

TaskContext  
AssignmentContext  

Merge into:

WorkManagementContext

---

# Signals Concept Must Move

Move entity when:

ownership unclear

Example:

Invoice inside OrderContext

Move to:

BillingContext

---

# Step-by-Step Refactoring

## Step 1 — Analyze contexts

List:

contexts  
entities  
workflows  
invariants  

---

## Step 2 — Detect semantic conflicts

Check:

multiple meanings  
overlapping invariants  
mixed workflows  

---

## Step 3 — Define new boundaries

Split:

Context A → Context A1 + Context A2

---

## Step 4 — Move entities

Move:

entities  
services  
events  

---

## Step 5 — Redefine communication

Add:

events  
translators  
interfaces  

---

# Refactoring Template

Before:

UserContext

Entities:

User  
Invoice  
Subscription  

After:

IdentityContext  
BillingContext  

---

# Example

Before:

AgentContext

Entities:

Agent  
Execution  
Evaluation  
Task  

After:

AgentContext  
ExecutionContext  
TaskContext  

---

# Output Template

The agent should output:

## Current Contexts

UserContext  
BillingContext  

---

## Problem

UserContext contains billing logic

---

## Refactoring

Split UserContext

---

## New Contexts

IdentityContext  
BillingContext  

---

## Moved Entities

Invoice → BillingContext  
Subscription → BillingContext  

---

# Refactoring Types

Split context  
Merge contexts  
Move entity  
Extract subdomain  
Redefine ownership  

---

# Rules

Context refactoring must:

- follow domain meaning
- reduce coupling
- clarify ownership
- isolate invariants

Context refactoring must NOT:

- be technical
- be based on folders
- be based on frameworks

This is semantic refactoring.

---

# Dependency Impact

After split:

Add communication:

events  
translators  
interfaces  

---

# Architecture Update

After refactor update:

components  
layers  
communication  
wiring  

---

# Goal

Evolve semantic boundaries.

Keep domain clean.

Prevent context erosion.