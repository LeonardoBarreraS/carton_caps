# Phase 7 — Shell / Composition Layer: Analysis
## Carton Caps Conversational Assistant

> **Scope:** Dependency Wiring · System Composition · Context Wiring  
> **Skills applied:** `dependency-wiring-skill` · `system-composition-skill` · `context-wiring`  
> **Status:** All three tasks fully implemented prior to formal Phase 7 planning.

---

## Executive Summary

All three shell/composition layer tasks are **already complete**. The implementation was carried forward organically from Phase 6 (Infrastructure Layer Design), where the API entry points and composition root were built as part of making the system runnable. No new development work is required in Phase 7. This document records what was built, how it maps to each skill, and what specifically does **not** apply to this system and why.

---

## Task 1 — Dependency Wiring

**Skill:** `dependency-wiring-skill`  
**Status:** COMPLETE

### What was built

| Artifact | Location | Purpose |
|---|---|---|
| `AppContainer` dataclass | `src/shell/composition/container.py` | Typed holder for the 3 exposed use cases |
| `build_container()` function | `src/shell/composition/container.py` | Single composition root — assembles the full object graph |
| `LoggingEventPublisher` | `src/shell/composition/logging_event_publisher.py` | Shell-layer implementation of both BC-1 and BC-2 `IEventPublisher` ports |
| `DecisionIntelligenceAdapter` | `src/shell/composition/adapters/decision_intelligence_adapter.py` | Cross-context bridge: BC-1 → BC-2 |
| `KnowledgeRetrievalAdapter` | `src/shell/composition/adapters/knowledge_retrieval_adapter.py` | Cross-context bridge: BC-2 → BC-3 |

### Wiring order in `build_container()`

The instantiation follows strict bottom-up dependency order, matching the skill's prescribed flow (`infrastructure → application → domain`):

```
1. Configuration (env vars / dotenv)
2. Shared OpenAI client
3. BC-3 infrastructure  →  BC-3 use cases  →  KnowledgeRetrievalAdapter
4. BC-2 infrastructure  →  BC-2 use cases  →  DecisionIntelligenceAdapter
5. BC-1 infrastructure  →  BC-1 use cases
6. return AppContainer(start_session, process_turn, close_session)
```

This order is intentional: downstream dependencies (BC-3, BC-2) are fully constructed before the upstream contexts (BC-1) that depend on them are instantiated.

### Key wiring decisions

- **Single `OpenAI` client instance** shared across all five AI adapters — avoids duplicate connection overhead.
- **Single `LoggingEventPublisher` instance** satisfies both `BC1IEventPublisher` and `BC2IEventPublisher` via multiple inheritance. It is wired to all three BC-1 use cases and to `ProcessTurnIntelligenceUseCase` in BC-2.
- **`InMemoryConversationSessionRepository`** — session state is intentionally ephemeral (prototype scope); no persistence needed.
- **`InMemoryDecisionContextRepository`** — decision context is session-scoped by design and lives only in working memory.
- **Configuration defaults** allow the system to start with zero environment variables set (local development path for SQLite, `localhost:6333` for Qdrant, `gpt-4o-mini` as model).

### Skill rules satisfied

| Rule | How |
|---|---|
| Wiring lives in shell | All wiring is in `src/shell/composition/` |
| Instantiates implementations | All infrastructure classes are `new`-ed inside `build_container()` |
| Injects dependencies | Constructor injection throughout — no service locator |
| Builds object graph | Full graph assembled before any use case is exposed |
| Does not contain domain logic | `build_container()` has zero conditional business rules |

---

## Task 2 — System Composition

**Skill:** `system-composition-skill`  
**Status:** COMPLETE

### What was built

| Artifact | Location | Purpose |
|---|---|---|
| `create_app()` factory | `src/shell/api/app.py` | FastAPI app initialization, exception handler registration |
| `build_router()` | `src/shell/api/router.py` | Route registration for all 3 API endpoints |
| Pydantic schemas | `src/shell/api/schemas.py` | Request/response models + `ErrorResponse` |
| `main.py` | workspace root | ASGI entry point — `app = create_app()` |

### Composition sequence

```
uvicorn main:app
    ↓
main.py → create_app()
    ↓
build_container()         ← full object graph assembled once
    ↓
build_router(container)   ← routes registered, use cases bound
    ↓
exception handlers        ← 9 domain errors mapped to HTTP status codes
    ↓
app ready to serve
```

### Routes registered

| Method | Path | Handler | Use Case |
|---|---|---|---|
| `POST` | `/sessions` | `start_session` | `StartSessionUseCase` |
| `POST` | `/sessions/{session_id}/turns` | `process_turn` | `ProcessTurnUseCase` |
| `DELETE` | `/sessions/{session_id}` | `close_session` | `CloseSessionUseCase` |

### Exception handler coverage

| Domain Exception | HTTP Status | Error Code |
|---|---|---|
| `SessionConflictError` | 409 | `SESSION_CONFLICT` |
| `UserNotFoundError` | 404 | `USER_NOT_FOUND` |
| `SchoolNotFoundError` | 404 | `SCHOOL_NOT_FOUND` |
| `SessionNotFoundError` (turn) | 404 | `SESSION_NOT_FOUND` |
| `SessionNotFoundError` (close) | 404 | `SESSION_NOT_FOUND` |
| `SessionOwnershipError` | 403 | `OWNERSHIP_MISMATCH` |
| `InvalidTurnStateError` | 422 | `INVALID_SESSION_STATE` |
| `AuthorizationError` | 403 | `AUTHORIZATION_ERROR` |
| `InvalidSessionTransitionError` | 409 | `INVALID_STATE_TRANSITION` |

### Skill rules satisfied

| Rule | How |
|---|---|
| Starts system | `uvicorn main:app` loads `main.py`, calls `create_app()` |
| Registers routes | `build_router()` registers all 3 routes |
| Initializes controllers | `container` resolved at startup, use cases bound to handlers |
| Activates handlers | Exception handlers registered before first request |
| Contains no domain logic | `app.py` and `router.py` have zero business rules |

---

## Task 3 — Context Wiring

**Skill:** `context-wiring`  
**Status:** COMPLETE — but with a critical architectural distinction.

### How this system's context wiring differs from the skill template

The `context-wiring` skill prescribes **event subscriptions** as the primary mechanism for connecting bounded contexts:

```python
# skill template
event_bus.subscribe(OrderCreated, process_payment_handler)
event_bus.subscribe(PaymentCompleted, send_notification_handler)
```

**This system does not use that pattern.** The architectural decision, recorded in `context_communication.json`, is:

> *"All cross-context calls are synchronous and cross via port interfaces defined in the caller's application layer. Domain events are intra-component signals only — they do not drive cross-context communication."*

The rationale is sound and documented:

1. **The RAG pipeline is inherently synchronous** — evidence retrieval must complete before response generation can begin; async routing adds latency with no benefit.
2. **Domain events are observability signals, not behavioral triggers** — the only consumer of all 6 domain events is the `LoggingEventPublisher` (file logger). There are no handlers that respond to events with business logic.
3. **An event subscription infrastructure would be machinery with no registered handlers** — a subscribe/dispatch setup would exist purely to dispatch to a logger that needs no dispatch at all.

### What was built instead

Context wiring is achieved through **synchronous direct port calls via shell adapters**:

```
BC-1 ConversationManagement
    IDecisionIntelligenceService (port defined in BC-1 application/ports/)
         ↕  DecisionIntelligenceAdapter (shell wiring)
BC-2 DecisionIntelligence
    IKnowledgeRetrievalService (port defined in BC-2 application/ports/)
         ↕  KnowledgeRetrievalAdapter (shell wiring)
BC-3 KnowledgeRetrieval
```

Both adapters are instantiated and injected in `build_container()` — this is the context wiring. The shell layer is the only place in the codebase permitted to import from multiple bounded contexts simultaneously.

### Cross-context communication map

| Contract | Direction | Mechanism | Adapter |
|---|---|---|---|
| COMM-1 | BC-1 → BC-2 | `IDecisionIntelligenceService` port → DTO | `DecisionIntelligenceAdapter` |
| COMM-2 | BC-2 → BC-3 | `IKnowledgeRetrievalService` port → DTO | `KnowledgeRetrievalAdapter` |

### What must NOT be done

The following items from the generic skill template **must not be added** to this system:

| Skill template item | Why not applicable |
|---|---|
| `event_bus.subscribe(Event, Handler)` | No cross-context event subscribers exist or are needed |
| Async event dispatch infrastructure | The RAG pipeline is synchronous by architectural decision |
| Event routing between contexts | Events are observability signals; all routing is via synchronous adapters |
| External broker integration (Kafka, RabbitMQ) | No async workflows, no multi-process fan-out, prototype scope |
| `NotificationContext` fan-out wiring | No notification bounded context exists in this system |

---

## File Map — Full Shell Layer

```
src/shell/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── app.py                  FastAPI factory + exception handlers
│   ├── router.py               3 route handlers (POST, POST, DELETE)
│   └── schemas.py              Pydantic request/response/error models
└── composition/
    ├── __init__.py
    ├── container.py            Composition root — build_container()
    ├── logging_event_publisher.py  Shell event publisher (BC-1 + BC-2 ports)
    └── adapters/
        ├── __init__.py
        ├── decision_intelligence_adapter.py  BC-1 → BC-2 bridge
        └── knowledge_retrieval_adapter.py    BC-2 → BC-3 bridge

main.py                         ASGI entry point at workspace root
```

---

## Dependency Direction Verification

```
main.py
    → shell.api.app (create_app)
        → shell.composition.container (build_container)
            → conversation_management.application.use_cases.*
            → decision_intelligence.application.use_cases.*
            → knowledge_retrieval.application.use_cases.*
            → conversation_management.infrastructure.*
            → decision_intelligence.infrastructure.*
            → knowledge_retrieval.infrastructure.*
            → shell.composition.adapters.*   ← only place with multi-BC imports
            → shell.composition.logging_event_publisher
        → shell.api.router (build_router)
            → shell.api.schemas
```

Shell imports from all layers. No bounded context imports from shell. Dependency arrows flow strictly inward. Clean Architecture rules are satisfied.

---

## Conclusion

Phase 7 is complete. All three skills have been operationalized, with one deliberate and documented deviation from the `context-wiring` skill's event subscription template: this system wires bounded contexts through synchronous adapter calls rather than event subscriptions, which matches its RAG pipeline semantics and keeps the system strictly synchronous. No additional development work is required in the shell/composition layer to make the system runnable.

**Run command:**
```
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
