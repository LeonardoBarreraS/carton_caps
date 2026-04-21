# Phase 7 — Shell / Composition Layer: Summary
## Carton Caps Conversational Assistant

---

## Part I — For Non-Technical Readers

### What problem were we solving?

By the end of Phase 6, the system had everything it needed to *think*: a domain model that owned all the business rules, an application layer that orchestrated every conversation workflow, and a full set of infrastructure adapters that connected to OpenAI, Qdrant, and SQLite. Every component was built, tested, and waiting.

But none of them knew about each other.

The intent classifier did not know which response generator to hand results to. The decision intelligence engine did not know which knowledge retrieval service to call. The database sessions had no connection to the conversation sessions. Every component was a standalone island.

Phase 7 solved this problem. Its one and only job was to **connect every island into a single, working system** — and then expose that system to the world through a clean, well-guarded front door.

---

### Why is this step needed at all?

In well-designed software, the individual components deliberately do not know about each other. A component that knows too much about its neighbours becomes fragile — change one thing and everything breaks. This careful separation is what made phases 1 through 6 productive: each piece could be designed and built independently, with no risk of tangled dependencies.

But a system that is entirely separated is a system that does nothing. At some point, someone has to decide: *these two pieces go together, this port connects to that adapter, this boundary is crossed here and not there.* That decision-making point is the shell, and Phase 7 was entirely focused on getting it right.

The shell layer has three strict rules:
1. It is the **only** place in the codebase that is allowed to reach across the three bounded contexts simultaneously.
2. It contains **zero business logic** — the shell wires things together, it does not decide anything.
3. Once wired, the system behaves exactly as the domain and application layers specified — the shell adds nothing and removes nothing.

---

### What were the three tasks of Phase 7?

---

#### Task 1 — Dependency Wiring: Assembling the Object Graph

Think of this as plugging every cable into the right socket before turning on a device. Dependency wiring is the act of taking every component — the AI classifiers, the database connections, the response generators, the cross-context bridges — and declaring exactly which instance of each feeds into which use case.

The entire object graph is wired in a single function: `build_container()`. This function runs once when the server starts. Every AI adapter, every repository, every cross-context bridge, every use case — all of them are created and connected here, in a precise order that respects which pieces depend on which other pieces.

The output of this function is an `AppContainer` — a sealed object that holds exactly three things: the `StartSession`, `ProcessTurn`, and `CloseSession` use cases, each fully wired with every dependency they need to do their job. The rest of the system never needs to know how they were assembled.

**Fifteen wiring decisions were recorded**, covering:
- Every infrastructure adapter (AI, database, vector store)
- Both in-memory stores (session state and decision context)
- The single shared OpenAI connection (one connection, shared by all five AI adapters)
- The single shared event publisher (one instance, used by all four use cases that raise domain events)
- Both cross-context bridges (Decision Intelligence ↔ Conversation Management, Knowledge Retrieval ↔ Decision Intelligence)

**One known wiring gap was also documented (GAP-1):** the RAG metrics logger was already implemented in Phase 6 but had not yet been connected to the `ProcessTurnUseCase`. This gap was identified, recorded formally, and resolved — it is now wired.

---

#### Task 2 — System Composition: Bootstrapping the Application

If dependency wiring is plugging in the cables, system composition is pressing the power button in the right order.

`create_app()` is the function that builds the runnable FastAPI application. It calls `build_container()` to get the fully-wired use cases, registers all three API routes, and attaches nine exception handlers — one for every known error condition that the domain can raise. When the server starts, this sequence runs exactly once and the application is ready to serve requests.

The API has three endpoints:

| Endpoint | What it does |
|---|---|
| `POST /sessions` | A user opens a conversation. The system loads their profile, identifies their school, reads their purchase history, and seeds the AI reasoning engine — all before returning the session identifier. |
| `POST /sessions/{id}/turns` | The user sends a message. The full AI pipeline runs: intent classification, preference signal extraction, context evaluation, semantic retrieval if warranted, response generation, quality scoring, and history persistence. The response arrives with quality scores attached. |
| `DELETE /sessions/{id}` | The user or application closes the session cleanly. The system validates that the session is in the right state before closing it. |

Nine error conditions were mapped to precise HTTP responses. Every domain error — a session not found, a user not authorized, a session in the wrong state — produces a structured error envelope with a human-readable error code. No raw exceptions reach the client.

---

#### Task 3 — Context Wiring: Connecting the Bounded Contexts

The system is divided into three bounded contexts — three separate domains of responsibility that are designed to know nothing about each other's internals. Conversation Management owns the session and the conversation. Decision Intelligence owns the reasoning engine and preference signals. Knowledge Retrieval owns the vector search over products and referral rules.

These three contexts must communicate. But they must do so through controlled channels, carrying only the minimum data needed, never leaking internal domain objects across boundaries.

Context wiring established those controlled channels. Two bridges were built and registered:

**Bridge 1 — Conversation Management → Decision Intelligence:** When a session starts, Conversation Management tells Decision Intelligence to create and seed a decision context with the user's school and purchase history. On every turn, it passes the classified intent and message, and receives back evidence chunks, quality scores, and any clarification signal. The conversation manager never touches any Decision Intelligence domain object directly.

**Bridge 2 — Decision Intelligence → Knowledge Retrieval:** When Decision Intelligence has built up enough context about what the user wants, it asks Knowledge Retrieval to search for relevant products or referral rules. It passes a query text and a source target; it receives back content chunks. Decision Intelligence never touches Qdrant or any Knowledge Retrieval domain object directly.

Both bridges live exclusively in the shell layer, which is the only place permitted to see both sides.

One important architectural decision was documented here: the system uses **direct synchronous calls** instead of the event-subscription pattern that some architectural frameworks recommend for cross-context communication. This was a deliberate and justified choice — the RAG pipeline must execute step by step, and each step must complete before the next can begin. Asynchronous event routing would add complexity with no benefit.

---

### What does the completed system look like from start to finish?

Once Phase 7 was complete, the entire system could be started with a single command:

```
uvicorn main:app --host 0.0.0.0 --port 8000
```

And the life of one complete conversation turn looks like this:

1. **Client** sends `POST /sessions/{id}/turns` with a user message.
2. **FastAPI** validates the request shape.
3. **Router** calls `ProcessTurnUseCase.execute()` with a typed command.
4. **Use case** confirms the session exists, belongs to the right user, and is idle.
5. **TurnGraph** runs: intent is classified by OpenAI.
6. **Decision Intelligence** evaluates whether enough context exists; if not, it asks a clarifying question.
7. **Knowledge Retrieval** searches Qdrant for the top-matching products or referral rules.
8. **Response Generator** produces a grounded response citing only retrieved evidence.
9. **Response Evaluator** scores groundedness and relevance. If scores are below threshold, a safe fallback is returned instead.
10. **History** is written: user message and assistant response both persisted to SQLite.
11. **RAG metrics** are written: all quality scores for this turn saved to `rag_metrics.sqlite`.
12. **Domain events** are drained and written to `domain_events.log`.
13. **HTTP 200** is returned with the full response envelope.

From the user's perspective: they sent a question and received a grounded, school-specific, evidence-backed answer.

---

### What is the system's quality and observability story?

The system does not just respond — it measures its own quality on every turn.

Every conversation turn writes a metrics record containing: how many evidence chunks were retrieved, how well the retrieved evidence covered the question, how well the generated response was grounded in that evidence, how accurately the response answered the question, whether the response passed the quality gate or fell back to a safe answer, and whether a clarification question was asked.

Domain events provide an additional audit trail: every session open, turn completion, session close, new preference signal detected, context gap identified, and context readiness transition is recorded with a timestamp to a structured log.

None of this observability infrastructure ever interrupts a conversation — both systems are designed to fail silently rather than propagate errors into the turn pipeline.

---

### What was actually built in Phase 7?

| What | Count |
|---|---|
| Infrastructure components instantiated | 15 |
| Cross-context communication bridges | 2 |
| API endpoints exposed | 3 |
| Exception handlers registered | 9 |
| Environment configuration keys | 8 |
| Shell layer Python files | 11 |

---

---

## Part II — Technical Reference

### Layer Role and Constraints

The shell layer is the outermost composition ring of the Clean Architecture stack.

```
Shell (Phase 7)              — composition root, context wiring, API entry points
─────────────────────────────────────────────────────────────────────────────────────────
Infrastructure (Phase 6)     — adapters, repositories, event publisher
─────────────────────────────────────────────────────────────────────────────────────────
Application Layer (Phase 5)  — use cases, LangGraph workflows, ports, DTOs
─────────────────────────────────────────────────────────────────────────────────────────
Domain Layer (Phase 4)       — entities, value objects, invariants, domain events
```

**Rules that govern this layer:**
- The shell is the **only** location in the system permitted to import from multiple bounded contexts simultaneously.
- All wiring lives exclusively in `src/shell/composition/`.
- The shell contains zero domain logic — no conditionals, no business rules, no invariant checks.
- Constructor injection is used exclusively — no service locator, no global singletons, no lazy resolution.
- The object graph is assembled once at startup. No dependency is created on-demand after boot.
- No bounded context imports from `src/shell/` — the dependency direction is shell → BC, never BC → shell.

---

### Task 1 — Dependency Wiring

#### Composition Root: `build_container()`

**Location:** `src/shell/composition/container.py`

`build_container()` is the single composition root of the entire system. It reads environment configuration, instantiates every infrastructure adapter, assembles the use case graph, and returns a sealed `AppContainer`. The full wiring runs exactly once at startup.

#### Object Graph Assembly Order

The instantiation follows a strict bottom-up order to respect dependency direction. Each tier is fully constructed before the tier that depends on it:

| Step | Tier | Components instantiated |
|---|---|---|
| 1 | Configuration | Load `.env`; read 8 environment variables with defaults |
| 2 | Shared clients | `OpenAI(api_key=...)` — one instance shared by all 5 LLM adapters |
| 3 | BC-3 infrastructure | `QdrantProductRepository`, `QdrantReferralRuleRepository` |
| 4 | BC-3 use cases | `ExecuteRetrievalUseCase` |
| 5 | COMM-2 adapter | `KnowledgeRetrievalAdapter(execute_retrieval_use_case=...)` |
| 6 | BC-2 infrastructure | `InMemoryDecisionContextRepository`, `OpenAISignalExtractor`, `OpenAIEvidenceEvaluator` |
| 7 | BC-2 use cases | `PreSeedContextUseCase`, `ProcessTurnIntelligenceUseCase(..., knowledge_retrieval_service=knowledge_retrieval_adapter)` |
| 8 | COMM-1 adapter | `DecisionIntelligenceAdapter(pre_seed_use_case=..., process_turn_use_case=...)` |
| 9 | Event publisher | `LoggingEventPublisher(log_path=domain_event_log_path)` |
| 10 | BC-1 infrastructure | History repo, session repo, user repo, school repo, purchase history repo, intent classifier, response generator, response evaluator, RAG metrics logger |
| 11 | BC-1 use cases | `StartSessionUseCase`, `ProcessTurnUseCase`, `CloseSessionUseCase` |
| 12 | Return | `AppContainer(start_session=..., process_turn=..., close_session=...)` |

#### Full Wiring Registry

| ID | Port | Implementation | Bounded Context | Storage | Injected Into |
|---|---|---|---|---|---|
| WIRE-1 | `IConversationSessionRepository` | `InMemoryConversationSessionRepository` | BC-1 | Python dict | `StartSessionUseCase`, `ProcessTurnUseCase`, `CloseSessionUseCase` |
| WIRE-2 | `IConversationHistoryRepository` | `SQLiteConversationHistoryRepository` | BC-1 | SQLite `Conversation_History` | `StartSessionUseCase`, `ProcessTurnUseCase` |
| WIRE-3 | `IUserRepository` | `SQLiteUserRepository` | BC-1 | SQLite `Users` | `StartSessionUseCase` |
| WIRE-4 | `ISchoolRepository` | `SQLiteSchoolRepository` | BC-1 | SQLite `Schools`+`Users` JOIN | `StartSessionUseCase` |
| WIRE-5 | `IPurchaseHistoryRepository` | `SQLitePurchaseHistoryRepository` | BC-1 | SQLite `Purchase_History`+`Products` JOIN | `StartSessionUseCase` |
| WIRE-6 | `IIntentClassifier` | `OpenAIIntentClassifier` | BC-1 | OpenAI `gpt-4o-mini` | `ProcessTurnUseCase` via TurnGraph |
| WIRE-7 | `IResponseGenerator` | `OpenAIResponseGenerator` | BC-1 | OpenAI `gpt-4o` | `ProcessTurnUseCase` via TurnGraph |
| WIRE-8 | `IResponseEvaluator` | `OpenAIResponseEvaluator` | BC-1 | OpenAI `gpt-4o-mini` | `ProcessTurnUseCase` via TurnGraph |
| WIRE-9 | `IDecisionContextRepository` | `InMemoryDecisionContextRepository` | BC-2 | Python dict | `PreSeedContextUseCase`, `ProcessTurnIntelligenceUseCase` |
| WIRE-10 | `ISignalExtractor` | `OpenAISignalExtractor` | BC-2 | OpenAI `gpt-4o-mini` | `ProcessTurnIntelligenceUseCase` via subgraph |
| WIRE-11 | `IEvidenceEvaluator` | `OpenAIEvidenceEvaluator` | BC-2 | OpenAI `gpt-4o-mini` | `ProcessTurnIntelligenceUseCase` via subgraph |
| WIRE-12 | `IProductRepository` | `QdrantProductRepository` | BC-3 | Qdrant `product_catalog` | `ExecuteRetrievalUseCase` |
| WIRE-13 | `IReferralRuleRepository` | `QdrantReferralRuleRepository` | BC-3 | Qdrant `referral_program_rules` | `ExecuteRetrievalUseCase` |
| WIRE-14 | `IEventPublisher` (BC-1 + BC-2) | `LoggingEventPublisher` | shell | `data/domain_events.log` | All 4 use cases that emit events |
| WIRE-15 | `IRAGMetricsLogger` | `SQLiteRAGMetricsLogger` | BC-1 | `data/rag_metrics.sqlite` | `ProcessTurnUseCase` |

#### AppContainer

```python
@dataclass(frozen=True)
class AppContainer:
    start_session: StartSessionUseCase
    process_turn:  ProcessTurnUseCase
    close_session: CloseSessionUseCase
```

Frozen dataclass — immutable after construction. Holds the three public use cases that the API layer binds to route handlers. No infrastructure component is exposed beyond this container surface.

#### Configuration Keys

| Environment Variable | Default | Used By |
|---|---|---|
| `OPENAI_API_KEY` | *(required)* | OpenAI client (all 5 LLM adapters) |
| `SQLITE_DB_PATH` | `data/carton_caps_data.sqlite` | All SQLite repositories |
| `RAG_METRICS_DB_PATH` | `data/rag_metrics.sqlite` | `SQLiteRAGMetricsLogger` |
| `DOMAIN_EVENT_LOG_PATH` | `data/domain_events.log` | `LoggingEventPublisher` |
| `QDRANT_URL` | `http://localhost:6333` | `QdrantProductRepository`, `QdrantReferralRuleRepository` |
| `LLM_MODEL` | `gpt-4o-mini` | All 4 LLM adapters using mini model |
| `MIN_GROUNDEDNESS` | `0.8` | `ProcessTurnUseCase` quality gate |
| `MIN_RELEVANCE` | `0.75` | `ProcessTurnUseCase` quality gate |

**Note:** `LLM_MODEL` controls the default model used by `OpenAIIntentClassifier`, `OpenAISignalExtractor`, `OpenAIEvidenceEvaluator`, and `OpenAIResponseEvaluator`. `OpenAIResponseGenerator` is always instantiated with the same `llm_model` value — override via env var to switch all adapters from `gpt-4o-mini` to `gpt-4o` for maximum quality across all pipeline steps.

#### Wiring Rules

**Must:**
- All wiring lives exclusively in `src/shell/composition/`
- Implementations instantiated at startup — never on-demand
- Constructor injection for every dependency
- Single shared `OpenAI` client instance across all LLM adapters
- Single shared `LoggingEventPublisher` instance across all BC-1 and BC-2 use cases
- Object graph assembled in bottom-up order: BC-3 → COMM-2 → BC-2 → COMM-1 → event_publisher → BC-1

**Must not:**
- No domain logic in wiring code
- No bounded context importing from `src/shell/`
- No service locator pattern — all dependencies resolved at composition time
- No async dispatch infrastructure — the pipeline is synchronous by design
- No `event_bus.subscribe()` calls between contexts — cross-context wiring uses synchronous adapter port calls

---

### Task 2 — System Composition

#### FastAPI Application Factory: `create_app()`

**Location:** `src/shell/api/app.py`

```python
def create_app() -> FastAPI:
    app = FastAPI(title="Carton Caps Conversational Assistant")
    container = build_container()         # object graph assembled once
    app.include_router(build_router(container))
    # ... 9 exception handlers registered
    return app
```

**Startup sequence:**

```
uvicorn main:app
    ↓
main.py → app = create_app()
    ↓
build_container()         ← all 15 wirings resolved; infrastructure live
    ↓
build_router(container)   ← 3 routes registered; use cases bound to handlers
    ↓
9 exception handlers      ← domain errors mapped to HTTP status codes
    ↓
FastAPI app object returned → uvicorn begins serving
```

#### Route Handlers

**Location:** `src/shell/api/router.py`

All three handlers follow the same pattern: validate request (Pydantic), build a typed command, call `container.use_case.execute(command)`, map result to Pydantic response schema.

| ID | Method | Path | Handler | Use Case | Success Status |
|---|---|---|---|---|---|
| EP-1 | `POST` | `/sessions` | `start_session` | `StartSessionUseCase` | 201 Created |
| EP-2 | `POST` | `/sessions/{session_id}/turns` | `process_turn` | `ProcessTurnUseCase` | 200 OK |
| EP-3 | `DELETE` | `/sessions/{session_id}` | `close_session` | `CloseSessionUseCase` | 200 OK |

No business logic is present in any handler. Route handlers translate HTTP ↔ typed commands/responses exclusively.

#### Pydantic Schemas

**Location:** `src/shell/api/schemas.py`

**Request schemas:**

| Schema | Fields |
|---|---|
| `StartSessionRequest` | `user_id: str` |
| `ProcessTurnRequest` | `user_id: str`, `message: str` |
| `CloseSessionRequest` | `user_id: str` |

**Response schemas:**

| Schema | Fields |
|---|---|
| `StartSessionResponse` | `session_id: str`, `status: str` |
| `ProcessTurnResponse` | `session_id: str`, `response_text: str`, `intent: str`, `is_fallback: bool`, `groundedness_score: float`, `relevance_score: float` |
| `CloseSessionResponse` | `session_id: str`, `status: str` |
| `ErrorResponse` | `error_code: str`, `message: str` |

#### Exception Handler Registry

All handlers registered on the FastAPI `app` instance before any request is served. Route handlers contain no try/except — all error handling is centralised here. Every error response uses the `ErrorResponse` envelope.

| Exception Class | Source Module | HTTP Status | Error Code |
|---|---|---|---|
| `SessionConflictError` | `start_session_use_case` | 409 | `SESSION_CONFLICT` |
| `UserNotFoundError` | `start_session_use_case` | 404 | `USER_NOT_FOUND` |
| `SchoolNotFoundError` | `start_session_use_case` | 404 | `SCHOOL_NOT_FOUND` |
| `SessionNotFoundError` *(turn)* | `process_turn_use_case` | 404 | `SESSION_NOT_FOUND` |
| `SessionNotFoundError` *(close)* | `close_session_use_case` | 404 | `SESSION_NOT_FOUND` |
| `SessionOwnershipError` | `process_turn_use_case` | 403 | `OWNERSHIP_MISMATCH` |
| `InvalidTurnStateError` | `process_turn_use_case` | 422 | `INVALID_SESSION_STATE` |
| `AuthorizationError` | `close_session_use_case` | 403 | `AUTHORIZATION_ERROR` |
| `InvalidSessionTransitionError` | `conversation_session` (domain) | 409 | `INVALID_STATE_TRANSITION` |

**Import collision note:** Both `process_turn_use_case` and `close_session_use_case` declare a class named `SessionNotFoundError`. Both are imported with aliases (`TurnSessionNotFoundError`, `CloseSessionNotFoundError`) in `app.py` and registered as separate handlers that emit the same `SESSION_NOT_FOUND` code.

#### EP-2 — Full Turn Request/Response Trace

```
POST /sessions/{session_id}/turns
    Body: { "user_id": "...", "message": "..." }
          ↓ Pydantic validates shape
router.py
    ProcessTurnCommand(session_id=..., user_id=..., message=...)
          ↓
ProcessTurnUseCase.execute(command)                          [BC-1]
    guard: session exists + ownership + status=IDLE
    load full conversation_history from history
    session.receive_message()  →  IDLE → ACTIVE
          ↓
    TurnGraph.invoke(initial_state)
        N1 classify_intent        → OpenAI gpt-4o-mini
        N2 process_decision_intelligence
            → IDecisionIntelligenceService.process_turn(TurnInputDTO)   [COMM-1]
              DecisionIntelligenceAdapter
                ProcessTurnIntelligenceUseCase                           [BC-2]
                  DecisionIntelligenceSubgraph
                    extract_signals        → OpenAI gpt-4o-mini
                    update_decision_context
                    evaluate_context_readiness
                    construct_retrieval_query
                    execute_retrieval
                        → IKnowledgeRetrievalService.retrieve(RetrievalQueryDTO)  [COMM-2]
                          KnowledgeRetrievalAdapter
                            ExecuteRetrievalUseCase                      [BC-3]
                              Qdrant semantic search
                            ← RetrievedEvidenceDTO
                    evaluate_evidence_quality → OpenAI gpt-4o-mini
                  ← TurnIntelligenceResultDTO (evidence, scores, school_name, clarification)
        N3/N4 generate_response or generate_clarification
              → OpenAI gpt-4o
        N5 evaluate_response       → OpenAI gpt-4o-mini
        N6/N7 persist_turn or return_fallback  → SQLite
              (fallback and out_of_scope also route through persist_turn)
    session.complete_turn()  →  ACTIVE → IDLE
    session_repo.save(session)
    event_publisher.publish(events)          → domain_events.log
    rag_metrics_logger.log_turn_metrics(dto) → rag_metrics.sqlite
          ↓
ProcessTurnResponse(session_id, response_text, intent, is_fallback, groundedness, relevance)
          ↓ Pydantic serialises
HTTP 200 { "session_id": ..., "response_text": ..., "intent": ...,
           "is_fallback": ..., "groundedness_score": ..., "relevance_score": ... }
```

---

### Task 3 — Context Wiring

#### Wiring Model: Synchronous Adapter Port Calls

This system uses **synchronous direct port calls via shell adapters** for all cross-context communication. The `context-wiring` skill's default pattern (`event_bus.subscribe(Event, Handler)`) is explicitly not used.

**Rationale:**
1. The RAG pipeline is inherently sequential — evidence retrieval must complete before response generation; asynchronous routing adds latency with no behavioral benefit.
2. Domain events are observability signals — they carry no cross-context behavioral consequences and have no subscribers that act on them.
3. Subscribing events to a bus to route them to a logger that needs no bus is unjustified machinery.

This decision is recorded in `context_wiring.json` under `wiring_model.inter_context_mechanism = "synchronous_adapter_port_calls"`.

#### Bounded Context Roles

| Context | Role | Cross-Context Out | Cross-Context In |
|---|---|---|---|
| BC-1 Conversation Management | Primary driver — session lifecycle, turn orchestration, public API | COMM-1 → BC-2 | None |
| BC-2 Decision Intelligence | Reasoning engine — signal extraction, context evaluation, retrieval orchestration | COMM-2 → BC-3 | COMM-1 ← BC-1 |
| BC-3 Knowledge Retrieval | Semantic search — Qdrant queries for products and referral rules | None (leaf) | COMM-2 ← BC-2 |

#### Cross-Context Wiring

##### WIRE-CC-1 — COMM-1: BC-1 → BC-2

**Port:** `IDecisionIntelligenceService` (defined in `conversation_management/application/ports/`)  
**Adapter:** `DecisionIntelligenceAdapter` (`src/shell/composition/adapters/decision_intelligence_adapter.py`)

| Method | Called by | When | Request | Response |
|---|---|---|---|---|
| `pre_seed_context(PreSeedContextDTO)` | `StartSessionUseCase` | Once per session at initialization | `session_id`, `school_id`, `school_name`, `purchase_signals` | None |
| `process_turn(TurnInputDTO)` | `ProcessTurnUseCase` via TurnGraph | Every turn, after intent classification | `session_id`, `intent`, `message`, `turn_number`, `conversation_history` | `TurnIntelligenceResultDTO` (evidence, scores, context_state, clarification, school_name) |

##### WIRE-CC-2 — COMM-2: BC-2 → BC-3

**Port:** `IKnowledgeRetrievalService` (defined in `decision_intelligence/application/ports/`)  
**Adapter:** `KnowledgeRetrievalAdapter` (`src/shell/composition/adapters/knowledge_retrieval_adapter.py`)

| Method | Called by | When | Request | Response |
|---|---|---|---|---|
| `retrieve(RetrievalQueryDTO)` | `ProcessTurnIntelligenceUseCase` via subgraph | When context is ready/enriched and intent is `product_inquiry` or `referral_question` | `query_text`, `source_target` | `RetrievedEvidenceDTO` (chunks, evidence_type) |

**Frequency:** 0–N calls per turn. Conditional on context readiness. Includes retry cycle (up to `max_retrieval_retries=2`) when `context_recall_score < 0.6`.

#### DTO Isolation

No domain object from any bounded context crosses a boundary in either direction. All DTOs carry only primitives.

| DTO | Direction | Fields |
|---|---|---|
| `PreSeedContextDTO` | BC-1 → BC-2 | `session_id: str`, `school_id: str`, `school_name: str`, `purchase_signals: list[str]` |
| `TurnInputDTO` | BC-1 → BC-2 | `session_id: str`, `intent: str`, `message: str`, `turn_number: int`, `conversation_history: list[dict]` |
| `TurnIntelligenceResultDTO` | BC-2 → BC-1 | `evidence_chunks: list[str]`, `evidence_type: str`, scores, `context_state: str`, `clarification_needed: bool`, `clarification_question: str?`, `school_name: str` |
| `RetrievalQueryDTO` | BC-2 → BC-3 | `query_text: str`, `source_target: str` |
| `RetrievedEvidenceDTO` | BC-3 → BC-2 | `chunks: list[str]`, `evidence_type: str` |

#### Intra-Context Event Wiring

All six domain events are **observability signals only**. None crosses a context boundary. All are consumed by a single shared `LoggingEventPublisher` instance.

| Wire | Source | Events | Publisher Port | Sink |
|---|---|---|---|---|
| WIRE-EVT-1 | BC-1 aggregates — `ConversationSession` | `SessionStarted`, `TurnProcessed`, `SessionClosed` | `IEventPublisher` (BC-1) | `data/domain_events.log` |
| WIRE-EVT-2 | BC-2 aggregates — `DecisionContext` | `ContextUpdated`, `GapDetected`, `ContextReady` | `IEventPublisher` (BC-2) | `data/domain_events.log` |

`LoggingEventPublisher` satisfies both ports via Python multiple inheritance:

```python
class LoggingEventPublisher(BC1IEventPublisher, BC2IEventPublisher):
    ...
```

One constructor, one file handler, one log file. Both event streams write to the same sink.

#### Complete Context Topology

```
POST /sessions/{id}/turns
         ↓
BC-1 ConversationManagement
    TurnGraph (LangGraph WF-GRAPH-1)
    │
    ├─ COMM-1 (DecisionIntelligenceAdapter) ──────────────────┐
    │                                                        BC-2 DecisionIntelligence
    │                                                          │
    │                                                          ├─ COMM-2 (KnowledgeRetrievalAdapter) ──┐
    │                                                          │                              BC-3 KnowledgeRetrieval
    │                                                          │                              (Qdrant)
    │                                                          │  ← RetrievedEvidenceDTO ─────────────┘
    │                                                          │
    │                                                       BC-2 domain events
    │                                                       (ContextUpdated, GapDetected, ContextReady)
    │                                                          ↓ IEventPublisher (BC-2)
    │  ← TurnIntelligenceResultDTO ────────────────────────────┘  LoggingEventPublisher
    │                                                                      ↓
    │                                                             domain_events.log
    │
BC-1 domain events (SessionStarted, TurnProcessed, SessionClosed)
    ↓ IEventPublisher (BC-1)
    LoggingEventPublisher (same instance)
    ↓
domain_events.log
         ↓
HTTP 200 response
```

#### Context Wiring Rules

**Must:**
- All cross-context connections implemented as shell adapters in `src/shell/composition/adapters/`
- Port interfaces defined exclusively in the calling context's application layer
- DTOs carry only primitives — no domain objects cross context boundaries
- Same `LoggingEventPublisher` instance wired to both `IEventPublisher` ports
- Context isolation maintained: no BC module contains an import from another BC module

**Must not:**
- No BC imports from another BC
- No domain event routed across context boundaries — events terminate at the local observability sink
- No `event_bus.subscribe()` between contexts
- No async event dispatch

---

### Shell Layer File Map

```
src/shell/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── app.py                  create_app() — FastAPI factory + 9 exception handlers
│   ├── router.py               build_router(container) — 3 route handlers
│   └── schemas.py              Pydantic v2 request/response/error models
└── composition/
    ├── __init__.py
    ├── container.py            build_container() → AppContainer (composition root)
    ├── logging_event_publisher.py  LoggingEventPublisher — BC-1 + BC-2 IEventPublisher
    └── adapters/
        ├── __init__.py
        ├── decision_intelligence_adapter.py   COMM-1 — BC-1 → BC-2
        └── knowledge_retrieval_adapter.py     COMM-2 — BC-2 → BC-3

main.py                         ASGI entry point — app = create_app()
requirements.txt                Runtime dependency manifest
.env.example                    All 8 environment variable declarations with defaults
```

---

### Phase 7 Deliverables

| Artifact | Type | Purpose |
|---|---|---|
| `dependency_wiring.json` | Design document | Machine-readable full object graph specification |
| `dependency_wiring.md` | Design document | Human-readable dependency wiring narrative |
| `system_composition.json` | Design document | Machine-readable bootstrap sequence and API specification |
| `system_composition.md` | Design document | Human-readable system composition narrative |
| `context_wiring.json` | Design document | Machine-readable cross-context communication specification |
| `context_wiring.md` | Design document | Human-readable context wiring narrative |
| `phase_7_analysis.md` | Design document | Skills mapping and task-by-task analysis |
| `shell_composition_layer_summary.md` | This document | Comprehensive summary for both audiences |

---

### Dependency Direction

```
main.py
  └─► shell/api/app.py → build_container()
              ↓
              shell/composition/container.py
                  ↓                    ↓                    ↓
              BC-1 (conversation_management)  BC-2 (decision_intelligence)  BC-3 (knowledge_retrieval)
                  ↓
              infrastructure adapters / repositories
                  ↓
              domain entities / value objects

The arrow always points inward.
The shell is the only boundary permitted to reference multiple bounded contexts.
No bounded context imports from any other bounded context.
No bounded context imports from the shell.
```

---

### What Phase 7 Does Not Include

The following are intentionally out of scope:

- **Authentication / JWT** — `user_id` is treated as a pre-resolved trusted identity.
- **Async event bus** — No cross-context event handlers; synchronous drain-and-log pattern is architecturally complete for this system.
- **External message broker** — Kafka, RabbitMQ, Redis Streams are out of scope for a synchronous prototype.
- **Health check / readiness endpoints** — No `GET /health` or Kubernetes liveness probes implemented.
- **Multi-process session sharing** — `InMemoryConversationSessionRepository` is process-local; horizontal scaling requires a distributed session store (out of scope for prototype).
