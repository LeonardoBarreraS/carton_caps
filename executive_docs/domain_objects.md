# Carton Caps Conversational Assistant — Domain Objects Overview

---

## The Three Bounded Contexts

> A bounded context is a self-contained domain area with clear ownership, its own rules, and a specific responsibility in the system.

---

## BC-1 — Conversation Management

**Purpose:** Owns the entire lifecycle of a user conversation — from opening a session, to processing each message, to closing — and is the single entry point for every user interaction.

### Aggregate Root

| Entity | Classification | Role |
|--------|---------------|------|
| `ConversationSession` | Process Entity | The stateful container of a multi-turn conversation — enforces the full session state machine (`created → initializing → idle ⇄ active → closed`), tracks turn count, and sequences all turn execution. |

### Entities

| Entity | Classification | Role |
|--------|---------------|------|
| `ConversationHistory` | Immutable Historical Entity | Append-only log of all messages exchanged, stored per user. Loaded at session start to restore prior context. Never mutated after creation. |
| `PurchaseHistory` | Entity | Record of products previously purchased by the user. Loaded at session init as an optional context enrichment signal — empty in current dataset, designed for future use. |

### Value Objects

| Value Object | Classification | Role |
|-------------|---------------|------|
| `User` | External Reference | Immutable identity reference for the interacting user. Pre-resolved by the external auth API before any request reaches this service. Never authenticated or mutated here. |
| `School` | External Reference | Immutable reference to the school the user supports. Loaded from DB at session init. Passed to BC-2 as a `SchoolAnchor` for context pre-seeding. Never mutated here. |
| `Intent` | Value Object | The classified purpose of a user message. Drives routing through the turn pipeline. Values: `product_inquiry`, `referral_question`, `general_question`, `clarification_response`, `ambiguous`, `out_of_scope`. |
| `AssistantResponse` | Value Object | The grounded response returned to the caller. Always backed by retrieved evidence. Carries `groundedness_score` (claim traceability) and `relevance_score` (intent alignment via reverse-question technique). A response failing either threshold is never returned — a safe fallback is delivered instead. |

### Domain Events

| Event | Emitted When |
|-------|-------------|
| `SessionStarted` | Session transitions from `initializing` to `idle` |
| `TurnProcessed` | Session transitions from `active` to `idle` after a successful turn |
| `SessionClosed` | Session transitions to `closed` |

### Use Cases

| Use Case | Module | Objective |
|----------|--------|-----------|
| `StartSessionUseCase` | `application/use_cases/start_session_use_case.py` | Creates and fully initializes a `ConversationSession`. Enforces the one-session-per-user constraint. Loads user profile, school, conversation history, and purchase history from the DB. Pre-seeds `DecisionContext` in BC-2 before the first turn. |
| `ProcessTurnUseCase` | `application/use_cases/process_turn_use_case.py` | Entry point for every conversation turn. Runs `TurnGraph` (LangGraph): classifies intent → routes to Decision Intelligence → generates a grounded response → evaluates quality → persists the turn or returns a safe fallback. |
| `CloseSessionUseCase` | `application/use_cases/close_session_use_case.py` | Transitions a `ConversationSession` to the `closed` terminal state. Enforces that only `idle` sessions can be closed. |

### Execution Engine — `TurnGraph`

`ProcessTurnUseCase` runs a LangGraph graph (`TurnGraph`) as the per-turn pipeline. Key routing rules:

- `out_of_scope` / `general_question` → `generate_redirect` node (DI and retrieval bypassed entirely)
- `ambiguous` → `generate_clarification` node
- `product_inquiry` / `referral_question` / `clarification_response` → `process_decision_intelligence` → `generate_response` → `evaluate_response`
- Quality failure (`groundedness_score` or `relevance_score` below threshold) → `generate_redirect` with `redirect_reason='low_quality'`
- All paths converge at `persist_turn` → `END`

### Output
A grounded `AssistantResponse` — the final text the user receives, carrying `groundedness_score`, `relevance_score`, `context_recall_score`, `context_precision_score`, and `is_fallback`.

---

## BC-2 — Decision Intelligence

**Purpose:** Accumulates what the system knows about the user across every turn and uses that growing understanding to construct precise search queries — never searching with raw messages, always searching with enriched context.

### Aggregate Root

| Entity | Classification | Role |
|--------|---------------|------|
| `DecisionContext` | Process Entity | The core intelligence asset. Progressively accumulates user preference signals across turns (`empty → partial → ready → enriched`). Signals are strictly monotonic — never removed. School anchor always present. State drives retrieval readiness. Holds `_pending_retrieval_intent` to resume retrieval after a clarification gap is resolved. |

### Entities

| Entity | Classification | Role |
|--------|---------------|------|
| `RetrievalQuery` | Immutable Historical Artifact | Context-enriched query constructed from `DecisionContext` + `Intent`. Created once via factory `from_context()`; never mutated. Routes retrieval to `product_catalog` or `referral_program_rules` based on intent. Must never be built from the raw user message (INV-RQ-1). |

### Value Objects

| Value Object | Classification | Role |
|-------------|---------------|------|
| `PreferenceSignal` | Value Object | A single preference or constraint extracted from one conversation turn (e.g., `kids=picky`, `preference=healthy`). Immutable once created. |
| `SchoolAnchor` | Value Object | The school identity pre-seeded into `DecisionContext` at session init. The fundraising anchor — always present, never changes during the session. |
| `RetrievedEvidence` | Value Object | The result of a retrieval execution received from BC-3. Carries retrieved content chunks plus `context_recall_score` and `context_precision_score` evaluated before evidence is injected into generation. If `context_recall_score` falls below threshold, retrieval is retried before proceeding. |

### Domain Events

| Event | Emitted When |
|-------|-------------|
| `ContextUpdated` | A new `PreferenceSignal` is added and context state changes |
| `GapDetected` | Gap evaluation finds the context insufficient for recommendation; surfaces to BC-1 as `clarification_needed=True` in the DTO — never as a cross-context event |
| `ContextReady` | `DecisionContext` transitions to `ready` state for the first time |

### Use Cases

| Use Case | Module | Objective |
|----------|--------|-----------|
| `PreSeedContextUseCase` | `application/use_cases/pre_seed_context_use_case.py` | Creates a `DecisionContext` pre-seeded with the `SchoolAnchor` and any available purchase signals. Called once per session during initialization — before any turn. |
| `ProcessTurnIntelligenceUseCase` | `application/use_cases/process_turn_intelligence_use_case.py` | Runs `DecisionIntelligenceSubgraph` (LangGraph): extract signals → update `DecisionContext` → evaluate readiness → construct `RetrievalQuery` → execute retrieval via BC-3 → evaluate evidence quality (with retry on low recall). Returns `TurnIntelligenceResult`. |

### Execution Engine — `DecisionIntelligenceSubgraph`

`ProcessTurnIntelligenceUseCase` runs a LangGraph subgraph. Key routing rules:

- Gap detected AND intent doesn't require retrieval → `clarification_needed=True`, retrieval skipped
- `intent.requires_retrieval()` AND `context.is_ready_for_retrieval()` → `construct_retrieval_query` → `execute_retrieval` → `evaluate_evidence_quality`
- `context_recall_score` below threshold → refine query and retry retrieval (INV-RE-3)
- `general_question` / `clarification_response` → retrieval skipped entirely

### Output
A `TurnIntelligenceResult` — containing `evidence_chunks`, `evidence_type`, `context_recall_score`, `context_precision_score`, `context_state`, `clarification_needed`, `clarification_question`, and `school_name` (forwarded for LLM personalization in BC-1).

---

## BC-3 — Knowledge Retrieval

**Purpose:** Holds the system's verified knowledge sources — the product catalog and referral program rules — and executes semantic search against them, returning only real, retrieved content and never inventing answers.

> No aggregates. `Product` and `ReferralRule` are read-only external reference value objects retrieved by semantic similarity. They are never created, mutated, or owned by this bounded context.

### Value Objects

| Value Object | Classification | Role |
|-------------|---------------|------|
| `Product` | External Reference Value Object | An item from the platform's catalog — retrieved by semantic relevance from the `product_catalog` vector store. Never invented by the LLM. Carries: `product_id`, `name`, `category`, `brand`, `description`, `attributes`. |
| `ReferralRule` | External Reference Value Object | A platform-defined referral rule — retrieved by semantic relevance from the `referral_program_rules` vector store. Never rewritten. Carries: `rule_id`, `title`, `description`, `rule_type` (`eligibility`, `bonus`, `invitation`, `requirement`). |

### Use Cases

| Use Case | Module | Objective |
|----------|--------|-----------|
| `ExecuteRetrievalUseCase` | `application/use_cases/execute_retrieval_use_case.py` | Routes a retrieval query to the correct knowledge store based on `source_target`. Returns raw retrieved content as `RetrievedEvidenceDTO`. Never invents or rewrites content. Leaf use case — no outbound dependencies. |

### Output
`RetrievedEvidenceDTO` — the top-matching product items or referral rules returned to BC-2, which evaluates their quality (recall + precision scores) before injecting them into response generation.

---

## How the Three Contexts Connect

```
User Message
    │
    ▼
BC-1  Conversation Management
      Classifies intent · manages session · delivers final response
    │
    │  classified Intent + message (TurnInputDTO)
    ▼
BC-2  Decision Intelligence
      Extracts signals · accumulates context · detects gaps · builds enriched RetrievalQuery
    │
    │  RetrievalQueryDTO (context-enriched — never raw message)
    ▼
BC-3  Knowledge Retrieval
      Searches product_catalog or referral_program_rules · returns verified content
    │
    │  RetrievedEvidenceDTO
    ▼
BC-2  Evaluates evidence quality (recall + precision scores)
    │
    │  TurnIntelligenceResultDTO (evidence_chunks + scores + context_state)
    ▼
BC-1  Generates grounded AssistantResponse · evaluates groundedness + relevance · returns to caller
```

### Cross-Context Communication

All cross-context calls are **synchronous**, cross via **port interfaces**, and use **plain DTOs** — no domain objects from one context are ever passed into another.

| Communication | Port | Defined In | Adapter (shell) |
|---------------|------|------------|-----------------|
| BC-1 → BC-2 | `IDecisionIntelligenceService` | `src/conversation_management/application/ports/` | `DecisionIntelligenceAdapter` |
| BC-2 → BC-3 | `IKnowledgeRetrievalService` | `src/decision_intelligence/application/ports/` | `KnowledgeRetrievalAdapter` |

Both adapters live in `src/shell/composition/adapters/` — the only place in the codebase permitted to import across component boundaries.

### Key Invariants Across All Contexts

| Invariant | Rule |
|-----------|------|
| INV-RQ-1 | A `RetrievalQuery` must always be built from `intent + accumulated DecisionContext` — never from the raw user message |
| INV-AR-1 | Every response must be grounded in retrieved evidence — pure LLM responses without retrieval are not permitted |
| INV-AR-2 | Product recommendations must cite only products returned by retrieval |
| INV-AR-3 | Referral guidance must be derived exclusively from retrieved referral rules |
| INV-DC-3 | `DecisionContext` state never regresses — once `ready`, it never returns to `partial` or `empty` |
| INV-DC-5 | Preference signals accumulate monotonically — once added, a signal is never removed |
| INV-WF-1 | Intent must be classified **before** `DecisionContext` is updated on every turn |
| INV-WF-4 | Decision Intelligence (WF1) must execute on every turn — it cannot be skipped or bypassed |
