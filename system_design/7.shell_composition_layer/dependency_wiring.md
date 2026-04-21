# Dependency Wiring
## Carton Caps Conversational Assistant — Phase 7, Shell / Composition Layer

> **Companion document:** dependency_wiring.json  
> **Composition root:** `src/shell/composition/container.py`  
> **Derived from:** use_cases.json · adapters.json · repositories.json · event_bus.json · context_communication.json

---

## What Dependency Wiring Does

Dependency wiring is the act of assembling the system. It is the one place in the codebase that is permitted to know everything — every bounded context, every infrastructure implementation, every port — for the sole purpose of connecting them together.

The result is a fully constructed object graph, built once at startup, where every component receives its dependencies at construction time through constructor injection, and where no component knows how to build itself.

In this system, dependency wiring lives entirely in `src/shell/composition/`.

---

## Wiring Model

**Inter-context mechanism: synchronous adapter port calls.**  
**Event mechanism: observability drain only — no cross-context behavioral handlers.**

The RAG pipeline that drives every conversation turn is inherently synchronous: intent classification → intelligence processing → retrieval → response generation → evaluation. Each step depends on the output of the previous. Async inter-context routing would introduce latency and failure modes with no compensating benefit.

Domain events (`SessionStarted`, `TurnProcessed`, `SessionClosed`, `ContextUpdated`, `GapDetected`, `ContextReady`) are factual records emitted for observability. They have one consumer: a file logger. They do not trigger business logic in any bounded context and they do not drive cross-context communication. An event-subscription infrastructure would be machinery with no registered behavioral handlers.

---

## Bounded Contexts

| Context | Role | Exposes to Shell | Consumes via Ports |
|---|---|---|---|
| **BC-1** `conversation_management` | Primary driver — session lifecycle, turn orchestration, public API surface | `StartSessionUseCase`, `ProcessTurnUseCase`, `CloseSessionUseCase` | `IDecisionIntelligenceService` (→ BC-2) |
| **BC-2** `decision_intelligence` | Reasoning engine — DecisionContext, signal extraction, evidence evaluation, gap detection | `PreSeedContextUseCase`, `ProcessTurnIntelligenceUseCase` | `IKnowledgeRetrievalService` (→ BC-3) |
| **BC-3** `knowledge_retrieval` | Semantic search — product catalog and referral rules via Qdrant | `ExecuteRetrievalUseCase` | _(none)_ |

---

## Cross-Context Wiring

### COMM-1 — BC-1 → BC-2

```
BC-1 ConversationManagement
    IDecisionIntelligenceService   ← port defined in BC-1 application/ports/
              ↕
    DecisionIntelligenceAdapter    ← lives in src/shell/composition/adapters/
              ↕
BC-2 DecisionIntelligence
    PreSeedContextUseCase
    ProcessTurnIntelligenceUseCase
```

**Port:** `IDecisionIntelligenceService`  
**Defined in:** `src/conversation_management/application/ports/i_decision_intelligence_service.py`  
**Adapter:** `DecisionIntelligenceAdapter`  
**Adapter location:** `src/shell/composition/adapters/decision_intelligence_adapter.py`

| Method | Called by | When | DTO crossing boundary |
|---|---|---|---|
| `pre_seed_context(PreSeedContextDTO)` | `StartSessionUseCase` | Once per session, at initialization | `PreSeedContextDTO` → None |
| `process_turn(TurnInputDTO)` | `ProcessTurnUseCase` via TurnGraph | Every turn, after intent classification | `TurnInputDTO` → `TurnIntelligenceResultDTO` |

The adapter translates BC-1 DTOs into BC-2 commands. No BC-1 domain objects (ConversationSession, Intent, AssistantResponse) ever cross into BC-2. No BC-2 domain objects (DecisionContext, PreferenceSignal, EvidenceChunk) ever cross into BC-1.

**Wiring in `build_container()`:**
```python
decision_intelligence_adapter = DecisionIntelligenceAdapter(
    pre_seed_use_case=pre_seed_uc,
    process_turn_use_case=process_turn_intelligence_uc,
)
start_session_uc = StartSessionUseCase(
    ...,
    decision_intelligence_service=decision_intelligence_adapter,
    ...
)
process_turn_uc = ProcessTurnUseCase(
    ...,
    decision_intelligence_service=decision_intelligence_adapter,
    ...
)
```

---

### COMM-2 — BC-2 → BC-3

```
BC-2 DecisionIntelligence
    IKnowledgeRetrievalService     ← port defined in BC-2 application/ports/
              ↕
    KnowledgeRetrievalAdapter      ← lives in src/shell/composition/adapters/
              ↕
BC-3 KnowledgeRetrieval
    ExecuteRetrievalUseCase
```

**Port:** `IKnowledgeRetrievalService`  
**Defined in:** `src/decision_intelligence/application/ports/i_knowledge_retrieval_service.py`  
**Adapter:** `KnowledgeRetrievalAdapter`  
**Adapter location:** `src/shell/composition/adapters/knowledge_retrieval_adapter.py`

| Method | Called by | When | DTO crossing boundary |
|---|---|---|---|
| `retrieve(RetrievalQueryDTO)` | `ProcessTurnIntelligenceUseCase` via DecisionIntelligenceSubgraph | When DecisionContext is ready/enriched and intent is product or referral inquiry | `RetrievalQueryDTO` → `RetrievedEvidenceDTO` |

No BC-2 domain objects cross into BC-3. The result surfaces back to BC-1 via `TurnIntelligenceResultDTO` — a chain of DTO translations with no domain object leakage.

**Wiring in `build_container()`:**
```python
knowledge_retrieval_adapter = KnowledgeRetrievalAdapter(
    execute_retrieval_use_case=execute_retrieval_uc,
)
process_turn_intelligence_uc = ProcessTurnIntelligenceUseCase(
    ...,
    knowledge_retrieval_service=knowledge_retrieval_adapter,
    ...
)
```

---

## Event Publisher Wiring

```
LoggingEventPublisher
  implements BC1IEventPublisher  ← src/conversation_management/application/ports/i_event_publisher.py
  implements BC2IEventPublisher  ← src/decision_intelligence/application/ports/i_event_publisher.py
  writes to  data/domain_events.log
```

A single `LoggingEventPublisher` instance is created in `build_container()` and wired to every use case that emits domain events. Multiple inheritance allows the single instance to satisfy both port contracts.

| Use case | Context | Events published |
|---|---|---|
| `StartSessionUseCase` | BC-1 | `SessionStarted` |
| `ProcessTurnUseCase` | BC-1 | `TurnProcessed` |
| `CloseSessionUseCase` | BC-1 | `SessionClosed` |
| `ProcessTurnIntelligenceUseCase` | BC-2 | `ContextUpdated`, `GapDetected`\*, `ContextReady`\* |

\* Conditional — emitted only when the corresponding domain state transition occurs.

**Events are drained synchronously inside each use case boundary, then published in a single batch. The publisher never raises — write failures are silently swallowed so the turn pipeline is never interrupted.**

Events do **not** cross context boundaries. There are no cross-context event handlers, no event subscribers, and no event-driven orchestration in this system.

**Wiring in `build_container()`:**
```python
event_publisher = LoggingEventPublisher(log_path=domain_event_log_path)
```

---

## Full Infrastructure Wiring

| Wire ID | Port | Implementation | Context | Storage | Injected Into |
|---|---|---|---|---|---|
| WIRE-1 | `IConversationSessionRepository` | `InMemoryConversationSessionRepository` | BC-1 | Python dict | StartSession, ProcessTurn, CloseSession |
| WIRE-2 | `IConversationHistoryRepository` | `SQLiteConversationHistoryRepository` | BC-1 | SQLite — Conversation_History | StartSession, ProcessTurn |
| WIRE-3 | `IUserRepository` | `SQLiteUserRepository` | BC-1 | SQLite — Users (read-only) | StartSession, ProcessTurn |
| WIRE-4 | `ISchoolRepository` | `SQLiteSchoolRepository` | BC-1 | SQLite — Schools+Users JOIN (read-only) | StartSession, ProcessTurn |
| WIRE-5 | `IPurchaseHistoryRepository` | `SQLitePurchaseHistoryRepository` | BC-1 | SQLite — Purchase_History+Products JOIN (read-only) | StartSession |
| WIRE-6 | `IIntentClassifier` | `OpenAIIntentClassifier` | BC-1 | OpenAI gpt-4o-mini | ProcessTurn (via TurnGraph) |
| WIRE-7 | `IResponseGenerator` | `OpenAIResponseGenerator` | BC-1 | OpenAI gpt-4o | ProcessTurn (via TurnGraph) |
| WIRE-8 | `IResponseEvaluator` | `OpenAIResponseEvaluator` | BC-1 | OpenAI gpt-4o-mini | ProcessTurn (via TurnGraph) |
| WIRE-9 | `IDecisionContextRepository` | `InMemoryDecisionContextRepository` | BC-2 | Python dict | PreSeedContext, ProcessTurnIntelligence |
| WIRE-10 | `ISignalExtractor` | `OpenAISignalExtractor` | BC-2 | OpenAI gpt-4o-mini | ProcessTurnIntelligence (via subgraph) |
| WIRE-11 | `IEvidenceEvaluator` | `OpenAIEvidenceEvaluator` | BC-2 | OpenAI gpt-4o-mini | ProcessTurnIntelligence (via subgraph) |
| WIRE-12 | `IProductRepository` | `QdrantProductRepository` | BC-3 | Qdrant — product_catalog | ExecuteRetrieval |
| WIRE-13 | `IReferralRuleRepository` | `QdrantReferralRuleRepository` | BC-3 | Qdrant — referral_program_rules | ExecuteRetrieval |
| WIRE-14 | `IEventPublisher` (BC-1 + BC-2) | `LoggingEventPublisher` | cross-cutting | file — domain_events.log | StartSession, ProcessTurn, CloseSession, ProcessTurnIntelligence |
| WIRE-15 | `IRAGMetricsLogger` | `SQLiteRAGMetricsLogger` | BC-1 | SQLite — rag_metrics.sqlite | ProcessTurn |

---

## Object Graph Assembly Order

`build_container()` assembles the object graph bottom-up, from the most downstream dependency to the most upstream consumer. This guarantees that every object's dependencies are fully constructed before it is instantiated.

```
Step 1 — Configuration
    load_dotenv()
    read: OPENAI_API_KEY, SQLITE_DB_PATH, DOMAIN_EVENT_LOG_PATH
          QDRANT_URL, LLM_MODEL, MIN_GROUNDEDNESS, MIN_RELEVANCE
          RAG_METRICS_DB_PATH

Step 2 — Shared clients
    openai_client = OpenAI(api_key=openai_api_key)

Step 3 — BC-3 infrastructure
    product_repo  = QdrantProductRepository(qdrant_url, openai_client)
    referral_repo = QdrantReferralRuleRepository(qdrant_url, openai_client)

Step 4 — BC-3 use cases
    execute_retrieval_uc = ExecuteRetrievalUseCase(product_repo, referral_repo)

Step 5 — COMM-2 cross-context adapter
    knowledge_retrieval_adapter = KnowledgeRetrievalAdapter(execute_retrieval_uc)

Step 6 — BC-2 infrastructure
    decision_context_repo = InMemoryDecisionContextRepository()
    signal_extractor      = OpenAISignalExtractor(openai_client, llm_model)
    evidence_evaluator    = OpenAIEvidenceEvaluator(openai_client, llm_model)

Step 7 — BC-2 use cases
    pre_seed_uc                = PreSeedContextUseCase(decision_context_repo)
    process_turn_intelligence_uc = ProcessTurnIntelligenceUseCase(
        decision_context_repo, signal_extractor, evidence_evaluator,
        knowledge_retrieval_adapter, event_publisher   ← see step 9
    )

Step 8 — COMM-1 cross-context adapter
    decision_intelligence_adapter = DecisionIntelligenceAdapter(
        pre_seed_uc, process_turn_intelligence_uc
    )

Step 9 — Cross-cutting event publisher
    event_publisher = LoggingEventPublisher(log_path=domain_event_log_path)

Step 10 — BC-1 infrastructure
    history_repo          = SQLiteConversationHistoryRepository(sqlite_db_path)
    session_repo          = InMemoryConversationSessionRepository()
    user_repo             = SQLiteUserRepository(sqlite_db_path)
    school_repo           = SQLiteSchoolRepository(sqlite_db_path)
    purchase_history_repo = SQLitePurchaseHistoryRepository(sqlite_db_path)
    intent_classifier     = OpenAIIntentClassifier(openai_client, llm_model)
    response_generator    = OpenAIResponseGenerator(openai_client, llm_model)
    response_evaluator    = OpenAIResponseEvaluator(openai_client, llm_model)
    rag_metrics_logger    = SQLiteRAGMetricsLogger(rag_metrics_db_path)

Step 11 — BC-1 use cases
    start_session_uc = StartSessionUseCase(
        session_repo, history_repo, user_repo, school_repo, purchase_history_repo,
        decision_intelligence_adapter, event_publisher
    )
    process_turn_uc = ProcessTurnUseCase(
        session_repo, intent_classifier, decision_intelligence_adapter,
        response_generator, response_evaluator, history_repo,
        event_publisher, min_groundedness, min_relevance,
        user_repository=user_repo, school_repository=school_repo,
        rag_metrics_logger=rag_metrics_logger
    )
    close_session_uc = CloseSessionUseCase(session_repo, event_publisher)

Step 12 — Composition output
    return AppContainer(
        start_session=start_session_uc,
        process_turn=process_turn_uc,
        close_session=close_session_uc,
    )
```

The assembly order strictly observes the dependency direction:

```
BC-3 (no upstream)
  ↑ COMM-2 adapter wires BC-3 into BC-2 scope
BC-2 (depends on BC-3 via port)
  ↑ COMM-1 adapter wires BC-2 into BC-1 scope
BC-1 (depends on BC-2 via port)
  ↑ AppContainer exposes BC-1 use cases to the API layer
```

---

## Configuration

All configuration is sourced from environment variables, with safe defaults for local development. `load_dotenv()` is called at the top of `build_container()` — no `.env` file is required.

| Environment Variable | Default | Used By |
|---|---|---|
| `OPENAI_API_KEY` | _(empty string)_ | All LLM adapters |
| `SQLITE_DB_PATH` | `data/carton_caps_data.sqlite` | All SQLite repositories |
| `DOMAIN_EVENT_LOG_PATH` | `data/domain_events.log` | LoggingEventPublisher |
| `QDRANT_URL` | `http://localhost:6333` | Qdrant repositories |
| `LLM_MODEL` | `gpt-4o-mini` | All OpenAI adapters |
| `MIN_GROUNDEDNESS` | `0.8` | ProcessTurnUseCase quality gate |
| `MIN_RELEVANCE` | `0.75` | ProcessTurnUseCase quality gate |
| `RAG_METRICS_DB_PATH` | `data/rag_metrics.sqlite` | SQLiteRAGMetricsLogger |

---

## Implementation Note — WIRE-15

**`IRAGMetricsLogger` / `SQLiteRAGMetricsLogger` (ADAPT-15) — Wired**

`ProcessTurnUseCase` accepts `rag_metrics_logger: IRAGMetricsLogger` as a constructor dependency and calls `self._rag_metrics_logger.log_turn_metrics(...)` after `TurnGraph` completes. `build_container()` instantiates `SQLiteRAGMetricsLogger(db_path=rag_metrics_db_path)` and injects it into `ProcessTurnUseCase`.

Per-turn RAG metrics (groundedness, relevance, context recall, context precision, context state, fallback rate) are persisted to `data/rag_metrics.sqlite` on every turn.

---

## Shell Folder Structure

```
src/shell/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── app.py              FastAPI factory — create_app(), exception handlers
│   ├── router.py           3 route handlers (POST /sessions, POST turns, DELETE session)
│   └── schemas.py          Pydantic request/response/error models
└── composition/
    ├── __init__.py
    ├── container.py                    Composition root — build_container() → AppContainer
    ├── logging_event_publisher.py      LoggingEventPublisher — BC-1 + BC-2 IEventPublisher
    └── adapters/
        ├── __init__.py
        ├── decision_intelligence_adapter.py    COMM-1 bridge
        └── knowledge_retrieval_adapter.py      COMM-2 bridge

main.py                     ASGI entry point — app = create_app()
```

---

## Wiring Rules

**Must:**
- All wiring lives in `src/shell/composition/` — never inside a bounded context
- All dependencies injected through constructors at startup — never on demand
- Object graph assembled bottom-up: BC-3 → COMM-2 → BC-2 → COMM-1 → event publisher → BC-1
- One shared `OpenAI` client instance across all five LLM adapters
- One shared `LoggingEventPublisher` instance wired to all event-emitting use cases

**Must not:**
- No domain logic in wiring code — `build_container()` has zero conditional business rules
- No bounded context may import from `src/shell/`
- No service locator, no global registry, no on-demand resolution
- No `event_bus.subscribe()` calls — there are no cross-context event handlers in this system
- No async event dispatch infrastructure — the pipeline is synchronous by architectural decision
- No external message broker (Kafka, RabbitMQ, Redis Streams) — out of scope for this prototype
