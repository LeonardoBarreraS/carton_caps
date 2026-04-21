---
name: 6-3-messaging-adapter
description: Implements messaging and event-based communication ports defined in the application layer, enabling asynchronous processing and decoupled interactions without imposing event-driven architecture as a default.
---

# Messaging Adapter (Phase 6.3)

This skill generates infrastructure adapters for **messaging and event-based communication**.

It transforms:

- messaging/event ports (Phase 5)

into:

- concrete messaging implementations

---

# Core Principle

Messaging adapters are:

> mechanisms to transport messages or events between system components

They enable:

- asynchronous execution  
- decoupled communication  
- cross-process interaction  

But they are:

> an implementation choice, not a default architectural requirement

---

# Role in the Architecture

Messaging adapters:

- implement **ports defined in Phase 5**  
- belong to the **Infrastructure Layer**  
- handle **message transport and dispatch**  

They do NOT:

- define workflows  
- orchestrate behavior  
- enforce domain rules  

---

# Responsibilities

Messaging adapters must:

- publish messages/events  
- subscribe to messages/events  
- route messages to handlers  
- manage delivery mechanisms  
- serialize and deserialize data  
- handle transport protocols  

Messaging adapters must NOT:

- contain domain logic  
- enforce invariants  
- orchestrate workflows  
- define business behavior  

---

# Inputs

This skill requires:

- messaging/event ports from Phase 5  

Examples:

- EventPublisher  
- EventSubscriber  
- MessageBus  
- NotificationChannel  

---

# Outputs

This skill produces:

- messaging adapters  
- event bus implementations  
- message routing configurations  
- transport integrations  

---

# Messaging Patterns

This skill supports:

## Publish / Subscribe

- publish event  
- multiple subscribers receive  

Example:

TaskAssigned → NotifyHandler, MetricsHandler  

---

## Queue-based Messaging

- message sent to queue  
- consumer processes it  

Example:

ProcessTaskQueue  

---

## Event Streaming

- continuous event flow  
- streaming platforms  

Example:

Kafka streams  

---

# Step-by-Step Generation

## Step 1 — Identify messaging ports

From Phase 5:

Example:

- EventPublisher  
- MessageBus  

---

## Step 2 — Define adapter implementation

Examples:

- InMemoryEventBus  
- KafkaEventBus  
- RabbitMQAdapter  

---

## Step 3 — Define responsibilities

Adapter must:

- send messages  
- receive messages  
- route to handlers  
- manage subscriptions  

---

## Step 4 — Define data handling

Adapters must:

- serialize messages  
- deserialize incoming data  
- ensure compatibility  

---

# Messaging Adapter Template

Port (Phase 5):

EventPublisher  

Methods:

- publish(event)  

---

Adapter (Phase 6):

KafkaEventBus  

Responsibilities:

- publish event to Kafka  
- route to subscribers  
- manage topics  

---

# Example

Port:

MessageBus  

Adapter:

RabbitMQAdapter  

Methods:

- publish(message)  
- subscribe(handler)  

Responsibilities:

- send message to queue  
- deliver to consumer  
- manage acknowledgments  

---

# Multiple Implementations

Messaging adapters may include:

- InMemoryEventBus (testing)  
- KafkaEventBus (streaming)  
- RabbitMQAdapter (queue-based)  

This allows:

- flexibility  
- scalability  
- environment-specific configurations  

---

# Folder Structure

/infrastructure  
    /messaging  
        KafkaEventBus  
        RabbitMQAdapter  
        InMemoryEventBus  

---

# Dependency Direction

Application defines:

- messaging ports  

Infrastructure implements:

- messaging adapters  

Application depends on:

- ports only  

Infrastructure depends on:

- messaging systems  
- brokers  
- protocols  

---

# Rules

Messaging adapters must:

- implement messaging ports  
- handle transport  
- manage routing  
- remain replaceable  

Messaging adapters must NOT:

- contain domain logic  
- orchestrate workflows  
- define coordination logic  
- enforce invariants  

---

# Goal

Provide **message transport mechanisms** by:

- implementing messaging ports  
- enabling asynchronous communication  
- decoupling system components  

Messaging adapters allow the system to **communicate across boundaries and time** while preserving the purity of the application and domain layers.

