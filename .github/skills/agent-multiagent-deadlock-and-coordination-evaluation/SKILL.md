---
name: agent-multiagent-deadlock-and-coordination-evaluation
description: Evaluate coordination behavior in multi-agent systems, including delegation, synchronization, and termination. Use this when validating multi-agent workflows, planner–executor loops, and distributed agent orchestration.
---

# Multi-Agent Deadlocks and Coordination

This skill evaluates **coordination reliability in multi-agent systems**.

This is a **Level 3 — Systemic Multi-Agent Evaluation**.

When multiple agents collaborate, failures emerge that do not exist in single-agent systems:

- deadlocks  
- livelocks  
- circular delegation  
- coordination collapse  

This skill evaluates whether agents **cooperate correctly to complete tasks**.

---

# When to use this skill

Use this skill when you need to:

- evaluate multi-agent systems
- validate planner–executor architecture
- test agent delegation logic
- detect circular loops
- evaluate orchestration reliability
- validate task ownership
- test termination conditions
- evaluate CrewAI / LangGraph systems
- debug multi-agent workflows

---

# Core Question

Do multiple agents coordinate correctly to complete a task?

A valid multi-agent system must:

- delegate correctly  
- synchronize properly  
- terminate when complete  

---

# Conceptual Model

Planner Agent  
↓  
Delegates task  
↓  
Executor Agent  
↓  
Returns result  
↓  
Planner validates  
↓  
Task complete

Coordination must converge.

---

# Failure Modes

## Deadlock

Agents wait for each other indefinitely.

Planner waits for executor  
Executor waits for planner  

No progress.

---

## Livelock

Agents act repeatedly but never complete.

Planner → executor  
Executor → planner  
Planner → executor  

Infinite loop.

---

## Circular Delegation

Agents delegate tasks back and forth.

Agent A → Agent B  
Agent B → Agent A  

No task ownership.

---

## Missing Termination

Agents continue after goal reached.

System keeps executing unnecessarily.

---

## Delegation Confusion

Multiple agents try to perform same task.

Duplicate execution.

---

# Example Failure

Content pipeline:

Planner → "Generate report"  
Executor → "Need clarification"  
Planner → "Clarify report"  
Executor → "Need clarification"  

Loop.

No completion.

---

# Correct Behavior

Planner:

delegate task

Executor:

complete task

Planner:

validate result

Terminate.

---

# What This Skill Evaluates

## Delegation Correctness

- Is task assigned to correct agent?
- Is responsibility clear?
- Is ownership defined?

## Synchronization

- Do agents wait correctly?
- Are dependencies respected?
- Is execution ordered?

## Termination

- Does system stop when complete?
- Are loops prevented?
- Is goal detection implemented?

---

# Evaluation Checklist

Delegation

- Is task assigned once?
- Is ownership defined?
- Is delegation necessary?

Coordination

- Do agents communicate clearly?
- Are dependencies satisfied?
- Are responses consumed?

Termination

- Is goal detected?
- Does execution stop?
- Are loops avoided?

---

# Evaluation Pipeline

Step 1 — Capture agents

Step 2 — Capture delegation flow

Step 3 — Detect loops

Step 4 — Detect deadlocks

Step 5 — Detect duplicate execution

Step 6 — Evaluate termination

Step 7 — Score coordination

---

# Example Evaluation

Agents:

Planner  
Executor  

Flow:

Planner → Executor  
Executor → Planner  
Planner → Executor  
Executor → Planner  

Loop detected.

Coordination failure.

---

# Metrics

Deadlock Rate

deadlocks / runs

Loop Rate

loops_detected / runs

Delegation Accuracy

correct_delegations / total_delegations

Termination Accuracy

correct_terminations / runs

Coordination Score

weighted combination

---

# Output Schema

{
  "agents": [],
  "delegation_flow": [],
  "deadlock_detected": true/false,
  "loop_detected": true/false,
  "circular_delegation": true/false,
  "termination_detected": true/false,
  "coordination_score": float,
  "diagnosis": ""
}

---

# Observability Signals

Track:

- delegation chains
- loop frequency
- deadlock occurrences
- task ownership conflicts
- duplicate executions
- termination failures
- agent handoff count

These indicate coordination health.

---

# Best Practices

Define agent roles clearly

Assign task ownership

Prevent circular delegation

Implement termination conditions

Limit delegation depth

Track task state

Use coordinator agent

Avoid symmetric delegation

---

# Interpretation Guide

Score | Meaning
------|--------
1.0 | perfect coordination
0.8+ | mostly stable
0.6–0.8 | minor loops
0.4–0.6 | coordination issues
0.2–0.4 | frequent deadlocks
<0.2 | unusable multi-agent system

---

# Mental Model

Single agent:

planning problem

Multi-agent:

coordination problem

System must:

delegate  
execute  
synchronize  
terminate  

Coordination failure = system failure