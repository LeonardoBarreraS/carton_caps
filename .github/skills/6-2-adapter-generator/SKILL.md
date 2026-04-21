---
name: 6-2-adapter-generator
description: Implements non-persistence application ports by generating infrastructure adapters that connect the system to external services (APIs, AI, storage, auth, etc.), translating between domain/application models and technical protocols.
---

# Adapter Generator (Phase 6.2)

This skill generates **infrastructure adapters** that implement **non-persistence ports**.

It transforms:

- application ports (Phase 5)

into:

- concrete integrations with external systems

---

# Core Principle

Adapters are:

> translators between the system and the external world

They convert:

- domain/application requests → external protocols  
- external responses → domain/application data  

---

# Scope Definition (Critical)

This skill implements:

- external service integrations  
- technical connectors  
- IO-based services  

This skill does NOT include:

- repositories (handled in Phase 6.1)  
- system orchestration  
- business logic  

---

# Role in the Architecture

Adapters:

- implement **ports defined in Phase 5**  
- belong to the **Infrastructure Layer**  
- execute **technical side effects**  

They are driven by:

> what the application needs (ports), not by technology choices

---

# Responsibilities

Adapters must:

- implement application ports  
- call external systems  
- handle IO operations  
- translate data formats  
- manage protocol details  
- return results in domain-friendly structures  

Adapters must NOT:

- contain domain logic  
- enforce invariants  
- orchestrate workflows  
- coordinate use cases  

---

# Inputs

This skill requires:

- ports defined in Phase 5 (use cases)  

Examples:

- NotificationService  
- LLMService  
- PaymentGateway  
- FileStorage  
- AuthProvider  

---

# Outputs

This skill produces:

- adapter implementations  
- external service clients  
- data translation layers  

---

# Adapter Categories

This skill may generate adapters for:

## External APIs

- Payment gateways (StripeAdapter)  
- Email services (SendgridAdapter)  
- Third-party integrations  

---

## AI Services

- LLM adapters (OpenAIAdapter)  
- Embedding services  
- Model inference clients  

---

## Storage (non-repository)

- file storage (S3Adapter)  
- blob storage  
- document storage APIs  

---

## Authentication

- OAuth providers  
- JWT services  
- Identity providers  

---

## Cache

- RedisAdapter  
- memory cache  

---

# Step-by-Step Generation

## Step 1 — Identify ports

From Phase 5:

Example:

- NotificationService  
- LLMService  
- PaymentGateway  

---

## Step 2 — Define adapter implementation

Example:

- EmailNotificationAdapter  
- OpenAIAdapter  
- StripePaymentAdapter  

Each adapter must implement its port.

---

## Step 3 — Define responsibilities

Adapter must:

- send requests to external system  
- handle responses  
- manage errors  
- transform data  

---

## Step 4 — Define data translation

Adapters translate:

- domain objects → external format  
- external response → domain-friendly structure  

---

# Adapter Template

Port (Phase 5):

NotificationService  

Methods:

- send_notification(message)  

---

Adapter (Phase 6):

EmailNotificationAdapter  

Responsibilities:

- connect to email provider  
- send message  
- handle response  

---

# Example

Port:

LLMService  

Adapter:

OpenAIAdapter  

Methods:

- generate(prompt)  
- analyze(input)  

Responsibilities:

- call OpenAI API  
- process response  
- return structured output  

---

# Multiple Implementations

Adapters may have multiple implementations:

- OpenAIAdapter  
- AzureOpenAIAdapter  
- LocalModelAdapter  

This allows:

- flexibility  
- vendor independence  
- experimentation  

---

# Folder Structure

/infrastructure  
    /adapters  
        /api  
        /ai  
        /auth  
        /storage  
        /cache  

---

# Dependency Direction

Application defines:

- ports  

Infrastructure implements:

- adapters  

Application depends on:

- ports only  

Infrastructure depends on:

- external libraries  
- APIs  
- SDKs  

---

# Rules

Adapters must:

- implement ports  
- isolate external systems  
- handle IO  
- translate data  

Adapters must NOT:

- contain domain logic  
- orchestrate workflows  
- depend on use case logic  
- mutate domain incorrectly  

---

# Goal

Provide **technical implementations** for external interactions by:

- implementing application ports  
- connecting to external systems  
- translating between domain and technical formats  

Adapters enable the system to **interact with reality** while keeping the application and domain layers pure and independent.

