---
name: architecture-consistency-checker
description: Validates architecture boundaries, dependency direction, and layer responsibilities across the entire system.
---

# Architecture Consistency Checker

This skill validates architecture integrity.

It checks:

- layer boundaries
- dependency direction
- context isolation
- domain purity
- clean architecture rules
- DDD boundaries

This skill protects system structure.

---

# When to use this skill

Use this skill when:

- architecture evolves
- refactoring occurs
- new features added
- contexts modified
- layers changed
- dependencies added

This is Phase 8 — Evolution.

---

# Core Principle

Architecture protects meaning.

If architecture breaks:

domain meaning leaks

This skill detects structural violations.

---

# What This Skill Validates

This skill validates:

Domain layer purity  
Application layer orchestration rules  
Infrastructure isolation  
Shell boundary correctness  
Dependency direction  
Context isolation  

---

# Layer Dependency Rules

Allowed:

Shell → Application → Domain  
Infrastructure → Application → Domain  

Not allowed:

Domain → Application  
Domain → Infrastructure  
Application → Shell  
Domain → Shell  

---

# Domain Layer Checks

Domain must NOT:

import infrastructure  
call database  
call HTTP  
call AI services  
depend on frameworks  

Detect violations.

---

# Application Layer Checks

Application must:

orchestrate domain  
call repositories (interfaces)  

Application must NOT:

contain domain rules  
call database directly  
depend on frameworks  

---

# Infrastructure Layer Checks

Infrastructure must:

implement ports  
handle IO  

Infrastructure must NOT:

contain domain rules  
orchestrate workflows  
mutate entities arbitrarily  

---

# Shell Layer Checks

Shell must:

call use cases  
translate input/output  

Shell must NOT:

contain domain logic  
call repositories  
orchestrate workflows  

---

# Context Boundary Checks

Contexts must NOT:

share entities  
share aggregates  
share invariants  

Contexts must communicate via:

events  
interfaces  
translators  

---

# Dependency Direction Check

Detect:

Domain importing infrastructure  
Application importing controllers  
Context importing other context domain  

Flag violations.

---

# Step-by-Step Validation

## Step 1 — Analyze layers

Identify:

domain  
application  
infrastructure  
shell  

---

## Step 2 — Analyze dependencies

Check imports:

layer → layer

---

## Step 3 — Detect violations

Example:

Domain imports repository implementation

Violation.

---

## Step 4 — Check contexts

Verify:

no shared domain objects  
no cross-context invariants  

---

## Step 5 — Validate communication

Check:

events  
interfaces  
translators  

---

# Violation Template

Violation:

Domain depends on infrastructure

Location:

domain/order.py

Problem:

imports PostgresRepository

Fix:

use repository interface

---

# Example

Detected:

Application calls SQL client

Violation:

Application must not depend on database

Fix:

move to repository

---

# Context Violation Example

Detected:

OrderContext imports Payment entity

Violation:

cross-context domain dependency

Fix:

use event or interface

---

# Output Template

The agent should output:

## Layer Violation

Domain → Infrastructure dependency

---

## File

domain/order.py

---

## Problem

imports PostgresRepository

---

## Fix

use OrderRepository interface

---

# Validation Categories

Layer violations  
Dependency direction violations  
Context boundary violations  
Domain purity violations  
Architecture drift  

---

# Clean Architecture Rules

Domain:

pure

Application:

orchestration

Infrastructure:

implementation

Shell:

interaction

Validate all.

---

# Rules

Checker must:

analyze dependencies  
validate layers  
validate contexts  
detect violations  

Checker must NOT:

refactor automatically  
modify architecture  

Only detect.

---

# Goal

Enforce architecture consistency.

Protect DDD boundaries.

Prevent structural erosion.