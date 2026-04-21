---
name: 7-1-dependency-wiring
description: Builds the composition root by instantiating and connecting application and infrastructure components, creating the object graph required for system execution without introducing business logic or runtime concerns.
---

# Dependency Wiring (Phase 7.1)

This skill creates the **composition root** of the system.

It transforms:

- use cases (Phase 5)
- ports (Phase 5)
- infrastructure implementations (Phase 6)

into:

- a fully connected object graph

---

# Core Principle

Dependency wiring answers:

> "How are all components instantiated and connected?"

It does NOT define:

- system behavior  
- workflows  
- domain rules  
- runtime execution  

It only **assembles the system**.

---

# Role in the Architecture

Dependency wiring:

- belongs to the **Shell Layer**  
- is the **single place where dependencies are instantiated**  
- connects application with infrastructure  

It is the bridge between:

abstract design → concrete system

---

# Responsibilities

Dependency wiring must:

- instantiate infrastructure implementations  
- inject dependencies into use cases  
- wire coordinators  
- connect ports to implementations  
- build the object graph  

Dependency wiring must NOT:

- define business logic  
- orchestrate workflows  
- handle external input  
- start the system runtime  

---

# Inputs

This skill requires:

- use cases (Phase 5.1)  
- coordinators (Phase 5.3)  
- repository implementations (Phase 6.1)  
- adapters (Phase 6.2)  
- messaging adapters (Phase 6.3, if present)  

---

# Outputs

This skill produces:

- instantiated repositories  
- instantiated adapters  
- wired use cases  
- wired coordinators  
- composition root (container / bootstrap module)  

---

# Step-by-Step Wiring

## Step 1 — Identify use cases

Example:

- CreateOrderUseCase  
- AssignTaskUseCase  

---

## Step 2 — Identify required ports

From use cases:

- OrderRepository  
- NotificationService  
- LLMService  

---

## Step 3 — Map ports to implementations

Example:

- OrderRepository → PostgresOrderRepository  
- NotificationService → EmailNotificationAdapter  
- LLMService → OpenAIAdapter  

---

## Step 4 — Instantiate implementations

Example:

order_repository = PostgresOrderRepository()  
notification_service = EmailNotificationAdapter()  
llm_service = OpenAIAdapter()  

---

## Step 5 — Wire use cases

Example:

create_order_use_case = CreateOrderUseCase(  
    order_repository,  
    notification_service  
)  

---

## Step 6 — Wire coordinators (if present)

Example:

process_order_coordinator = ProcessOrderCoordinator(  
    create_order_use_case,  
    process_payment_use_case  
)  

---

# Composition Root

The composition root is:

the single place where the system is assembled

Examples:

- main.py  
- bootstrap.py  
- container.py  

---

# Wiring Patterns

## Manual Wiring

repo = PostgresRepository()  
use_case = UseCase(repo)  

---

## Factory Wiring

def create_use_case():  
    return UseCase(repo)  

---

## Container Wiring (Dependency Injection)

container.register(  
    OrderRepository,  
    PostgresOrderRepository  
)  

---

# Folder Structure

/shell  
    /composition  
    /container  
    bootstrap.py  

---

# Dependency Direction

Shell (wiring)  
↓  
Application (use cases)  
↓  
Domain  
↑  
Infrastructure (implementations)  

- Application depends on ports  
- Infrastructure implements ports  
- Shell connects both  

---

# Rules

Dependency wiring must:

- be centralized (single composition root)  
- instantiate concrete implementations  
- inject dependencies explicitly  
- remain simple and explicit  

Dependency wiring must NOT:

- contain domain logic  
- orchestrate behavior  
- define workflows  
- depend on frameworks unnecessarily  

---

# Goal

Create a **fully assembled system graph** by:

- connecting application and infrastructure  
- resolving all dependencies  
- preparing the system for execution  

Dependency wiring turns the architecture into a **connected system**, ready to be exposed and executed in the next steps.

