---
name: 3-2-layered-architecture-generation
description: Defines the internal structure of each component using Clean Architecture layers, ensuring strict separation of concerns and protection of domain semantics.
---

# Layered Architecture Generation

## Purpose
This skill transforms **components** into **internal layered architectures**.

It defines:
- how each component is structured internally
- separation of responsibilities
- dependency direction
- protection of domain logic

This ensures that:

Domain meaning is **isolated, protected, and not corrupted by implementation details**.

---

## Core Principle

Architecture exists to:

protect domain semantics

NOT to define them.

Each component becomes a **self-contained system** with strict internal boundaries.

---

## Critical Rule

NO NEW DOMAIN SEMANTICS ARE CREATED IN THIS PHASE

This phase:
- structures existing domain logic  
- does NOT introduce new entities, rules, or workflows  

If domain logic appears here:
→ Phase 2 is incomplete

---

## When to Use

Use this skill when:
- components are defined
- context-to-component mapping exists
- domain model is complete
- before defining communication between contexts

---

## Strict Rules

### DO NOT:
- define new domain concepts
- modify aggregates or invariants
- introduce business logic in non-domain layers
- mix responsibilities across layers

### ONLY DEFINE:
- internal structure of components
- layer responsibilities
- dependency direction
- placement of domain elements

---

## Architectural Model

Each component must contain:

/component  
├── domain  
├── application  
├── infrastructure  
└── shell  

Architecture is **per component**, not global.

---

## Layer Responsibilities

---

### Domain Layer

Contains:
- entities  
- value objects  
- aggregates  
- process entities  
- invariants  
- domain services  
- domain events  
- policies  

Responsibilities:
- define state  
- enforce invariants  
- define valid transitions  

Must NOT:
- depend on any other layer  
- include infrastructure or frameworks  
- include orchestration logic  

Domain is pure.

---

### Application Layer

Contains:
- use cases  
- commands  
- queries  
- DTOs  
- ports (interfaces)  
- orchestrators  

Responsibilities:
- coordinate workflows  
- invoke domain behavior  
- manage execution flow  

Must NOT:
- define domain rules  
- contain entities or invariants  
- perform IO  

Application controls flow.

---

### Infrastructure Layer

Contains:
- repository implementations  
- database adapters  
- external API clients  
- messaging systems  
- AI integrations  
- persistence logic  

Responsibilities:
- execute IO  
- implement ports  
- integrate external systems  

Must NOT:
- define domain rules  
- enforce invariants  
- control workflows  

Infrastructure executes effects.

---

### Shell Layer

Contains:
- controllers  
- endpoints  
- request/response DTOs  
- input adapters  
- routing  
- CLI interfaces  

Responsibilities:
- receive input  
- call application use cases  
- return responses  

Must NOT:
- implement domain logic  
- orchestrate workflows  
- access repositories directly  

Shell is the interaction boundary.

---

## Dependency Direction

Dependencies must flow inward:

shell → application → domain  
infrastructure → application → domain  

Rules:
- domain depends on nothing  
- application depends only on domain  
- infrastructure depends on domain + application  
- shell depends only on application  

Never reverse dependencies.

---

## Execution Methodology

Follow this reasoning pipeline:

---

### Step 1 — Iterate Over Components

For each component defined in Phase 3.1:

Create internal structure.

---

### Step 2 — Define Layer Skeleton

Create:

/component  
/domain  
/application  
/infrastructure  
/shell  

---

### Step 3 — Map Domain Elements

From Phase 2:

Place into domain layer:
- entities  
- value objects  
- aggregates  
- process entities  
- invariants  
- domain services  

---

### Step 4 — Define Application Layer

From behaviors and workflows:

Place:
- use cases  
- workflow orchestrators  
- commands and queries  
- ports  

---

### Step 5 — Define Infrastructure Layer

Place:
- repository implementations  
- adapters  
- integrations  
- persistence  

---

### Step 6 — Define Shell Layer

Place:
- controllers  
- endpoints  
- input/output handlers  

---

### Step 7 — Validate Separation of Concerns

Ensure:
- domain is pure  
- application contains no domain rules  
- infrastructure contains no domain logic  
- shell contains no orchestration  

---

### Step 8 — Validate Dependency Rules

Ensure:
- no outward dependencies  
- no domain dependency on infrastructure  
- no circular dependencies  

If violated:
→ architecture is incorrect

---

## Output Format (MANDATORY)

### Markdown

# Layered Architecture

## Components

### <Component Name>

- domain  
- application  
- infrastructure  
- shell  

---

## Folder Structure

/components  
/<component-name>  
/domain  
/application  
/infrastructure  
/shell  

---

## Dependency Direction

- shell → application → domain  
- infrastructure → application → domain  

---

## Layer Rules

### Domain
- no external dependencies  
- no frameworks  

### Application
- no domain rules  
- no IO  

### Infrastructure
- no domain logic  
- implements ports  

### Shell
- no domain logic  
- no orchestration  

---

### JSON

{
  "components": [
    {
      "name": "",
      "layers": ["domain", "application", "infrastructure", "shell"]
    }
  ],
  "dependency_direction": [
    "shell -> application -> domain",
    "infrastructure -> application -> domain"
  ]
}

---

## Completion Criteria

The skill is complete when:
- each component has all four layers  
- responsibilities are clearly separated  
- domain layer is pure  
- dependency direction is correct  
- no semantic leakage occurs  
- JSON output is valid and structured  

---

## Key Insight

This skill transforms:

Structural boundaries → Protected internal architecture  

It ensures:
- domain logic is isolated  
- orchestration is separated  
- infrastructure cannot corrupt meaning  

If layering is incorrect:
- domain becomes coupled to infrastructure  
- invariants are violated  
- system becomes fragile  

Layered architecture is the mechanism that preserves domain integrity over time.

