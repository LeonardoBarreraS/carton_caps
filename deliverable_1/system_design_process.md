# Software Development Process — Carton Caps Conversational Assistant

---

## The Foundation: Three Layers Before Any Code

Every decision in this system was made in a deliberate order across three layers, each one building on the previous:

| Layer | What it defines |
|-------|----------------|
| **1. Domain Layer** | The business rules, entities, invariants, and language of the problem — independent of any technology |
| **2. Architecture Layer** | How the domain is structured into components, boundaries, and communication contracts |
| **3. AI Execution Layer** | How language models, vector search, and pipelines are wired to fulfil the domain's contracts |

> **Why this order matters:** Technology changes. Business rules don't. Building the domain first ensures that swapping an LLM, a database, or a vector store never touches the core logic of the system.

---

## The Seven Phases

### Phase 0 — Problem Understanding
Define what the system actually is, who uses it, and what success looks like. Capture the business case, the user persona, and the fundraising goal before any technical decision is made.

### Phase 1 — Requirements
Translate the problem into structured functional requirements and behavioral workflows. Define what the system must do — not how. Establish the observable behaviors and the actors involved.

### Phase 2 — Domain Modeling
Extract the real-world concepts the system works with: entities, value objects, process entities, and invariants. Define the rules that must never be broken, regardless of what surrounds the system.

### Phase 3 — Domain Architecture
Identify the bounded contexts — the semantic boundaries where concepts have clear ownership. Map each context to an architectural component. Define how contexts communicate without leaking internals.

### Phase 4 — Domain Layer Materialization
Generate the concrete domain model: aggregate roots, state machines, domain events, and lifecycle transitions. This is the constitution of the system — pure logic with no infrastructure.

### Phase 5 — Application Layer Design
Design the use cases that orchestrate domain behavior. Define the ports (interfaces) the system needs to talk to the outside world, without knowing what fulfils them. Wire LangGraph execution graphs for the two complex pipelines.

### Phase 6 — Infrastructure Layer Design
Build the concrete adapters that fulfil the ports: OpenAI classifiers, Qdrant semantic search, SQLite repositories, response evaluators, and the ingestion pipeline. Connect the system to the real world without touching domain logic.

### Phase 7 — Shell Composition
Wire every component into a single, runnable application. The shell is the only place that knows all components simultaneously. It holds zero business logic — it only connects.

---

## The Ultimate Goal

Software that can evolve.

Each phase adds a layer of structure that protects everything below it. New AI models, different databases, new conversation flows — any of these can be swapped or extended without rewriting the system. The domain stays stable. The architecture stays clean. The AI execution layer stays replaceable.

That is the discipline this process enforces: **build what the problem demands, in the order that makes it last.**
