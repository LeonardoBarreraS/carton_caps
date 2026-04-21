---
name: invariant-regression-detection
description: Detects violations of domain invariants after refactoring or feature changes.
---

# Invariant Regression Detection

This skill detects when domain invariants are broken.

It verifies:

- state validity
- allowed transitions
- aggregate consistency
- domain rules
- lifecycle constraints

This skill protects domain integrity.

---

# When to use this skill

Use this skill when:

- domain refactored
- new features added
- contexts split
- workflows changed
- entities modified
- services added

This is Phase 8 — Evolution.

---

# Core Principle

Domain invariants define:

what must always hold

If invariant breaks:

domain meaning breaks

This skill detects semantic regressions.

---

# What is an Invariant

Invariant:

rule that must always hold

Examples:

order cannot ship before payment  
task cannot complete twice  
execution cannot finish before evaluation  

---

# What This Skill Detects

This skill detects:

illegal state transitions  
missing validations  
broken aggregate consistency  
cross-entity rule violations  
invalid lifecycle flows  

---

# Step-by-Step Detection

## Step 1 — Identify invariants

Extract from:

entities  
aggregates  
domain services  
process entities  

---

## Step 2 — Identify changes

Detect:

new methods  
removed validations  
new transitions  
changed workflows  

---

## Step 3 — Check violations

Verify:

transitions allowed  
states valid  
rules enforced  

---

# Detection Template

Entity:

Order

Invariant:

must be paid before shipped

Check:

ship() without payment?

Violation detected.

---

# Example

Before:

Task:

Assigned → Completed

Invariant:

must be assigned first

After change:

complete() callable anytime

Violation:

Task completed without assignment

---

# Aggregate Consistency Detection

Aggregate:

Order

Invariant:

total = sum(items)

Check:

items changed  
total unchanged

Violation.

---

# Workflow Invariant Detection

Process entity:

Execution

States:

Planned → Running → Completed

Check:

Completed without Running

Violation.

---

# Cross-Entity Invariant Detection

Rule:

agent must exist before assignment

Check:

assign(task, agent_id)

agent missing

Violation.

---

# Output Template

The agent should output:

## Entity

Task

---

## Invariant

must be assigned before completed

---

## Detected Change

complete() bypasses assign()

---

## Violation

Task completed without assignment

---

## Fix Suggestion

add state validation

---

# Detection Categories

State transition violations  
Aggregate consistency violations  
Lifecycle violations  
Cross-entity rule violations  
Process invariant violations  

---

# Signals of Regression

removed validation  
new public setter  
direct state mutation  
missing guard clause  
skipped process step  

---

# Example Output

Invariant:

Order must be paid before shipped

Detected:

ship() callable anytime

Regression:

yes

---

# Rules

Invariant detection must:

- analyze entities
- analyze transitions
- analyze workflows
- analyze services

Must NOT:

- check infrastructure
- check controllers
- check DTOs

Only domain semantics.

---

# Relationship with Tests

This skill is:

semantic validation

Not:

unit testing

It detects conceptual breakage.

---

# Goal

Detect broken domain invariants.

Protect domain correctness.

Prevent semantic regressions.