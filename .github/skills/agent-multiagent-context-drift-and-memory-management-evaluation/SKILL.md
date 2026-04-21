---
name: agent-multiagent-context-drift-and-memory-management-evaluation
description: Evaluate whether multi-agent systems maintain consistent context, memory integrity, and state persistence across long interactions. Use this when validating memory reliability, context preservation, and state consistency.
---

# Multi-Agent Context Drift and Memory Management

This skill evaluates whether a multi-agent system **preserves context and memory over time**.

This is a **Level 3 — System Memory and State Reliability** evaluation.

In multi-agent systems, failures often occur when:

- context is forgotten  
- memory becomes inconsistent  
- constraints disappear  
- state is overwritten  
- irrelevant information dominates  

This skill ensures **state continuity across agents and time**.

---

# When to use this skill

Use this skill when you need to:

- evaluate agent memory reliability
- test long-running agent systems
- validate shared memory consistency
- detect context drift
- evaluate conversation persistence
- test knowledge retention
- validate state integrity
- debug multi-step workflows
- evaluate retrieval memory systems

---

# Core Question

Does the system preserve important context across time and agents?

A reliable system must:

- remember constraints  
- preserve goals  
- maintain shared state  
- avoid context corruption  

---

# Conceptual Model

Initial Context  
↓  
Agent A modifies state  
↓  
Agent B reads state  
↓  
Agent C updates memory  
↓  
Execution continues  
↓  
Final decision uses correct context

Context must remain consistent.

---

# Example

Initial constraint:

"Use USD currency"

Agent A:

creates report in USD

Agent B:

continues analysis

Agent C:

switches to EUR

Context drift detected.

---

# Failure Modes

Context drift  
Agents forget original instructions

Memory overwrite  
Important information replaced

State inconsistency  
Agents use different versions of context

Constraint forgetting  
Rules disappear over time

Irrelevant context dominance  
Noise replaces important information

Goal forgetting  
Agents lose original objective

Memory fragmentation  
Information split across agents

---

# Example Failure

Initial goal:

"Generate legal contract with clause A"

Agent A:

writes clause A

Agent B:

summarizes contract

Agent C:

rewrites contract without clause A

Constraint lost.

---

# Correct Behavior

Initial constraint:

Include clause A

All agents preserve clause A.

Context consistent.

---

# What This Skill Evaluates

## Context Preservation

- Are original instructions remembered?
- Are constraints preserved?
- Is goal maintained?

## Memory Integrity

- Is memory overwritten?
- Is state corrupted?
- Are updates consistent?

## Multi-Agent Consistency

- Do agents share same context?
- Are states synchronized?
- Is memory unified?

---

# Evaluation Checklist

Context

- Is original goal preserved?
- Are constraints remembered?
- Is scope consistent?

Memory

- Is memory overwritten?
- Are updates valid?
- Is information lost?

Consistency

- Do agents agree on state?
- Is shared memory aligned?
- Are conflicts resolved?

---

# Evaluation Pipeline

Step 1 — Capture initial context

Step 2 — Capture memory updates

Step 3 — Track state across agents

Step 4 — Detect drift

Step 5 — Detect overwrites

Step 6 — Evaluate consistency

Step 7 — Score memory reliability

---

# Example Evaluation

Initial:

"Return top 5 results"

Agent A:

retrieves 5

Agent B:

adds more results

Agent C:

returns 12 results

Constraint forgotten.

Context drift detected.

---

# Metrics

Context Preservation Score

constraints_preserved / constraints_total

Memory Consistency Score

consistent_states / total_states

Drift Rate

drift_events / runs

Memory Reliability Score

weighted combination

---

# Output Schema

{
  "initial_context": "",
  "memory_updates": [],
  "context_drift_detected": true/false,
  "constraint_loss": [],
  "state_inconsistency": true/false,
  "memory_overwrite": true/false,
  "memory_score": float,
  "diagnosis": ""
}

---

# Observability Signals

Track:

- constraint loss rate
- goal drift frequency
- memory overwrite events
- state mismatch
- context length growth
- irrelevant memory ratio
- shared memory conflicts

These indicate memory health.

---

# Best Practices

Use shared memory store

Re-anchor goals periodically

Summarize context regularly

Protect critical constraints

Version memory updates

Use structured state objects

Avoid uncontrolled context growth

Validate memory before use

---

# Interpretation Guide

Score | Meaning
------|--------
1.0 | stable context and memory
0.8+ | mostly consistent
0.6–0.8 | minor drift
0.4–0.6 | frequent context loss
0.2–0.4 | unstable memory
<0.2 | unusable multi-agent memory

---

# Mental Model

Level 1:

correct action

Level 2:

correct reasoning

Level 3:

correct system behavior

Context drift skill ensures:

system remembers what matters

Multi-agent systems fail when:

memory breaks

Reliable systems:

preserve context  
share memory  
maintain state  
avoid drift