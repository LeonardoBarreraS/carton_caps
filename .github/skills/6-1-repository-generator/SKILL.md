---
name: 6-1-repository-generator
description: Implements repository ports defined in the application/domain layers to persist and retrieve aggregates, translating between domain models and storage representations without introducing domain logic.
---

# Repository Implementation (Phase 6.1)

This skill implements **repository ports** for persistence.

It transforms:

- repository interfaces (Phase 5)
- aggregates (Phase 4)

into:

- concrete persistence implementations

---

# Core Principle

Repositories are:

> the mechanism by which aggregates are **stored and retrieved**

They are the **only infrastructure component directly tied to domain aggregates**.

---

# Role in the Architecture

Repositories:

- implement **repository ports** defined in Phase 5  
- belong to the **Infrastructure Layer**  
- are responsible for **persistence only**  

They do NOT:

- define business logic  
- orchestrate workflows  
- coordinate behavior  

---

# Responsibilities

A repository implementation must:

- load aggregates  
- persist aggregates  
- query aggregates (when needed)  
- map between domain objects and storage models  
- isolate the database from the domain  

A repository must NOT:

- contain domain rules  
- enforce invariants  
- call external APIs  
- orchestrate application behavior  

---

# Inputs

This skill requires:

- aggregates (from Phase 4)  
- repository interfaces / ports (from Phase 5)  

---

# Outputs

This skill produces:

- repository implementations  
- persistence mappings  
- storage-specific configurations (optional)  

---

# Step-by-Step Implementation

## Step 1 — Identify aggregates

Each aggregate requires a repository.

Example:

- Task  
- Order  
- Execution  

---

## Step 2 — Identify repository ports

From Phase 5:

Example:

TaskRepository  
OrderRepository  

These define:

- required methods  
- contract for persistence  

---

## Step 3 — Choose persistence strategy

Examples:

- relational (PostgreSQL)  
- document (MongoDB)  
- in-memory (testing)  

This decision is **deferred and replaceable**.

---

## Step 4 — Implement repository

Example:

PostgresTaskRepository  
MongoTaskRepository  
InMemoryTaskRepository  

Each must implement the corresponding port.

---

## Step 5 — Define mapping

Repositories translate:

- domain → storage  
- storage → domain  

Example:

Domain:

Task  
- id  
- status  
- agent_id  

Database:

tasks table  
- id  
- status  
- agent_id  

Mapping is handled internally.

---

# Repository Template

Repository Interface (Phase 5):

TaskRepository  

Methods:

- save(task)  
- get_by_id(id)  
- find_by_status(status)  

---

Implementation (Phase 6):

PostgresTaskRepository  

Responsibilities:

- persist task  
- retrieve task  
- map data  

---

# Example

Aggregate:

Task  

Repository Port:

TaskRepository  

Implementation:

PostgresTaskRepository  

Methods:

- save(task)  
- get(task_id)  
- find_by_agent(agent_id)  

---

# Multiple Implementations

Repositories may have multiple implementations:

- PostgresTaskRepository  
- MongoTaskRepository  
- InMemoryTaskRepository  

This allows:

- testing  
- flexibility  
- infrastructure evolution  

---

# Folder Structure

/domain  
    /repositories  
        TaskRepository  

/infrastructure  
    /repositories  
        PostgresTaskRepository  
        MongoTaskRepository  

---

# Dependency Direction

Domain / Application define:

TaskRepository (interface)

Infrastructure implements:

PostgresTaskRepository  

Application depends on:

TaskRepository  

Infrastructure depends on:

domain + application  

---

# Rules

Repository implementations must:

- implement repository ports  
- isolate persistence  
- map data correctly  
- remain replaceable  

Repository implementations must NOT:

- contain domain logic  
- enforce invariants  
- orchestrate workflows  
- depend on application flow  

---

# Goal

Provide **concrete persistence mechanisms** for aggregates by:

- implementing repository ports  
- isolating storage concerns  
- enabling data access  

Repositories enable the system to **persist state** without leaking infrastructure details into the domain or application layers.

