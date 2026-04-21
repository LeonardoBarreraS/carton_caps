---
name: agent-tool-accuracy-evaluation
description: Evaluate whether an agent selects the correct tool and constructs valid tool calls. Use this when validating tool-calling agents, debugging wrong tool usage, or designing reliable agent action interfaces.
---

# Agent Tool Accuracy

This skill evaluates whether an agent correctly translates **user intent into executable tool calls**.

This is a **Level 1 — Action Interface** evaluation.

The agent behaves like a semantic compiler:

intent → tool → execution

If tool accuracy fails, the agent cannot act correctly even if reasoning is perfect. :contentReference[oaicite:0]{index=0}

---

# When to use this skill

Use this skill when you need to:

- evaluate tool-calling agents
- debug wrong tool selection
- validate function calling
- validate structured tool arguments
- detect tool hallucination
- evaluate ReAct agents
- test agent action reliability
- enforce tool schemas
- evaluate LLM → API behavior

---

# What This Skill Evaluates

This skill evaluates two dimensions:

1. Correct Tool Selection  
2. Tool Syntax and Argument Accuracy  

Both must be correct for a valid action.

---

# 1. Correct Tool Selection

Core Question:

Did the agent choose the correct tool for the user's intent?

This is an **intent classification problem** over available tools. :contentReference[oaicite:1]{index=1}

The agent must map:

User intent → tool capability

---

## Example

Available tools:

- search_products
- refund_order
- track_order

User:

"Where is my order?"

Correct tool:

track_order

Failure:

search_products

The agent selected a related but incorrect capability.

---

## Failure Modes

Tool hallucination  
Agent calls non-existent tool

Wrong tool selection  
Agent chooses incorrect capability

Overgeneralization  
Agent defaults to generic search tool

Capability confusion  
Agent confuses similar tools

Fallback bias  
Agent repeatedly uses same tool

---

# 2. Tool Syntax and Argument Accuracy

Core Question:

Did the agent construct the tool call correctly?

This evaluates **API contract compliance**. :contentReference[oaicite:2]{index=2}

The agent must:

- provide required parameters
- use correct types
- respect schema
- use meaningful values

---

## Example

Tool:

transfer_funds(account_id, amount)

Correct:

transfer_funds("user_123", 100)

Failure:

transfer_funds("user_123", "100")

Wrong type.

Semantic failure:

transfer_funds("wrong_account", 100)

Format correct, meaning wrong.

---

# Evaluation Checklist

## Tool Selection

- Does tool match user intent?
- Is better tool available?
- Is generic tool overused?
- Is tool semantically correct?
- Is tool hallucinated?

## Argument Accuracy

- JSON valid
- Required fields present
- Types correct
- Values meaningful
- No extra parameters
- Schema respected

---

# Evaluation Pipeline

Step 1 — Capture user request

Step 2 — Capture selected tool

Step 3 — Validate tool choice

Step 4 — Validate arguments

Step 5 — Score action correctness

---

# Scoring

Tool Selection Accuracy

correct_tool / total_calls

Argument Accuracy

valid_arguments / total_calls

Execution Accuracy

successful_calls / total_calls

---

# Example Evaluation

User:

"Refund my last order"

Agent call:

search_orders()

Failure:

Wrong tool.

Correct:

refund_order(order_id)

---

# Output Schema

{
  "user_intent": "",
  "selected_tool": "",
  "expected_tool": "",
  "tool_correct": true/false,
  "arguments_valid": true/false,
  "argument_errors": [],
  "diagnosis": ""
}

---

# Observability Signals

Track:

- tool selection accuracy
- schema violations
- retries
- fallback usage
- tool error rate
- invalid arguments
- hallucinated tools

These indicate agent reliability.

---

# Best Practices

Use strict tool schemas

Avoid overlapping tool capabilities

Make tool descriptions discriminative

Enforce structured outputs

Validate before execution

Disallow free-form tool calls

Use typed parameters

Reject missing arguments

---

# Interpretation Guide

Score | Meaning
------|--------
1.0 | correct tool + correct arguments
0.8+ | mostly correct
0.6–0.8 | minor issues
0.4–0.6 | frequent mistakes
0.2–0.4 | unreliable tool usage
<0.2 | broken agent interface

---

# Mental Model

Tool accuracy guarantees:

The agent can act correctly.

Level hierarchy:

Level 1 — Tool Accuracy → can act  
Level 2 — Reasoning → can plan  
Level 3 — Multi-agent → can coordinate  

Tool accuracy is the **action correctness layer** of agent systems.