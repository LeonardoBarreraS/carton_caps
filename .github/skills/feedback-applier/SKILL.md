---

name: feedback-applier
description: Performs dependency-aware diagnostic analysis of structured feedback by discovering all artifacts in the system_design directory, selecting relevant artifacts via dependency traversal, and producing a deterministic transformation plan as a JSON file without modifying any artifact.
---

# ⚙️ Skill: Feedback Applier (Dependency-Aware Diagnostic Engine with Artifact Discovery)

## (Structured Feedback → Global Discovery → Dependency Filtering → Diagnostic + Transformation Plan)

---

## 1. Purpose

Process structured feedback and produce a **deterministic, dependency-aware diagnostic and transformation plan** that:

* Discovers **all artifacts in the system_design folder**
* Selects **only dependency-related artifacts**
* Identifies **where changes must occur**
* Explains **why (causal reasoning)**
* Outputs a **JSON file in the same folder as the input artifact**
* **Does NOT modify any artifact**

This skill acts as a:

**Filesystem-aware semantic diagnostic engine constrained by dependency relationships**

---

## 2. Critical Constraints

* MUST NOT modify any artifact or file
* MUST output a JSON file in the SAME folder as the input artifact
* MUST scan ALL artifacts but ONLY analyze dependency-related ones
* MUST separate discovery from analysis

---

## 3. Conceptual Role

Structured Feedback
→ Artifact Discovery (global)
→ Dependency Filtering (local subgraph)
→ Diagnostic + Transformation Plan
→ Execution (separate step)

---

## 4. Inputs

### Required

1. Current Artifact (JSON or MD)
2. Structured Feedback (JSON array)
3. Artifact Path

---

### Optional

4. Dependency Map (if available)
5. Phase / Task

---

## 5. Artifact Discovery (MANDATORY FIRST STEP)

The system MUST:

```text
1. Traverse root directory: /system_design
2. Recursively scan all subfolders (phase folders)
3. Collect ALL files with extensions:
   - .json
   - .md
```

---

### 5.1 Build Artifact Registry

For each file, extract:

* file_path
* file_name
* inferred_phase (from folder or naming)
* artifact_type (if inferable)

---

### 5.2 Example Registry

```json
[
  {
    "artifact": "state_model.json",
    "phase": "2",
    "path": "system_design/phase_2/state_model.json"
  },
  {
    "artifact": "invariants.json",
    "phase": "3",
    "path": "system_design/phase_3/invariants.json"
  }
]
```

---

## 6. Dependency-Based Filtering (CRITICAL STEP)

After discovery:

> DO NOT analyze all artifacts

Instead:

```text
1. Identify primary target artifact from feedback
2. Traverse dependency graph:
   - UPSTREAM (inputs)
   - DOWNSTREAM (derived artifacts)
   - LATERAL (same-level relations)
3. Select ONLY artifacts within this dependency subgraph
4. Ignore all unrelated artifacts
```

---

### 6.1 Propagation Limit

Max depth = 1–2 levels

---

## 7. Output File

### Location

Same directory as input artifact

### Name

`<artifact_name>.feedback-plan.json`

---

## 8. Output Structure

```json
{
  "artifact_reference": "<path>",
  "generated_at": "<timestamp>",
  "diagnostic_scope": "DEPENDENCY_CONSTRAINED",
  "artifact_discovery": [
    {
      "artifact": "<artifact>",
      "relation": "PRIMARY | UPSTREAM | DOWNSTREAM | LATERAL"
    }
  ],
  "diagnostic": [
    {
      "affected_phase": "<phase>",
      "artifact": "<artifact>",
      "impact_type": "DIRECT | UPSTREAM | DOWNSTREAM | LATERAL",
      "dependency_path": "<relationship>",
      "reason": "<causal explanation>"
    }
  ],
  "transformation_plan": [
    {
      "target_artifact": "<artifact>",
      "target_location": "<section>",
      "action": "<ACTION>",
      "instruction": "<precise change>",
      "source_feedback_id": "<id>",
      "priority": "HIGH | MEDIUM | LOW"
    }
  ],
  "consistency_risks": [
    {
      "description": "<risk>",
      "severity": "HIGH | MEDIUM | LOW"
    }
  ]
}
```

---

## 9. Dependency Model (Reference)

Workflow → Concepts → Entities → State → Invariants → Contexts

---

## 10. Core Responsibilities

### 10.1 Parse Feedback

* Preserve feedback_id
* Maintain order

---

### 10.2 Discover Artifact Space

* Scan full system_design directory
* Build registry

---

### 10.3 Filter Relevant Artifacts

* Apply dependency traversal
* Select subgraph only

---

### 10.4 Diagnose Impact

For each feedback item:

* Identify DIRECT impact
* Identify UPSTREAM dependencies
* Identify DOWNSTREAM dependencies

---

### 10.5 Build Transformation Plan

For each affected artifact:

* define action
* define exact instruction
* maintain traceability

---

### 10.6 Detect Consistency Risks

Examples:

* broken invariants
* missing transitions
* inconsistent constraints

---

## 11. Supported Actions

ADD
REMOVE
MODIFY
MOVE
RENAME
SPLIT
MERGE
CONSTRAIN

---

## 12. Prompt Definition (Core Skill)

You are a Dependency-Aware Semantic Diagnostic Engine with filesystem awareness.

Your task is to analyze structured feedback and produce a transformation plan.

INPUT:

1. Current artifact
2. Structured feedback
3. Artifact path

EXECUTION STEPS:

1. Discover ALL artifacts in /system_design
2. Build artifact registry
3. Identify primary target artifact
4. Traverse dependency graph
5. Select ONLY relevant artifacts
6. Perform diagnostic
7. Generate transformation plan

STRICT RULES:

* DO NOT modify any artifact
* DO NOT generate updated artifacts
* DO NOT analyze all artifacts globally
* ONLY analyze dependency-connected artifacts
* Separate discovery from analysis
* Maintain traceability to feedback_id
* Output MUST be valid JSON

OUTPUT:

Return ONLY a JSON object matching the schema.

---

## 13. Behavioral Guarantees

* Deterministic
* Dependency-constrained
* Filesystem-aware
* No global drift
* No direct modification

---

## 14. Key Insight

This skill ensures:

> Full system visibility + selective semantic reasoning

---

## 15. Final Principle

Discover everything.
Analyze only what matters.
Transform nothing directly.
