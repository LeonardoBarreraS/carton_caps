# Event Bus Design
## Carton Caps Conversational Assistant — Phase 6, Infrastructure Layer

> **Companion document:** event_bus.json
> **Derived from:** domain_model.json · context_communication.json · adapters.json · repositories.json

---

## Architectural Decision

**Bus type: synchronous drain-and-publish — minimal by design.**

Domain events in this system are **observability signals, not behavioral triggers**. They are processed by one consumer (a file logger) and carry no routing, no handlers, and no cross-context delivery. The communication model defined in `context_communication.json` is explicit: all inter-context coordination happens through synchronous direct port calls (`COMM-1`, `COMM-2`). Events do not drive any cross-context behavior.

The RAG pipeline is inherently synchronous — evidence retrieval must complete before response generation. An asynchronous event bus would introduce complexity with no architectural benefit.

**Why not subscribe/dispatch?**  
There are no subscribers that respond to domain events with business logic. The only consumer is a logger. A subscribe/dispatch infrastructure would be machinery with no registered handlers — a solution looking for a problem.

**Why not an external broker?**  
No async workflow requirements, no multi-process fan-out, no event replay needs. Kafka, RabbitMQ, and Redis Streams are out of scope for the prototype.

---

## Event Summary

| ID | Event | Bounded Context | Emitted by | Drained in |
|---|---|---|---|---|
| EVT-SS | `SessionStarted` | BC-1 | `ConversationSession.complete_initialization()` | `StartSessionUseCase` |
| EVT-TP | `TurnProcessed` | BC-1 | `ConversationSession.complete_turn()` | `ProcessTurnUseCase` |
| EVT-SC | `SessionClosed` | BC-1 | `ConversationSession.close()` | `CloseSessionUseCase` |
| EVT-CU | `ContextUpdated` | BC-2 | `DecisionContext.add_signal()` | `ProcessTurnIntelligenceUseCase` |
| EVT-GD | `GapDetected` | BC-2 | `DecisionContext.record_gap_evaluation()` | `ProcessTurnIntelligenceUseCase` |
| EVT-CR | `ContextReady` | BC-2 | `DecisionContext.mark_ready()` | `ProcessTurnIntelligenceUseCase` |

---

## Publisher Ports

### EVTBUS-PORT-1 — `IEventPublisher` (BC-1)

**Location:** `src/conversation_management/application/ports/i_event_publisher.py`  
**Layer:** application  
**Implemented by:** EVTBUS-IMPL-1 — `LoggingEventPublisher`

```
IEventPublisher (BC-1)
  publish(events: list) -> None
```

**Events served:**

| Event | Drained in |
|---|---|
| `SessionStarted` | `StartSessionUseCase` |
| `TurnProcessed` | `ProcessTurnUseCase` |
| `SessionClosed` | `CloseSessionUseCase` |

---

### EVTBUS-PORT-2 — `IEventPublisher` (BC-2)

**Location:** `src/decision_intelligence/application/ports/i_event_publisher.py`  
**Layer:** application  
**Implemented by:** EVTBUS-IMPL-1 — `LoggingEventPublisher`

```
IEventPublisher (BC-2)
  publish(events: list) -> None
```

**Events served:**

| Event | Drained in | Conditional? |
|---|---|---|
| `ContextUpdated` | `ProcessTurnIntelligenceUseCase` | Emitted on every signal-adding turn |
| `GapDetected` | `ProcessTurnIntelligenceUseCase` | Conditional — only when gaps are non-empty |
| `ContextReady` | `ProcessTurnIntelligenceUseCase` | Conditional — only on first `ready` transition |

---

## Publisher Implementation

### EVTBUS-IMPL-1 — `LoggingEventPublisher`

**Location:** `src/shell/composition/logging_event_publisher.py`  
**Layer:** shell  
**Adapter ID:** ADAPT-17  
**Implements:** EVTBUS-PORT-1 (BC-1 `IEventPublisher`) + EVTBUS-PORT-2 (BC-2 `IEventPublisher`)  
**Output sink:** `data/domain_events.log`  
**Technology:** Python stdlib `logging` + `FileHandler`

**Behaviour:**
- Iterates the drained event batch; serialises each event via `dataclasses.asdict()`
- Writes one structured `INFO`-level log line per event: `[DomainEvent] <EventType> <field>=<value> ...`
- Never raises — all exceptions are silently swallowed to protect the main turn pipeline
- Configures the `FileHandler` once on construction; idempotent (no duplicate handlers)
- Creates `data/` directory if it does not exist

**Constructor:** `LoggingEventPublisher(log_path: str)`  
**Injection points:**

| Use case | Bounded context |
|---|---|
| `StartSessionUseCase` | BC-1 |
| `ProcessTurnUseCase` | BC-1 |
| `CloseSessionUseCase` | BC-1 |
| `ProcessTurnIntelligenceUseCase` | BC-2 |

One shared instance is injected into all four use cases from the composition root.

---

## Domain Event Registry

### EVT-SS — `SessionStarted`

**Location:** `src/conversation_management/domain/events/session_started.py`  
**Emitted by:** `ConversationSession.complete_initialization()`  
**Drained by:** `StartSessionUseCase`

Payload:
```
session_id   : str
user_id      : str
school_id    : str
occurred_at  : datetime
```

**Observability purpose:** Audit trail for session creation. Enables counting active sessions, measuring session frequency per user, and detecting initialization failures by absence.

---

### EVT-TP — `TurnProcessed`

**Location:** `src/conversation_management/domain/events/turn_processed.py`  
**Emitted by:** `ConversationSession.complete_turn()`  
**Drained by:** `ProcessTurnUseCase`

Payload:
```
session_id   : str
turn_count   : int
intent_value : str
occurred_at  : datetime
```

**Observability purpose:** Audit trail for every completed turn. Enables intent distribution analysis, conversation length tracking, and per-session activity timelines.

---

### EVT-SC — `SessionClosed`

**Location:** `src/conversation_management/domain/events/session_closed.py`  
**Emitted by:** `ConversationSession.close()`  
**Drained by:** `CloseSessionUseCase`

Payload:
```
session_id  : str
user_id     : str
occurred_at : datetime
```

**Observability purpose:** Audit trail for session closure. Enables session duration calculation and detection of sessions that are opened but never explicitly closed.

---

### EVT-CU — `ContextUpdated`

**Location:** `src/decision_intelligence/domain/events/context_updated.py`  
**Emitted by:** `DecisionContext.add_signal()`  
**Drained by:** `ProcessTurnIntelligenceUseCase`

Payload:
```
session_id    : str
context_state : str
signal_count  : int
occurred_at   : datetime
```

**Observability purpose:** Tracks preference signal accumulation across turns. Enables analysis of how many turns it takes for users to reach context readiness and which signal types are most frequently captured.

---

### EVT-GD — `GapDetected`

**Location:** `src/decision_intelligence/domain/events/gap_detected.py`  
**Emitted by:** `DecisionContext.record_gap_evaluation()` — conditional on non-empty gaps  
**Drained by:** `ProcessTurnIntelligenceUseCase`

Payload:
```
session_id  : str
gaps        : list[str]
occurred_at : datetime
```

**Observability purpose:** Audit trail for clarification requests. Enables tracking how often context gaps block retrieval, which gap types recur most frequently, and whether clarification loops converge.

> **Note:** The behavioral consequence (clarification question returned to the user) is delivered synchronously via `TurnIntelligenceResultDTO.clarification_needed`. The domain event is only for the observability log — it does not drive any handler or routing.

---

### EVT-CR — `ContextReady`

**Location:** `src/decision_intelligence/domain/events/context_ready.py`  
**Emitted by:** `DecisionContext.mark_ready()`  
**Drained by:** `ProcessTurnIntelligenceUseCase`

Payload:
```
session_id   : str
signal_count : int
occurred_at  : datetime
```

**Observability purpose:** Milestone event marking the first turn where context reached retrieval readiness. Enables measuring how many turns were required to build sufficient context for grounded retrieval.

---

## Event Flow

### Pattern: drain-and-publish

```
Aggregate (ConversationSession / DecisionContext)
  │
  │  domain operation executes
  │  self._events.append(SomeDomainEvent(...))
  │
  ▼
Use case
  │
  │  aggregate.collect_events()  →  drains and clears internal list
  │  self._event_publisher.publish(events)
  │
  ▼
LoggingEventPublisher
  │
  │  for event in events:
  │      dataclasses.asdict(event) → structured fields
  │      logger.info("[DomainEvent] EventType field=value ...")
  │
  ▼
data/domain_events.log
```

### Delivery guarantee

**At-most-once.** Events are not persisted before publishing — if the process crashes between drain and publish, those events are lost. This is acceptable for an observability-only log at prototype scope.

### Batch semantics

Events are published as a batch per aggregate drain. All events from a single domain operation are written in order with no interleaving from concurrent operations (single-process, synchronous pipeline).

---

## Full Event Lifecycle — Per Turn

```
POST /sessions/{id}/turns
 │
 ├── ProcessTurnUseCase (BC-1)
 │     ├── session.receive_message()
 │     ├── IIntentClassifier.classify()
 │     ├── IDecisionIntelligenceService.process_turn()  ──────────────────────┐
 │     │                                                                       │
 │     │                                                  ProcessTurnIntelligenceUseCase (BC-2)
 │     │                                                    ├── context.add_signal()
 │     │                                                    │     └── EVT-CU emitted
 │     │                                                    ├── context.record_gap_evaluation()
 │     │                                                    │     └── EVT-GD emitted (conditional)
 │     │                                                    ├── context.mark_ready()
 │     │                                                    │     └── EVT-CR emitted (conditional)
 │     │                                                    └── context.collect_events()
 │     │                                                          → event_publisher.publish([...])
 │     │                                                               → data/domain_events.log
 │     │
 │     ├── IResponseGenerator.generate()
 │     ├── IResponseEvaluator.evaluate()
 │     ├── session.complete_turn()
 │     │     └── EVT-TP emitted
 │     └── session.collect_events()
 │           → event_publisher.publish([EVT-TP])
 │                → data/domain_events.log
 │
 └── return AssistantResponse to API layer
```

---

## Folder Structure

```
src/
├── conversation_management/
│   ├── application/
│   │   └── ports/
│   │       └── i_event_publisher.py          EVTBUS-PORT-1
│   └── domain/
│       └── events/
│           ├── session_started.py             EVT-SS
│           ├── turn_processed.py              EVT-TP
│           └── session_closed.py              EVT-SC
│
├── decision_intelligence/
│   ├── application/
│   │   └── ports/
│   │       └── i_event_publisher.py          EVTBUS-PORT-2
│   └── domain/
│       └── events/
│           ├── context_updated.py             EVT-CU
│           ├── gap_detected.py                EVT-GD
│           └── context_ready.py               EVT-CR
│
└── shell/
    └── composition/
        └── logging_event_publisher.py         EVTBUS-IMPL-1 (ADAPT-17)

data/
└── domain_events.log                          output sink
```

---

## Scope Boundary

**In scope:**
- Domain event emission from `ConversationSession` and `DecisionContext` aggregates
- `IEventPublisher` port in BC-1 and BC-2 application layers
- `LoggingEventPublisher` shell implementation writing to `data/domain_events.log`
- Constructor injection of the single shared publisher into all four event-emitting use cases

**Out of scope:**
- Cross-context event routing — inter-context communication uses direct port calls (`COMM-1`, `COMM-2`)
- Event-driven handlers that trigger business logic — no such handlers exist in this system
- Event replay or event sourcing — not required at prototype scope
- Async event delivery — the synchronous RAG pipeline has no async requirements
- External message brokers — Kafka, RabbitMQ, Redis Streams are out of scope
- Subscribe/dispatch infrastructure — there are no subscribers; the port method is `publish()`, not `subscribe()`
