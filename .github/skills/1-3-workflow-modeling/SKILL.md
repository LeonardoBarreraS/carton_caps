---
name: 1-3-workflow-modeling
description: Converts structured behaviors into high-level semantic workflows representing system transitions over time. Defines HOW behavior unfolds without introducing domain concepts or implementation.
---

# Workflow Modeling

## Purpose
This skill transforms system behaviors into **high-level workflows**.

It defines:
- how behavior unfolds over time
- how the system transitions between meaningful stages
- the minimal sequence of transformations

This is the third step of Semantic Design.

---

## Core Principle

Behavior defines WHAT  
Workflow defines HOW (at a behavioral level)

A workflow is a sequence of **semantic transitions**, not technical steps.

---

## When to Use

Use this skill when:
- Goal & Scope Definition is completed
- Behavior Definition is completed
- system behaviors and dependencies are known
- before domain modeling
- before entity definition

---

## Strict Rules

### DO NOT:
- define entities or domain concepts
- define architecture or layers
- define APIs or infrastructure
- define classes or code
- define detailed algorithms
- include technical steps (e.g., parse JSON, call API)

### ONLY DEFINE:
- workflows
- transitions
- behavioral sequences

---

## Execution Methodology

Follow this reasoning pipeline strictly:

---

### Step 1 — Identify Behavioral Flows

From:
- core behaviors
- behavioral dependencies

Ask:
Which behaviors naturally form a sequence?

Group related behaviors into flows.

---

### Step 2 — Define Workflow Steps

Transform grouped behaviors into:

step → step → step

Each step must:
- represent a meaningful transformation
- reflect a change in system behavior
- be semantically clear

#### Good:
receive → analyze → evaluate → respond

#### Bad:
receive → parse → tokenize → call API → handle JSON

---

### Step 3 — Ensure Transition Validity

Each step must imply:

something changes between steps

Ask:
- what progresses?
- what moves forward?
- what evolves?

If nothing changes → step is invalid

---

### Step 4 — Detect Multiple Workflows

Systems usually contain:

#### Primary Workflow
Main value delivery

#### Secondary Workflows
Supporting processes

#### Support Workflows (optional)
Error handling, retries, maintenance

Identify all major workflows.

---

### Step 5 — Name Workflows

Each workflow must have a clear semantic name.

Examples:
- Response Generation Workflow
- Execution Workflow
- Evaluation Workflow
- Training Workflow

---

### Step 6 — Define Transition Model (NEW)

For each workflow, define transitions explicitly:

Format:
Step A → Step B

This prepares:
- state modeling (next phase)
- process entities
- invariant detection

---

### Step 7 — Validate Minimality

A good workflow must:
- be minimal (no unnecessary steps)
- be semantic (not technical)
- be complete (covers behavior)
- be consistent with dependencies

---

## Output Format (MANDATORY)

### Markdown

# Workflow Modeling

## Identified Workflows

### Primary Workflow — <Name>
Steps:
step → step → step

Transitions:
step A → step B  
step B → step C  

Description:
...

---

### Secondary Workflows

#### <Workflow Name>
Steps:
step → step → step

Transitions:
...

Description:
...

---

### Support Workflows (Optional)

#### <Workflow Name>
Steps:
...

---

## Workflow Relationships (Optional)

- Workflow A triggers Workflow B
- Workflow C depends on Workflow A

---

### JSON

{
  "workflows": [
    {
      "name": "",
      "type": "primary | secondary | support",
      "steps": [],
      "transitions": [
        ["stepA", "stepB"],
        ["stepB", "stepC"]
      ],
      "description": ""
    }
  ],
  "relationships": []
}

---

## Completion Criteria

The skill is complete when:
- all major workflows are identified
- each workflow has a clear sequence
- transitions are explicitly defined
- workflows are named
- workflows are minimal and semantic
- no technical or implementation details are included
- JSON output is valid and structured

---

## Key Insight

This skill transforms:

Behavioral space → Temporal structure

It defines how the system evolves over time without defining:
- domain structure
- internal state models
- implementation details

This prepares:
- domain concept extraction
- process entity identification
- invariant detection

Workflows are the bridge between behavior and domain.

