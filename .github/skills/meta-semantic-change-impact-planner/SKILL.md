# Skill: Semantic Change Impact & Evolution Planner

## 1. Purpose

This skill analyzes a system change request and produces a structured **Evolution Plan** that determines:

* What must change
* Where to start in the 7-phase Semantic Design pipeline
* How far the change propagates
* What must remain invariant

The skill operates strictly within the universe of **Stage 1: Semantic Design (Phases 1–7)**.

It does NOT execute changes. It defines **how the system must evolve without breaking its semantic integrity**.

---

## 2. Input

### Required

* Change Request (natural language or structured)

### Optional (recommended)

* Existing system artifacts:

  * Phase 1 outputs (Goal, Behavior, Workflows, Constraints)
  * Phase 2 outputs (Domain Model, States, Invariants, Aggregates, Contexts)
  * Phase 3 outputs (Architecture, Context Mapping)
  * Phase 4–7 outputs (Implementation structure)

---

## 3. Output

A **Structured Evolution Plan** composed of the following sections:

---

## 4. Evolution Plan Structure

### 4.1 Change Characterization

* Normalized Description

* Change Type:

  * Semantic (Domain)
  * Behavioral (Application)
  * Technical (Infrastructure / Shell)
  * Hybrid

* Intent Type:

  * New Capability
  * Extension
  * Optimization
  * Refactor (no behavior change)

---

### 4.2 Impacted Semantic Elements

Identify the minimal semantic delta:

* Affected Workflows
* Affected State Transitions
* Affected Invariants
* Affected Domain Concepts (Entities, Value Objects, Aggregates)

If none are affected → explicitly state: **No Domain Impact**

---

### 4.3 Layer Impact Matrix

| Layer          | Impact | Operation              |
| -------------- | ------ | ---------------------- |
| Domain         | Yes/No | Add / Modify / None    |
| Application    | Yes/No | Add / Modify / None    |
| Infrastructure | Yes/No | Add / Replace / Modify |
| Shell          | Yes/No | Add / Modify / None    |

---

### 4.4 Phase Entry Point

Determine the earliest phase that must be re-entered:

* Domain impact → Phase 1 or 2
* Behavioral only → Phase 5
* Technical only → Phase 6 or 7

---

### 4.5 Phase Propagation Path

Define the exact path of execution through phases:

Examples:

* Phase 5 → 6 → 7
* Phase 2 → 3 → 4 → 5 → 6 → 7

Only include phases that are impacted.

---

### 4.6 Phase-Specific Action Plan

For each phase in the propagation path, define:

#### Phase 1 – Problem Understanding & Requirements

* Re-evaluate goal (if needed)
* Extend behavior definitions
* Update workflows
* Update constraints

#### Phase 2 – Semantic Modeling (Domain)

* Update domain concepts (if needed)
* Adjust state models
* Add/modify invariants
* Validate aggregate consistency
* Re-evaluate bounded contexts

#### Phase 3 – Structural Design (Architecture)

* Validate context boundaries
* Update context-to-component mapping
* Define communication changes (if any)

#### Phase 4 – Domain Layer Materialization

* Update entities/value objects
* Update aggregates
* Update domain services (if needed)
* Ensure invariants are enforced in code

#### Phase 5 – Application Layer Design

* Add/modify use cases
* Adjust orchestration logic
* Validate coordination across contexts

#### Phase 6 – Infrastructure Layer Design

* Implement/modify adapters
* Implement repositories or integrations
* Ensure no domain logic leakage

#### Phase 7 – Shell & Composition

* Update entry points (API, CLI, events)
* Update request/response mappings
* Update wiring and composition root

---

### 4.7 Invariant & Consistency Risk Analysis

Identify risks such as:

* Invariant violations
* Invalid state transitions
* Aggregate inconsistency
* Cross-context semantic leakage

Explicitly state whether:

* Existing invariants remain valid
* New invariants are required

---

### 4.8 Architectural Integrity Checks

Validate that the change does NOT:

* Break layer boundaries
* Introduce domain logic outside domain
* Invert dependency direction
* Couple bounded contexts improperly

---

### 4.9 Evolution Strategy Recommendation

Provide guidance on:

* Incremental vs atomic implementation
* Backward compatibility
* Data/state migration (if needed)

---

## 5. Transformation Logic (Execution Steps)

1. Normalize the change request
2. Classify the change (Semantic / Behavioral / Technical)
3. Extract semantic delta
4. Identify impacted layers
5. Determine phase entry point
6. Compute propagation path
7. Generate phase-specific actions
8. Perform invariant risk analysis
9. Validate architectural integrity
10. Output structured evolution plan

---

## 6. Constraints

* Do NOT redesign unaffected parts of the system
* Do NOT introduce domain changes if the change is purely technical
* Always prioritize invariant preservation
* Respect dependency direction (inward)
* Maintain bounded context isolation

---

## 7. Key Principle

> The system evolves by projecting a **semantic delta** through the 7 phases, starting from the earliest impacted phase and propagating forward, while preserving domain invariants and architectural boundaries.

---

## 8. Expected Behavior of the Skill

* Minimal intervention
* Maximum semantic precision
* Explicit reasoning over implicit assumptions
* Clear separation of domain, behavior, and infrastructure

---

## 9. Output Format

The final output MUST be structured, deterministic, and sectioned exactly as defined in Section 4.

No unstructured explanations outside the Evolution Plan.
