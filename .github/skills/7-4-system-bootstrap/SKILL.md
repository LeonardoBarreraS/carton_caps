---
name: 7-4-system-bootstrap
description: Initializes and starts the system by loading the composition root, registering entry points, configuring interfaces, and activating the runtime environment without introducing business logic or dependency wiring.
---

# System Bootstrap (Phase 7.4)

This skill turns the system into a **running application**.

It transforms:

- a fully wired system (Phase 7.1–7.3)

into:

- an executable runtime

---

# Core Principle

System bootstrap answers:

> "How does the system start and run?"

It does NOT define:

- business logic  
- workflows  
- dependency wiring  
- domain behavior  

It only:

> activates the system

---

# Role in the Architecture

System bootstrap:

- belongs to the **Shell Layer**  
- is the **final step of system assembly**  
- initializes runtime and interfaces  

It is responsible for:

> transitioning from static structure → running system

---

# Responsibilities

System bootstrap must:

- load the composition root  
- initialize the application container  
- register system entry points  
- attach routes or interfaces  
- start runtime (server, CLI, worker)  
- activate messaging (if present)  

System bootstrap must NOT:

- instantiate dependencies (handled in Phase 7.1)  
- define business logic  
- orchestrate workflows  
- modify domain behavior  

---

# Inputs

This skill requires:

- composition root (Phase 7.1)  
- system entry points (Phase 7.2)  
- context wiring (Phase 7.3)  

---

# Outputs

This skill produces:

- application bootstrap module  
- runtime initialization logic  
- system entry point (main function)  

---

# Step-by-Step Bootstrap

## Step 1 — Load composition root

Example:

container = create_container()  

---

## Step 2 — Resolve entry points

Example:

create_order_handler = container.resolve(CreateOrderHandler)  

---

## Step 3 — Register interfaces

Example:

- register HTTP routes  
- register CLI commands  
- register event consumers  

---

## Step 4 — Attach handlers

Example:

POST /orders → create_order_handler  

---

## Step 5 — Start runtime

Examples:

- start web server  
- start CLI loop  
- start worker process  

---

## Step 6 — Activate messaging (if present)

Example:

event_bus.start()  

---

# Bootstrap Template

bootstrap():

1. load container  
2. resolve handlers  
3. register interfaces  
4. attach routes  
5. start runtime  

---

# Example — Web Application

app = WebApp()  

app.register(  
    "/orders",  
    create_order_handler  
)  

app.start()  

---

# Example — CLI Application

cli.register(  
    "create-order",  
    create_order_handler  
)  

cli.start()  

---

# Example — Event-Based System

event_bus.subscribe(  
    TaskAssigned,  
    notify_handler  
)  

event_bus.start()  

---

# Folder Structure

/shell  
    /bootstrap  
        main.py  

---

# Dependency Direction

Bootstrap depends on:

- composition root  
- entry points  
- runtime framework  

It does NOT affect:

- application logic  
- domain logic  

---

# Rules

System bootstrap must:

- initialize the system  
- register entry points  
- connect interfaces  
- start runtime  

System bootstrap must NOT:

- wire dependencies  
- contain domain logic  
- orchestrate workflows  
- implement business rules  

---

# Goal

Activate the system by:

- loading the composed architecture  
- exposing entry points  
- starting runtime execution  

System bootstrap turns a **fully assembled architecture** into a **live, executable system**.

