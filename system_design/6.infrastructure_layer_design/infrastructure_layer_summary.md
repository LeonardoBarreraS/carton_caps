# Phase 6 — Infrastructure Layer Design: Summary

---

## Part I — For Non-Technical Readers

### What problem were we solving?

By the end of Phase 5 the system had a complete set of business rules and a precise blueprint for every operation the assistant can perform. Every capability — classifying a user's intent, retrieving product knowledge, evaluating the quality of a response — was defined as a clean contract: a description of *what* is needed, with no opinion whatsoever about *how* it would be delivered.

That is exactly the right separation between architecture layers. But contracts alone do not make a system run. Something has to open the SQLite database, call the OpenAI API, talk to the vector search engine, and expose a URL the world can reach.

That is exactly what Phase 6 answered.

Phase 6 is the layer that connects the clean, rule-driven interior of the system to the real world. It is the last layer before the system becomes runnable.

---

### Why does infrastructure get its own dedicated phase?

Software systems age. The business rules that define how a Carton Caps conversation works — what constitutes a valid session, what makes a response grounded, how signals accumulate across turns — those rules change slowly when they change at all. The infrastructure that runs those rules changes constantly: cloud providers get replaced, databases get upgraded, AI models get superseded.

By keeping infrastructure strictly separated from business rules, the entire technology stack can be swapped — a different vector database, a different LLM provider, a different storage engine — without touching a single line of domain logic. The contracts defined in Phase 5 guarantee that. Phase 6 is the fulfilment of those contracts for the current technology choices.

---

### What were the four tasks of Phase 6?

Phase 6 was broken into four sequential tasks, each building on the previous.

---

#### Task 1 — Adapters: Connecting to External Services

Every time the assistant needs to do something that involves the outside world — asking an AI model to classify a message, searching a database for products, scoring the quality of a response — it goes through a thin translation layer called an **adapter**. The adapter speaks the clean language of the domain on one side and the real API or database protocol on the other.

Seventeen adapters were designed and built:

- **Five AI adapters** connect to OpenAI. Two handle understanding the conversation (classifying intent, extracting preference signals). Two handle generating and scoring responses (`gpt-4o` for quality generation, `gpt-4o-mini` for fast evaluation). One handles scoring the quality of evidence retrieved from the knowledge base.
- **Two vector search adapters** connect to the Qdrant vector database — one for searching the product catalog, one for searching the referral program rules. These are the "read side" of the knowledge base that the ingestion pipeline populated.
- **Six database adapters** connect to the existing SQLite database and read user records, school information, purchase history, and conversation history.
- **One observability adapter** writes quality scores for every AI pipeline execution to a dedicated metrics database, allowing the team to see how accurately and usefully the system responds over time.
- **One event adapter** records every significant system event — session opened, turn processed, session closed — to a structured log file.

A key technology decision was made here: the vector store was migrated from ChromaDB (used during initial ingestion) to **Qdrant**. Both the write side (ingestion) and the read side (runtime queries) now use the same embedding model (`text-embedding-3-small`), which is essential for retrieval quality — using different models at write and read time would cause the search to return irrelevant results.

---

#### Task 2 — Repositories: Persisting and Loading Domain Objects

If adapters are translators to external services, **repositories** are the system's memory. They know how to save a conversation session, load a user's school, find all prior messages, and retrieve a context object that accumulated across the entire conversation.

Eight repository contracts were defined and nine concrete implementations were built:

- **Session storage** uses an in-memory Python dictionary — session state only needs to live as long as a running conversation, and instant access across multiple pipeline steps is more important than durability at prototype scale.
- **Conversation history** persists to the existing SQLite database, with careful migration logic to preserve any pre-existing records. The system can read back and continue a human-readable conversation history that spans restarts.
- **User, school, and purchase history** are read directly from the existing SQLite database that Carton Caps already populates — the system consumes existing data rather than duplicating it.
- **Decision context** — the accumulation of preference signals the AI reasoning engine builds up across turns — is held in memory, scoped to the lifetime of a session.
- **Product and referral rule lookups** use semantic vector search — the system understands meaning, not just keywords, when searching for relevant knowledge.

---

#### Task 3 — Event Bus: Recording Everything That Matters

Every time something important happens in the system — a session starts, a turn completes, a new preference signal is learned, a context gap is detected — the system emits a **domain event**. These events are factual records: they describe what happened, when, and with what data.

In this system, domain events serve one purpose: **observability**. They are not triggers for further logic; they are a structured audit trail. The event bus was designed to match that reality: it is deliberately simple, synchronous, and never risks blocking the main conversation pipeline.

A single shared publisher — `LoggingEventPublisher` — collects all events from both the Conversation Management and Decision Intelligence contexts after each use-case boundary, serializes them to a structured file (`data/domain_events.log`), and never raises an error regardless of what happens during logging. The main pipeline is never interrupted by a logging failure.

Six domain events are tracked:

| Event | Meaning |
|---|---|
| `SessionStarted` | A session was opened and fully initialised |
| `TurnProcessed` | A user message was processed and a response delivered |
| `SessionClosed` | A session was explicitly terminated |
| `ContextUpdated` | The reasoning engine learned a new preference signal |
| `GapDetected` | The reasoning engine detected missing context and issued a clarifying question |
| `ContextReady` | Enough signals were accumulated to proceed with knowledge retrieval |

---

#### Task 4 — API Entry Points: The Door the World Knocks On

All of the work in the previous five phases — domain modeling, application orchestration, infrastructure implementation — culminates in three HTTP endpoints. These three endpoints are the only surface the outside world touches.

| Endpoint | What it does |
|---|---|
| `POST /sessions` | Opens a new conversation, loads all user context, seeds the reasoning engine, returns a session identifier |
| `POST /sessions/{id}/turns` | Receives a user message, runs the full AI pipeline, returns a grounded response with quality scores |
| `DELETE /sessions/{id}` | Closes a session gracefully, enforcing that it is in an idle state first |

The API layer was built with **FastAPI** — a Python framework that generates automatic interactive documentation, validates every request shape before it touches any code, and handles errors uniformly using a registered exception handler map. Every domain error (session not found, user not authorised, session in wrong state) is mapped to a precise HTTP status code and a structured error envelope. No business logic lives anywhere near the route handlers — they only translate HTTP into commands that the application layer already knows how to execute.

The system is started with a single command: `uvicorn main:app --host 0.0.0.0 --port 8000`

---

### What does the completed system look like end to end?

When a user sends a message like *"What products do you have for kids aged 5 to 8?"*, the following happens:

1. The client sends `POST /sessions/{id}/turns` with the user's message.
2. FastAPI validates the request and hands it to the route handler.
3. The route handler builds a command and calls `ProcessTurnUseCase`.
4. The use case guards that the session exists, is idle, and belongs to the requesting user.
5. The AI pipeline begins: OpenAI classifies the intent as `product_inquiry`.
6. Decision Intelligence examines accumulated context — if `product_category` is missing, it may ask a clarifying question first.
7. A semantically enriched query is constructed and sent to the Qdrant vector store, retrieving the most relevant products by meaning.
8. OpenAI generates a grounded response citing only the retrieved evidence.
9. Two quality scores are computed: groundedness (are all claims traceable to evidence?) and relevance (does this answer the question?).
10. If scores pass the thresholds, the response is delivered. If not, a safe fallback is returned.
11. Both the user message and the assistant response are written to conversation history.
12. Quality scores are written to the RAG metrics database.
13. Domain events are drained and written to the event log.
14. HTTP 200 is returned with the full response envelope.

From the user's perspective: they sent a message and received a helpful, school-specific, product-grounded answer.

---

### What was actually built?

| What | Count | Technology |
|---|---|---|
| Infrastructure adapters | 17 | OpenAI, Qdrant, SQLite, Python stdlib |
| Repository interfaces | 8 | Domain ports (clean contracts) |
| Repository implementations | 9 | Python dict × 3, SQLite × 4, Qdrant × 2 |
| Domain events tracked | 6 | Python dataclasses + stdlib logging |
| REST API endpoints | 3 | FastAPI |
| Exception handler mappings | 8 | HTTP 409 / 404 / 422 / 403 |
| Total new Python files | ~40 | Across 5 modules |

Every one of these components was designed to be replaceable: swap the vector store, change the LLM provider, move to a production database — none of those infrastructure decisions require touching domain or application logic.

---

---

## Part II — Technical Reference

### Layer Role and Constraints

The infrastructure layer sits at the outermost ring of the Clean Architecture stack.

```
Infrastructure (Phase 6)     — adapters, repositories, event publisher, API entry points
─────────────────────────────────────────────────────────────────────────────────────────
Application Layer (Phase 5)  — use cases, LangGraph workflows, ports, DTOs
─────────────────────────────────────────────────────────────────────────────────────────
Domain Layer (Phase 4)       — entities, value objects, invariants, domain events
```

**Rules that govern this layer:**
- Infrastructure depends on application and domain. Domain never imports infrastructure.
- Adapters implement exactly one port contract per class (single responsibility).
- No domain logic lives in any adapter. Adapters only translate data shapes and call external APIs.
- Repository implementations hold no query logic beyond what the port method contract requires.
- The shell layer (`src/shell/`) is the only location permitted to import across bounded context boundaries simultaneously.
- The domain event publisher is placed in the shell exactly because it must satisfy ports from both BC-1 and BC-2.

---

### Task 1 — Adapter Inventory

**New port added during this phase:**

#### `IRAGMetricsLogger` (PORT-OBS-1)
**Location:** `src/conversation_management/application/ports/i_rag_metrics_logger.py`

An observability port injected into `ProcessTurnUseCase`. Called after every TurnGraph execution. Receives `TurnMetricsDTO` (12 fields: session_id, turn_number, intent, context_state, 4 RAG scores, is_fallback, clarification_needed, evidence_chunk_count, timestamp) and persists to `rag_metrics.sqlite`. Keeps observability entirely outside domain logic.

---

#### Complete Adapter Registry

| ID | Class | Port | BC | Technology |
|---|---|---|---|---|
| ADAPT-1 | `QdrantVectorStoreWriter` | `IVectorStoreWriter` | Ingestion | Qdrant + OpenAI embeddings |
| ADAPT-2 | `OpenAIIntentClassifier` | `IIntentClassifier` | BC-1 | `gpt-4o-mini`, JSON mode |
| ADAPT-3 | `OpenAIResponseGenerator` | `IResponseGenerator` | BC-1 | `gpt-4o` |
| ADAPT-4 | `OpenAIResponseEvaluator` | `IResponseEvaluator` | BC-1 | `gpt-4o-mini`, JSON mode |
| ADAPT-5 | `OpenAISignalExtractor` | `ISignalExtractor` | BC-2 | `gpt-4o-mini`, JSON mode |
| ADAPT-6 | `OpenAIEvidenceEvaluator` | `IEvidenceEvaluator` | BC-2 | `gpt-4o-mini`, JSON mode |
| ADAPT-7 | `QdrantProductRepository` | `IProductRepository` | BC-3 | Qdrant `product_catalog` |
| ADAPT-8 | `QdrantReferralRuleRepository` | `IReferralRuleRepository` | BC-3 | Qdrant `referral_program_rules` |
| ADAPT-9 | `InMemoryConversationSessionRepository` | `IConversationSessionRepository` | BC-1 | Python dict |
| ADAPT-10 | `InMemoryConversationHistoryRepository` | `IConversationHistoryRepository` | BC-1 | Python defaultdict (dev alt) |
| ADAPT-11 | `SQLiteUserRepository` | `IUserRepository` | BC-1 | SQLite `Users` |
| ADAPT-12 | `SQLiteSchoolRepository` | `ISchoolRepository` | BC-1 | SQLite `Schools`+`Users` JOIN |
| ADAPT-13 | `SQLitePurchaseHistoryRepository` | `IPurchaseHistoryRepository` | BC-1 | SQLite `Purchase_History`+`Products` JOIN |
| ADAPT-14 | `InMemoryDecisionContextRepository` | `IDecisionContextRepository` | BC-2 | Python dict |
| ADAPT-15 | `SQLiteRAGMetricsLogger` | `IRAGMetricsLogger` | BC-1 | SQLite `rag_metrics.sqlite` |
| ADAPT-16 | `SQLiteConversationHistoryRepository` | `IConversationHistoryRepository` | BC-1 | SQLite `Conversation_History` (primary) |
| ADAPT-17 | `LoggingEventPublisher` | `IEventPublisher` (BC-1 + BC-2) | shell | Python stdlib logging |

**Already complete from Phase 5 (not rebuilt):**

| Port | Adapter | Location |
|---|---|---|
| `IDecisionIntelligenceService` | `DecisionIntelligenceAdapter` | `src/shell/composition/adapters/` |
| `IKnowledgeRetrievalService` | `KnowledgeRetrievalAdapter` | `src/shell/composition/adapters/` |

---

#### LLM Adapter Design Notes

**ADAPT-2 — `OpenAIIntentClassifier`** (`gpt-4o-mini`, JSON mode)  
Five valid intents: `product_inquiry`, `referral_question`, `general_question`, `clarification_response`, `ambiguous`. Falls back to `AMBIGUOUS` on unrecognised values. System prompt includes Carton Caps context and one-shot examples for the boundary case between `product_inquiry` and `referral_question`.

**ADAPT-3 — `OpenAIResponseGenerator`** (`gpt-4o`)  
The only adapter using `gpt-4o`. Evidence chunks injected as a numbered list with explicit instruction never to invent facts. `generate_clarification()` wraps the clarification question string into a conversational response. Scores start at `0.0` — populated by ADAPT-4 in the next node.

**ADAPT-4 — `OpenAIResponseEvaluator`** (`gpt-4o-mini`, JSON mode)  
Computes `groundedness_score` (claim tracing) and `relevance_score` (reverse-question technique) in one call. Scores clamped to `[0.0, 1.0]`. Returns a **new** `AssistantResponse` via `dataclasses.replace()` — immutability preserved. `reasoning` field attached for debugging.

**ADAPT-5 — `OpenAISignalExtractor`** (`gpt-4o-mini`, JSON mode)  
Extracts `PreferenceSignal` list from raw user messages. Conservative extraction — never forces signals. Emits exactly five valid keys: `product_category`, `meal_occasion`, `dietary_restriction`, `health_goal`, `budget_tier`. These keys were selected because their values appear verbatim in the enriched product documents stored in Qdrant, making them directly effective for vector similarity matching. Keys removed from the original design — `brand_preference` (no brand data in the catalog), `family_size` (not indexed in product embeddings), `age_group` (too coarse) — were dropped to focus extraction on signals that provably improve retrieval quality. Receives full `conversation_history` for context-aware extraction across all turns.

**ADAPT-6 — `OpenAIEvidenceEvaluator`** (`gpt-4o-mini`, JSON mode)  
Scores `context_recall_score` (coverage) and `context_precision_score` (relevance-to-query) for the retrieved evidence batch. Scores drive the **retry loop** in `DecisionIntelligenceSubgraph` — if `recall < 0.6` and retries remain, the subgraph constructs a refined query (up to `max_retries=2`). Returns `RetrievedEvidence.create()` with updated scores — immutability preserved.

---

#### Vector Store Technology Decision

The ingestion pipeline originally used **ChromaDB**. Phase 6 migrated both write (ADAPT-1) and read (ADAPT-7, ADAPT-8) sides to **Qdrant**. The critical constraint: the embedding model must be identical at write and read time. `text-embedding-3-small` with vector size 1536 and cosine distance is used for both collections. Using different models would produce an incoherent vector space and destroy retrieval quality.

---

#### Observability Adapter — ADAPT-15 `SQLiteRAGMetricsLogger`

Every `ProcessTurnUseCase` execution writes one row to `data/rag_metrics.sqlite`:

| Column | Type | Description |
|---|---|---|
| `session_id` | TEXT | Conversation session |
| `turn_number` | INTEGER | Turn index within session |
| `intent` | TEXT | Classified intent |
| `context_state` | TEXT | `empty` / `partial` / `ready` / `enriched` at retrieval time |
| `context_recall_score` | REAL | Did the vector search find the right evidence? |
| `context_precision_score` | REAL | Were retrieved chunks relevant? |
| `groundedness_score` | REAL | Are response claims traceable to evidence? |
| `relevance_score` | REAL | Does the response answer the question? |
| `is_fallback` | INTEGER | 1 if quality gate failed |
| `clarification_needed` | INTEGER | 1 if BC-2 detected context gaps |
| `evidence_chunk_count` | INTEGER | Number of chunks retrieved |
| `timestamp` | TEXT | ISO 8601 UTC |

---

### Task 2 — Repository Design

#### Repository Categories

| Category | Description | Repos |
|---|---|---|
| Aggregate Repository | Full lifecycle (save/load) of a mutable aggregate root | REPO-1, REPO-6 |
| Append Repository | Append-only write + chronological read | REPO-2 |
| Read-Only Repository | Query only — fixture data managed externally | REPO-3, REPO-4, REPO-5 |
| Search Repository | Semantic similarity search via Qdrant | REPO-7, REPO-8 |

#### Interface-to-Implementation Summary

| ID | Interface | Implementation | Adapter | Storage | BC |
|---|---|---|---|---|---|
| REPO-1 | `IConversationSessionRepository` | `InMemoryConversationSessionRepository` | ADAPT-9 | Python dict | BC-1 |
| REPO-2 | `IConversationHistoryRepository` | `SQLiteConversationHistoryRepository` (primary) | ADAPT-16 | SQLite `Conversation_History` | BC-1 |
| REPO-2 | `IConversationHistoryRepository` | `InMemoryConversationHistoryRepository` (dev alt) | ADAPT-10 | Python defaultdict | BC-1 |
| REPO-3 | `IUserRepository` | `SQLiteUserRepository` | ADAPT-11 | SQLite `Users` | BC-1 |
| REPO-4 | `ISchoolRepository` | `SQLiteSchoolRepository` | ADAPT-12 | SQLite `Schools`+`Users` JOIN | BC-1 |
| REPO-5 | `IPurchaseHistoryRepository` | `SQLitePurchaseHistoryRepository` | ADAPT-13 | SQLite `Purchase_History`+`Products` JOIN | BC-1 |
| REPO-6 | `IDecisionContextRepository` | `InMemoryDecisionContextRepository` | ADAPT-14 | Python dict | BC-2 |
| REPO-7 | `IProductRepository` | `QdrantProductRepository` | ADAPT-7 | Qdrant `product_catalog` | BC-3 |
| REPO-8 | `IReferralRuleRepository` | `QdrantReferralRuleRepository` | ADAPT-8 | Qdrant `referral_program_rules` | BC-3 |

#### Key Design Decisions

**REPO-1 / REPO-6 — In-memory aggregates:** Session and decision context state is turn-scoped by design. Zero-latency access across a multi-step synchronous pipeline outweighs durability requirements at prototype scale.

**REPO-2 — Append-only history with backward-compatible migration:** `SQLiteConversationHistoryRepository.__init__` adds optional `history_id` and `session_id` columns via `ALTER TABLE IF NOT EXISTS`. Existing rows receive empty-string defaults. On read, legacy `sender='bot'` is mapped to `SenderType.ASSISTANT` via `_SENDER_MAP`. On write, domain `SenderType.ASSISTANT` (`'assistant'`) is translated to `'bot'` via `_DB_SENDER_MAP` to satisfy the `CHECK(sender IN ('user', 'bot'))` constraint on the pre-existing table. The in-memory variant remains available for fast unit testing.

**REPO-5 — `list[dict]` contract:** Purchase records cross the BC-1→BC-2 boundary as primitive signal seeds in `PreSeedContextDTO.purchase_signals`. No purchase domain entity exists in BC-1 — creating one would add unnecessary coupling.

**REPO-7 / REPO-8 — Qdrant payload fallback chains:** `product_id` resolved via `payload.product_id` → `payload.doc_id` → `str(point.id)`. Ensures compatibility with different ingestion schemas without failing on payload variance.

---

### Task 3 — Event Bus Design

#### Architectural Decision: Synchronous Drain-and-Publish

Domain events in this system are **observability signals, not behavioral triggers**. All inter-context coordination happens through synchronous direct port calls (`COMM-1`, `COMM-2`). Events carry no routing and drive no cross-context behavior. The pipeline is inherently synchronous — an asynchronous bus would introduce latency buffering with zero architectural benefit.

**Pattern:** After each use-case transaction boundary, the use case calls `aggregate.collect_events()` to drain the event queue, then passes the list to `IEventPublisher.publish()`. This is the only publish point — events cannot bypass it.

#### Event Registry

| ID | Event | BC | Emitted by Domain Method | Drained in Use Case |
|---|---|---|---|---|
| EVT-SS | `SessionStarted` | BC-1 | `ConversationSession.complete_initialization()` | `StartSessionUseCase` |
| EVT-TP | `TurnProcessed` | BC-1 | `ConversationSession.complete_turn()` | `ProcessTurnUseCase` |
| EVT-SC | `SessionClosed` | BC-1 | `ConversationSession.close()` | `CloseSessionUseCase` |
| EVT-CU | `ContextUpdated` | BC-2 | `DecisionContext.add_signal()` | `ProcessTurnIntelligenceUseCase` |
| EVT-GD | `GapDetected` | BC-2 | `DecisionContext.record_gap_evaluation()` — conditional | `ProcessTurnIntelligenceUseCase` |
| EVT-CR | `ContextReady` | BC-2 | `DecisionContext.mark_ready()` — conditional | `ProcessTurnIntelligenceUseCase` |

#### EVTBUS-IMPL-1 — `LoggingEventPublisher` (ADAPT-17)

**Location:** `src/shell/composition/logging_event_publisher.py`  
**Implements:** EVTBUS-PORT-1 (BC-1 `IEventPublisher`) + EVTBUS-PORT-2 (BC-2 `IEventPublisher`) via Python multiple inheritance  
**Output:** `data/domain_events.log` (configurable via `DOMAIN_EVENT_LOG_PATH`)  
**Behaviour:**
- Iterates drained event batch; serialises each event via `dataclasses.asdict()`
- Writes one structured `INFO`-level log line per event: `[DomainEvent] <EventType> <field>=<value> ...`
- **Never raises** — all exceptions silently swallowed to protect the main turn pipeline
- Configures `FileHandler` once on construction; idempotent against re-construction in same process
- Creates `data/` directory if it does not exist

**Shell placement rationale:** `LoggingEventPublisher` is the only class in the system that must satisfy ports from two different bounded contexts simultaneously. The shell layer is the only location where such cross-BC imports are architecturally permitted.

#### Injection Points

One shared instance injected into all four use cases from the composition root:

| Use Case | BC |
|---|---|
| `StartSessionUseCase` | BC-1 |
| `ProcessTurnUseCase` | BC-1 |
| `CloseSessionUseCase` | BC-1 |
| `ProcessTurnIntelligenceUseCase` | BC-2 |

---

### Task 4 — API Entry Points

#### Framework: FastAPI (REST)

FastAPI selected for automatic OpenAPI documentation, Pydantic v2 request validation, and zero-boilerplate exception handler registration. Transport is HTTP/REST only — GraphQL, CLI, and webhook entry points are out of scope for the prototype.

#### Endpoint Summary

| ID | Method | Path | Use Case | Success Status |
|---|---|---|---|---|
| EP-1 | `POST` | `/sessions` | `StartSessionUseCase` (UC-1) | 201 Created |
| EP-2 | `POST` | `/sessions/{session_id}/turns` | `ProcessTurnUseCase` (UC-2) | 200 OK |
| EP-3 | `DELETE` | `/sessions/{session_id}` | `CloseSessionUseCase` (UC-3) | 200 OK |

#### Module Structure

```
src/shell/api/
├── __init__.py      package marker
├── schemas.py       Pydantic v2 request/response/error models
├── router.py        build_router(container) — 3 route handlers
└── app.py           create_app() — wires container, registers exception handlers, includes router

main.py              ASGI entry point at workspace root — app = create_app()
```

**Startup sequence:**
1. `uvicorn main:app` loads `main.py`
2. `create_app()` calls `build_container()` — all infrastructure and use cases instantiated once
3. Exception handlers registered on the app instance
4. Router included — app ready to serve

**Run:** `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

#### Schemas (`schemas.py`)

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

All handlers registered at app level in `app.py`. Route handlers never catch exceptions. Every 4xx response uses the standard error envelope `{"error_code": "...", "message": "..."}`.

| Exception | Status | Error Code | Source |
|---|---|---|---|
| `SessionConflictError` | 409 | `SESSION_CONFLICT` | `start_session_use_case` |
| `UserNotFoundError` | 404 | `USER_NOT_FOUND` | `start_session_use_case` |
| `SchoolNotFoundError` | 404 | `SCHOOL_NOT_FOUND` | `start_session_use_case` |
| `SessionNotFoundError` | 404 | `SESSION_NOT_FOUND` | `process_turn_use_case`, `close_session_use_case` |
| `InvalidTurnStateError` | 422 | `INVALID_SESSION_STATE` | `process_turn_use_case` |
| `SessionOwnershipError` | 403 | `OWNERSHIP_MISMATCH` | `process_turn_use_case` |
| `AuthorizationError` | 403 | `AUTHORIZATION_ERROR` | `close_session_use_case` |
| `InvalidSessionTransitionError` | 409 | `INVALID_STATE_TRANSITION` | domain — `conversation_session` |

#### EP-2 — Full Request/Response Flow

```
Client
  │
  │  POST /sessions/{session_id}/turns
  │  { "user_id": "u-42", "message": "What products for kids 5–8?" }
  │
  ▼
router.py — process_turn handler
  │  Pydantic validation (ProcessTurnRequest)
  │  ProcessTurnCommand(session_id, user_id, message)
  │
  ▼
ProcessTurnUseCase.execute(command)                     BC-1
  │  guard: session exists / ownership / status=IDLE
  │  session.receive_message()           [idle → active]
  │
  ▼
TurnGraph.invoke(initial_state)
  │
  ├── classify_intent
  │       └─► OpenAIIntentClassifier (ADAPT-2)
  │
  ├── process_decision_intelligence
  │       └─► IDecisionIntelligenceService (shell adapter)  COMM-1
  │                   ▼
  │           ProcessTurnIntelligenceUseCase (BC-2)
  │                   ▼
  │           DecisionIntelligenceSubgraph
  │               ├── OpenAISignalExtractor   (ADAPT-5)
  │               ├── (retry loop if recall < 0.6)
  │               ├── execute_retrieval
  │               │       └─► IKnowledgeRetrievalService (shell adapter)  COMM-2
  │               │                   ▼
  │               │           ExecuteRetrievalUseCase (BC-3)
  │               │               └─► QdrantProductRepository / QdrantReferralRuleRepository
  │               └── OpenAIEvidenceEvaluator (ADAPT-6)
  │
  ├── generate_response / generate_clarification
  │       └─► OpenAIResponseGenerator (ADAPT-3)
  │
  ├── evaluate_response
  │       └─► OpenAIResponseEvaluator (ADAPT-4)
  │
  ├── persist_turn
  │       └─► SQLiteConversationHistoryRepository (ADAPT-16) × 2 appends
  │
  └── return_fallback (if groundedness < 0.8 OR relevance < 0.75)
  │
  ▼
session.complete_turn(intent, response_vo)   [active → idle]
IConversationSessionRepository.save(session)
session.collect_events() → IEventPublisher.publish(events)
IRAGMetricsLogger.log(TurnMetricsDTO)
  │
  ▼
ProcessTurnResponse(session_id, response_text, intent, is_fallback, scores)
  │
  ▼
schemas.py — ProcessTurnResponse (Pydantic)
  │
  ▼
HTTP 200 { "session_id": ..., "response_text": ..., "intent": ..., "is_fallback": ...,
           "groundedness_score": ..., "relevance_score": ... }
```

---

### Complete Infrastructure File Manifest

```
src/
├── ingestion/
│   └── infrastructure/
│       └── vector_store/
│           └── qdrant_writer.py                  ← ADAPT-1 (replaces chroma_writer.py)
│
├── conversation_management/
│   ├── application/
│   │   └── ports/
│   │       └── i_rag_metrics_logger.py           ← PORT-OBS-1 (new — Phase 6)
│   └── infrastructure/
│       ├── llm/
│       │   ├── openai_intent_classifier.py        ← ADAPT-2
│       │   ├── openai_response_generator.py       ← ADAPT-3
│       │   └── openai_response_evaluator.py       ← ADAPT-4
│       ├── repositories/
│       │   ├── in_memory_conversation_session_repository.py  ← ADAPT-9  (REPO-1)
│       │   ├── in_memory_conversation_history_repository.py  ← ADAPT-10 (REPO-2 dev alt)
│       │   ├── sqlite_conversation_history_repository.py     ← ADAPT-16 (REPO-2 primary)
│       │   ├── sqlite_user_repository.py                     ← ADAPT-11 (REPO-3)
│       │   ├── sqlite_school_repository.py                   ← ADAPT-12 (REPO-4)
│       │   └── sqlite_purchase_history_repository.py         ← ADAPT-13 (REPO-5)
│       └── observability/
│           └── sqlite_rag_metrics_logger.py                  ← ADAPT-15
│
├── decision_intelligence/
│   └── infrastructure/
│       ├── llm/
│       │   ├── openai_signal_extractor.py         ← ADAPT-5
│       │   └── openai_evidence_evaluator.py       ← ADAPT-6
│       └── repositories/
│           └── in_memory_decision_context_repository.py  ← ADAPT-14 (REPO-6)
│
├── knowledge_retrieval/
│   └── infrastructure/
│       └── repositories/
│           ├── qdrant_product_repository.py       ← ADAPT-7 (REPO-7)
│           └── qdrant_referral_rule_repository.py ← ADAPT-8 (REPO-8)
│
└── shell/
    ├── composition/
    │   └── logging_event_publisher.py             ← ADAPT-17 (EVTBUS-IMPL-1)
    └── api/
        ├── __init__.py
        ├── schemas.py                             ← Pydantic request/response/error models
        ├── router.py                              ← build_router(container) — 3 handlers
        └── app.py                                 ← create_app() + exception handlers

main.py                                            ← ASGI root entry point
data/
├── domain_events.log                              ← ADAPT-17 output (auto-created)
└── rag_metrics.sqlite                             ← ADAPT-15 output (auto-created)
```

---

### Dependency Direction

```
main.py
  └─► shell/api/app.py → build_container()
        └─► shell/composition/container.py
              ├── BC-1 infrastructure ──► BC-1 application ──► BC-1 domain
              ├── BC-2 infrastructure ──► BC-2 application ──► BC-2 domain
              ├── BC-3 infrastructure                      ──► BC-3 domain
              └── shell/logging_event_publisher.py
                    ├── BC-1 application/ports/i_event_publisher.py
                    └── BC-2 application/ports/i_event_publisher.py

The arrow always points inward.
Domain layers import nothing from infrastructure or application.
Shell is the only boundary allowed to reference multiple bounded contexts.
```

---

### What Phase 6 Does Not Include

The following are intentionally out of scope for the prototype:

- **Authentication / JWT** — `user_id` is treated as a pre-resolved trusted identity
- **Rate limiting, CORS, TLS termination** — handled at infrastructure boundary (reverse proxy)
- **Event replay or event sourcing** — domain events are observability-only
- **Async messaging** (Kafka, RabbitMQ, Redis Streams) — not required with a synchronous RAG pipeline
- **Cross-restart session persistence** — in-memory storage is correct for prototype scope
- **Multi-process / distributed deployment** — single-process ASGI app is the target topology
