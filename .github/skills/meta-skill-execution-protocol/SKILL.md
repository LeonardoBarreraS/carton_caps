---
name: meta-skill-execution-protocol
description: Governs how the AI executes system design skills, enforcing structured outputs, strict phase discipline, and purpose-driven scope control across the full methodology.
---

# Skill Execution Protocol

This skill defines how ALL other skills must be executed.

---

# Core Principle

Each skill is a **local, purpose-driven transformation** within a **global, ordered pipeline**.

input artifacts → structured output artifacts

---

# Global Process Awareness (CRITICAL)

The system follows ordered phases:

1 → Problem  
2 → Domain  
3 → Architecture  
4 → Domain Implementation  
5 → Application  
6 → Infrastructure  
7 → Composition  
8 → Evolution  

Rules:

- Execute ONLY the current phase  
- Do NOT anticipate future phases  
- Do NOT generate artifacts from future steps  
- Do NOT collapse multiple phases into one  

---

# Skill Purpose Anchoring (CRITICAL)

Before executing any skill:

1. Identify the PURPOSE of the skill  
2. Define its RESPONSIBILITY boundary  
3. Generate ONLY what is required to fulfill that purpose  

Rules:

- If an element is not required by the purpose → DO NOT generate it  
- Do NOT complete future parts of the system  

The purpose defines WHAT must be produced.  
The AI must NOT go beyond that scope.

---

# Output Requirement (MANDATORY)

Every skill MUST produce:

1. `.md` → human-readable explanation  
2. `.json` → structured artifact  

Both must represent the SAME information.

---

# Execution Rules

## 1. Input Discipline
- Use ONLY provided inputs  
- Do NOT invent missing data  
- If data is missing, make assumptions explicit  

---

## 2. Phase Isolation
- Respect the current phase boundaries  
- Do NOT mix domain, application, infrastructure, or shell concerns  

---

## 3. Structural Consistency
- Follow the structure defined by the skill  
- Use consistent naming across artifacts  
- Ensure `.md` and `.json` alignment  

---

## 4. Traceability
Each output must reference:
- source workflows or concepts  
- related artifacts from previous phases  

---

## 5. No Premature Design
- Do NOT define infrastructure in early phases  
- Do NOT define APIs before application layer  
- Do NOT define execution before domain is complete  

---

## 6. No Logic Leakage
- Domain rules → only in domain layer  
- Orchestration → only in application layer  
- IO/technical details → only in infrastructure  

---


---

# Goal

Ensure that all skills execute as part of a **controlled, sequential, purpose-driven pipeline**, producing:

- structured  
- traceable  
- phase-correct  

artifacts that can be composed into a complete system.