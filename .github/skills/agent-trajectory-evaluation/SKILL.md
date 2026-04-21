---
name: agent-trajectory-evaluation
description: Evaluate the full sequence of actions taken by an agent to determine whether it efficiently and correctly reaches the goal. Use this when validating planning quality, multi-step reasoning, and execution efficiency.
---

# Agent Trajectory Evaluation

This skill evaluates the **full action trajectory** of an agent.

A trajectory is the sequence:

initial state → steps → goal

This is a **Level 2 — Reasoning and Planning** evaluation.

Instead of evaluating individual actions, this skill evaluates:

- the sequence of actions  
- planning efficiency  
- goal-directed behavior  
- step relevance  

The question becomes:

Did the agent follow a coherent path to the goal?

---

# When to use this skill

Use this skill when you need to:

- evaluate multi-step agents
- validate planning quality
- detect inefficient execution
- detect redundant tool calls
- evaluate reasoning chains
- analyze agent traces
- debug long workflows
- evaluate ReAct trajectories
- measure planning efficiency

---

# Core Question

Does the agent take the correct sequence of steps to reach the goal?

This includes:

- step relevance  
- step ordering  
- step efficiency  
- goal completion  

---

# Conceptual Model

Goal  
↓  
Planning  
↓  
Step 1  
↓  
Step 2  
↓  
Step 3  
↓  
Goal reached

Trajectory = all steps combined

---

# Example

Goal:

Generate sales report

Bad trajectory:

search data  
search data again  
summarize  
search again  
summarize again  

Redundant steps.

Good trajectory:

retrieve data  
aggregate  
generate report  

Efficient.

---

# What This Skill Evaluates

## 1. Efficiency

Does the agent use minimal steps?

Failure:

- repeated tool calls
- unnecessary reasoning
- redundant queries

---

## 2. Efficacy

Does the trajectory reach the goal?

Failure:

- stops early
- incomplete result
- wrong final output

---

## 3. Relevance

Does each step contribute to the goal?

Failure:

- irrelevant tools
- unrelated exploration
- random actions

---

# Failure Modes

Redundant steps  
Agent repeats actions

Irrelevant actions  
Agent performs unrelated steps

Inefficient exploration  
Agent searches excessively

Looping  
Agent repeats cycle

Premature termination  
Agent stops before completion

Wrong ordering  
Steps executed in wrong order

Tool thrashing  
Agent switches tools unnecessarily

---

# Example Failure

Goal:

"Find top 3 customers by revenue"

Agent:

search customers  
summarize customers  
search revenue  
search customers again  
calculate revenue  

Redundant.

Correct:

retrieve customers  
retrieve revenue  
sort  
return top 3

---

# Evaluation Checklist

Step relevance

- Does step contribute to goal?
- Is step necessary?
- Is step redundant?

Ordering

- Are steps logically ordered?
- Are dependencies respected?

Efficiency

- Are steps minimal?
- Are repeated calls avoided?

Goal completion

- Was goal reached?
- Is output complete?

---

# Evaluation Pipeline

Step 1 — Capture goal

Step 2 — Capture agent steps

Step 3 — Evaluate each step relevance

Step 4 — Detect redundancy

Step 5 — Evaluate efficiency

Step 6 — Score trajectory

---

# Example Evaluation

Goal:

"Summarize document"

Trajectory:

read document  
summarize  
summarize again  

Second summarize redundant.

Trajectory inefficient.

---

# Metrics

Step Relevance Score

relevant_steps / total_steps

Efficiency Score

minimal_steps / actual_steps

Goal Completion Score

goal_reached ? 1 : 0

Trajectory Score

weighted combination of above

---

# Output Schema

{
  "goal": "",
  "steps": [],
  "redundant_steps": [],
  "irrelevant_steps": [],
  "goal_reached": true/false,
  "efficiency_score": float,
  "relevance_score": float,
  "trajectory_score": float,
  "diagnosis": ""
}

---

# Observability Signals

Track:

- number of steps
- repeated tool calls
- loops detected
- irrelevant actions
- time to completion
- goal completion rate
- trajectory length

These indicate planning quality.

---

# Best Practices

Encourage minimal planning

Avoid repeated tool calls

Use goal-directed reasoning

Stop when goal reached

Prevent loops

Track executed steps

Use planning before acting

Cache intermediate results

---

# Interpretation Guide

Score | Meaning
------|--------
1.0 | optimal trajectory
0.8+ | efficient planning
0.6–0.8 | minor inefficiencies
0.4–0.6 | poor planning
0.2–0.4 | chaotic trajectory
<0.2 | unusable agent

---

# Mental Model

Level 1 evaluates:

single actions

Level 2 evaluates:

sequence of actions

Trajectory evaluation ensures:

agent thinks coherently over time

Good agent:

correct actions  
+ correct order  
+ minimal steps  
= coherent trajectory