---

name: meta-semantic-change-impact
description: Analyzes a system change request and produces a phase-scoped evolution plan by projecting the semantic delta through the 7 phases of Stage 1 (Semantic Design), preserving invariants and architectural integrity while identifying impacted layers and propagation paths.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Semantic Change Impact & Evolution Planner

## Purpose

This skill determines **how a system must evolve** when a change is introduced.

It analyzes a change request and produces a **structured Evolution Plan** that:

* Classifies the change (semantic, behavioral, technical)
* Identifies impacted semantic elements
* Determines the correct entry phase in the 7-phase pipeline
* Projects the delta through affected phases
* Ensures invariants and architectural integrity are preserved

This skill operates strictly within:

> **Stage 1: Semantic Design (Phases 1–7)**

It does NOT execute changes. It defines **how changes must be applied**.

---

## Core Principle

> System evolution = projection of a **semantic delta** through the design pipeline

The skill ensures:

* Minimal intervention
* Maximum semantic precision
* No invariant violations
* No architectural degradation

---

## Input

The input is **unstructured natural language**, typically written by a human expressing a need, request, or change.

Examples:

* "We need to allow users to cancel orders after payment"
* "Integrate a new payment provider"
* "Optimize response time of the recommendation system"

### Input Characteristics

* May be ambiguous or incomplete
* May mix domain, behavioral, and technical concerns
* May lack explicit system references

### Responsibility of the Skill

The skill MUST:

1. Interpret and normalize the unstructured request
2. Extract implicit intent and assumptions
3. Identify missing information (without inventing facts)
4. Transform the request into a structured internal representation

---

### Internal Normalization Step (implicit, not exposed as separate output)

The LLM should internally derive:

```json
{
  "interpreted_intent": "string",
  "assumptions": [],
  "ambiguities": [],
  "missing_information": []
}
```

This normalized understanding becomes the basis for all subsequent analysis.

---json
{
"change_request": "string",
"existing_artifacts": {
"phase1": "optional",
"phase2": "optional",
"phase3": "optional",
"phase4": "optional",
"phase5": "optional",
"phase6": "optional",
"phase7": "optional"
}
}

````

---

## Output

The skill MUST produce two aligned artifacts:

### 1. `.md` (Human-readable Evolution Plan)
### 2. `.json` (Machine-readable Evolution Plan)

Both must contain identical information.

---

# OUTPUT — `.md`

## 1. Change Characterization
- Normalized Description
- Change Type (Semantic / Behavioral / Technical / Hybrid)
- Intent Type (New Capability / Extension / Optimization / Refactor)

## 2. Impacted Semantic Elements
- Workflows affected
- State transitions affected
- Invariants affected
- Domain concepts affected
- OR explicit: No Domain Impact

## 3. Layer Impact Matrix
| Layer | Impact | Operation |
|------|--------|----------|
| Domain | Yes/No | Add / Modify / None |
| Application | Yes/No | Add / Modify / None |
| Infrastructure | Yes/No | Add / Replace / Modify |
| Shell | Yes/No | Add / Modify / None |

## 4. Phase Entry Point
- Earliest phase to re-enter
- Justification

## 5. Phase Propagation Path
- Ordered list of phases impacted

## 6. Phase-Specific Action Plan
For each phase:
- What to analyze
- What to change
- What must remain unchanged

## 7. Invariant & Consistency Risk Analysis
- Existing invariants status
- Potential violations
- Required new invariants

## 8. Architectural Integrity Checks
- Layer boundary validation
- Dependency direction validation
- Context isolation validation

## 9. Evolution Strategy
- Incremental vs atomic
- Backward compatibility
- Migration needs

---

# OUTPUT — `.json`

```json
{
  "change_characterization": {
    "description": "string",
    "type": "semantic | behavioral | technical | hybrid",
    "intent": "new_capability | extension | optimization | refactor"
  },
  "semantic_impact": {
    "workflows": [],
    "state_transitions": [],
    "invariants": [],
    "domain_concepts": [],
    "no_domain_impact": true
  },
  "layer_impact": {
    "domain": {"impact": false, "operation": "none"},
    "application": {"impact": false, "operation": "none"},
    "infrastructure": {"impact": true, "operation": "add"},
    "shell": {"impact": false, "operation": "none"}
  },
  "phase_entry_point": {
    "phase": 6,
    "justification": "string"
  },
  "propagation_path": [6,7],
  "phase_actions": {
    "6": {
      "analyze": [],
      "change": [],
      "preserve": []
    },
    "7": {
      "analyze": [],
      "change": [],
      "preserve": []
    }
  },
  "risk_analysis": {
    "invariant_status": "unchanged | modified",
    "risks": [],
    "new_invariants_required": []
  },
  "architecture_checks": {
    "layer_boundaries": "valid | violated",
    "dependency_direction": "valid | violated",
    "context_isolation": "valid | violated"
  },
  "evolution_strategy": {
    "approach": "incremental | atomic",
    "backward_compatibility": "required | not_required",
    "migration": "required | not_required"
  }
}
````

---

## Execution Steps

1. Normalize change request
2. Classify change type
3. Extract semantic delta
4. Identify impacted layers
5. Determine entry phase
6. Compute propagation path
7. Generate phase actions
8. Evaluate risks
9. Validate architecture
10. Produce `.md` and `.json`

---

## Constraints

* Do NOT redesign unaffected parts
* Do NOT introduce domain changes for technical-only changes
* Preserve invariants at all costs
* Respect phase isolation
* Maintain bounded context separation

---

## Final Insight

> This skill does not modify the system.
>
> It ensures that any modification is **semantically correct, minimal, and architecturally safe**.
