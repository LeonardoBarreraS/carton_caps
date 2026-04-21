---
name: 7-2-system-entry-points
description: Defines the system input boundary by generating handlers that receive external input, map it to application commands, invoke use cases, and return responses, without introducing business logic or infrastructure concerns.
---

# System Entry Points (Phase 7.2)

This skill defines the **input boundary of the system**.

It transforms:

- external input

into:

- use case execution

---

# Core Principle

System entry points answer:

> "How does the external world interact with the system?"

They implement the transformation:

external input → command → use case → response

They do NOT define:

- business logic  
- workflows  
- domain rules  
- infrastructure behavior  

---

# Role in the Architecture

System entry points:

- belong to the **Shell Layer**  
- are the **interface between external world and application layer**  
- expose use cases to the outside  

They act as:

> input translators

---

# Responsibilities

System entry points must:

- receive external input  
- validate input structure (not domain rules)  
- map input to command objects  
- invoke use cases  
- map results to output format  
- return responses  

System entry points must NOT:

- contain domain logic  
- orchestrate workflows  
- call repositories or adapters directly  
- implement infrastructure concerns  

---

# Inputs

This skill requires:

- use cases (Phase 5.1)  
- command definitions (Phase 5.1)  

---

# Outputs

This skill produces:

- handlers / controllers  
- input-to-command mappings  
- response mappings  

---

# Supported Entry Types

System entry points may include:

- HTTP endpoints (REST, GraphQL)  
- CLI commands  
- event consumers  
- webhooks  
- scheduled jobs  

All follow the same pattern.

---

# Step-by-Step Definition

## Step 1 — Identify use cases

Example:

- CreateOrderUseCase  
- AssignTaskUseCase  

---

## Step 2 — Define input structure

Example:

CreateOrderInput  
- user_id  
- items  

---

## Step 3 — Map input to command

Example:

CreateOrderCommand(  
    user_id,  
    items  
)  

---

## Step 4 — Invoke use case

Example:

create_order_use_case.execute(command)  

---

## Step 5 — Map result to output

Example:

CreateOrderResponse  
- order_id  
- status  

---

# Entry Point Template

Handler:

1. receive input  
2. validate structure  
3. build command  
4. call use case  
5. return response  

---

# Example — HTTP Entry

Input:

POST /orders  

Handler:

- parse request  
- create CreateOrderCommand  
- call CreateOrderUseCase  
- return response  

---

# Example — CLI Entry

Command:

app create-order  

Handler:

- parse arguments  
- create CreateOrderCommand  
- call use case  
- print result  

---

# Example — Event Consumer

Incoming event:

OrderRequested  

Handler:

- parse event  
- create command  
- call use case  

---

# Folder Structure

/shell  
    /entrypoints  
        /http  
        /cli  
        /events  

---

# Dependency Direction

External world  
↓  
Entry point  
↓  
Use case  
↓  
Domain  

Entry points depend on:

- use cases  

They do NOT depend on:

- domain directly  
- infrastructure implementations  

---

# Rules

System entry points must:

- expose use cases  
- translate input/output  
- remain thin and simple  
- be protocol-agnostic at design level  

System entry points must NOT:

- contain domain logic  
- orchestrate workflows  
- call repositories or adapters  
- depend on specific frameworks  

---

# Goal

Define the **system boundary** by:

- exposing use cases to the external world  
- translating input into commands  
- returning results to callers  

System entry points enable interaction with the system while preserving the purity of the application and domain layers.

