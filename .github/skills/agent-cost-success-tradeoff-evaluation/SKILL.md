---
name: agent-cost-success-tradeoff-evaluation
description: Evaluate whether an agent or multi-agent system achieves task success efficiently with minimal cost and latency. Use this when optimizing model usage, tool selection, and execution efficiency.
---

# Agent Cost / Success Trade-off

This skill evaluates whether an agent achieves **high success with efficient resource usage**.

This is a **Level 3 — System Efficiency Evaluation**.

An agent can be:

- correct but extremely expensive  
- fast but inaccurate  
- accurate but slow  

This skill evaluates the **optimal balance** between:

- success rate  
- cost  
- latency  

A robust system must maximize:

success / cost

---

# When to use this skill

Use this skill when you need to:

- optimize agent cost
- evaluate model selection
- compare architectures
- optimize multi-agent systems
- reduce token usage
- reduce latency
- evaluate tool efficiency
- optimize planning depth
- benchmark agent performance

---

# Core Question

Does the system achieve success efficiently?

A good agent:

high success  
low cost  
low latency  

A bad agent:

high cost  
low improvement  

---

# Conceptual Model

Agent Execution  
↓  
Tokens used  
Tools called  
Steps executed  
Time elapsed  
↓  
Final result  
↓  
Compute efficiency

Efficiency = success / cost

---

# Example

Agent A

success: 95%  
tokens: 20k  

Agent B

success: 93%  
tokens: 3k  

Agent B is more efficient.

---

# What This Skill Evaluates

## Cost

- token usage
- model size
- tool calls
- compute usage

## Success

- task completion
- correctness
- goal achievement

## Latency

- execution time
- step count
- response delay

---

# Failure Modes

High cost minimal gain  
Large model unnecessary

Overuse of large models  
GPT-4 for trivial tasks

Excessive tool calls  
Repeated retrieval

Unnecessary planning  
Too many reasoning steps

Latency bottlenecks  
Slow execution chain

Multi-agent overhead  
Too many agents

Inefficient retries  
Repeated failures

---

# Example Failure

Task:

"Summarize paragraph"

Agent:

planner agent  
retriever agent  
analysis agent  
writer agent  

Over-engineered.

High cost for simple task.

---

# Correct Behavior

Small model

single step

direct summary

Efficient.

---

# Evaluation Checklist

Cost

- Are large models necessary?
- Are tool calls minimal?
- Is token usage reasonable?

Success

- Is goal achieved?
- Is output correct?
- Is quality acceptable?

Latency

- Is execution fast?
- Are steps minimal?
- Are delays avoided?

---

# Evaluation Pipeline

Step 1 — Capture execution

Step 2 — Measure cost

Step 3 — Measure success

Step 4 — Measure latency

Step 5 — Compute efficiency

Step 6 — Compare alternatives

Step 7 — Score trade-off

---

# Metrics

Success Rate

successful_runs / total_runs

Cost

tokens + tool_calls + compute

Latency

execution_time

Efficiency Score

success / cost

Cost Efficiency

success_rate / token_usage

Latency Efficiency

success_rate / time

---

# Example Evaluation

System A

success: 0.95  
tokens: 20k  
latency: 12s  

System B

success: 0.92  
tokens: 4k  
latency: 2s  

System B better trade-off.

---

# Output Schema

{
  "success_rate": float,
  "token_usage": int,
  "latency": float,
  "tool_calls": int,
  "cost_score": float,
  "efficiency_score": float,
  "diagnosis": ""
}

---

# Observability Signals

Track:

- token usage per task
- cost per success
- latency per run
- model usage distribution
- tool call count
- retries
- agent count

These indicate efficiency.

---

# Best Practices

Use smallest capable model

Avoid unnecessary agents

Minimize tool calls

Limit planning depth

Cache results

Use retrieval sparingly

Avoid redundant reasoning

Use early stopping

Optimize architecture

---

# Interpretation Guide

Score | Meaning
------|--------
1.0 | optimal efficiency
0.8+ | efficient system
0.6–0.8 | acceptable cost
0.4–0.6 | inefficient
0.2–0.4 | very costly
<0.2 | unusable cost

---

# Mental Model

Level 1 ensures:

agent can act

Level 2 ensures:

agent reasons correctly

Level 3 ensures:

system scales efficiently

Cost/success trade-off ensures:

the system is practical

Best system:

correct  
stable  
efficient