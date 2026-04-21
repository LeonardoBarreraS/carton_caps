# Context Wiring
## Carton Caps Conversational Assistant — Phase 7, Shell / Composition Layer

> **Companion document:** context_wiring.json  
> **Derived from:** event_bus.json · context_coordination.json · context_communication.json · dependency_wiring.json  
> **Precondition:** Dependency wiring complete — bounded contexts assembled. System composition complete — API layer bootstrapped.

---

## What Context Wiring Does

Context wiring is the act of connecting bounded contexts to each other. It defines which contexts talk, through what channel, carrying what data, and in which direction. It also defines how domain events are connected to their consumers.

Context wiring is the final act of shell composition: once dependencies are wired and the system is bootstrapped, the question is: *how do the pieces talk to each other?*

In this system, context wiring lives in `src/shell/composition/` — exclusively the adapters folder and the event publisher.

---

## Wiring Model

**Cross-context mechanism: synchronous adapter port calls.**  
**Event mechanism: intra-context observability drain — no cross-context routing.**

The `context-wiring` skill prescribes `event_bus.subscribe(Event, Handler)` as its standard wiring pattern. **This system uses a different mechanism by design**, documented in `context_communication.json`:

> *"Domain events are intra-component signals only — they do not drive cross-context communication."*

The RAG pipeline is a blocking sequential chain: intent classification → signal extraction → context evaluation → evidence retrieval → response generation → response evaluation. Each stage needs the result of the previous stage before it can proceed. Synchronous direct port calls are the only mechanism that fits this structure. Reactive event handling would require BC-1 to emit an event and await BC-2's reaction — the opposite of what is needed.

There are no cross-context event handlers in this system because there is no cross-context reactive behavior to implement.

---

## Bounded Contexts

### BC-1 — Conversation Management

**Role:** Primary driver. Owns session lifecycle, turn orchestration, intent classification, response generation and evaluation, and the public API surface.

**Outbound cross-context connection:** `IDecisionIntelligenceService` → BC-2  
**Intra-context events emitted:** `SessionStarted`, `TurnProcessed`, `SessionClosed`  
**Event publisher port:** `IEventPublisher` (BC-1) → `LoggingEventPublisher`

---

### BC-2 — Decision Intelligence

**Role:** Reasoning engine. Owns DecisionContext lifecycle, preference signal extraction, context readiness evaluation, retrieval query construction, and evidence quality scoring.

**Outbound cross-context connection:** `IKnowledgeRetrievalService` → BC-3  
**Inbound cross-context connection:** Called by BC-1 via `IDecisionIntelligenceService`  
**Intra-context events emitted:** `ContextUpdated`, `GapDetected`\*, `ContextReady`\*  
**Event publisher port:** `IEventPublisher` (BC-2) → `LoggingEventPublisher`

\* Conditional — emitted only when the corresponding domain state transition occurs.

---

### BC-3 — Knowledge Retrieval

**Role:** Semantic search service. Owns all Qdrant vector store queries for products and referral program rules.

**Outbound cross-context connection:** None — leaf service  
**Inbound cross-context connection:** Called by BC-2 via `IKnowledgeRetrievalService`  
**Intra-context events:** None  
**Event publisher port:** None

---

## Events

All six domain events are **intra-context observability signals**. None crosses a context boundary. None triggers behavior in any other context.

| Event | Context | Emitted by | Behavioral consequence | Cross-context routed? |
|---|---|---|---|---|
| `SessionStarted` | BC-1 | `ConversationSession.complete_initialization()` | None — audit record | No |
| `TurnProcessed` | BC-1 | `ConversationSession.complete_turn()` | None — audit record | No |
| `SessionClosed` | BC-1 | `ConversationSession.close()` | None — audit record | No |
| `ContextUpdated` | BC-2 | `DecisionContext.add_signal()` | None — audit record | No |
| `GapDetected` | BC-2 | `DecisionContext.record_gap_evaluation()` | Clarification signal travels via `TurnIntelligenceResultDTO`, not via this event | No |
| `ContextReady` | BC-2 | `DecisionContext.mark_ready()` | None — milestone record | No |

The `GapDetected` event deserves attention: the behavioral consequence of a detected gap (asking the user a clarification question) does not travel via the event. It travels synchronously via the `clarification_needed` and `clarification_question` fields in `TurnIntelligenceResultDTO` — the return value of the COMM-1 `process_turn` port call. The event is an audit record of the same fact, written independently to the log.

---

## Handlers

**Cross-context handlers: none.**

The skill template's handler concept applies when a context must react to an event from another context with business logic. In this system:

- BC-2 does not react to BC-1 events (`SessionStarted`, `TurnProcessed`, `SessionClosed`)
- BC-3 does not react to BC-2 events (`ContextUpdated`, `GapDetected`, `ContextReady`)
- No context reacts to any other context's events

The only event consumer in this system is `LoggingEventPublisher` — an observability sink, not a behavioral handler. It writes structured log lines and returns. It implements no business logic.

---

## Wiring

### Cross-Context Connections

#### WIRE-CC-1 — COMM-1: BC-1 → BC-2

```
BC-1 ConversationManagement
    IDecisionIntelligenceService      ← port defined in BC-1 application/ports/
              ↕
    DecisionIntelligenceAdapter       ← src/shell/composition/adapters/decision_intelligence_adapter.py
              ↕
BC-2 DecisionIntelligence
    PreSeedContextUseCase
    ProcessTurnIntelligenceUseCase
```

| Call | Triggered by | When | Request DTO | Response DTO |
|---|---|---|---|---|
| `pre_seed_context` | `StartSessionUseCase` | Once per session at initialization | `PreSeedContextDTO` | None |
| `process_turn` | `ProcessTurnUseCase` via TurnGraph | Every turn, after intent classification | `TurnInputDTO` | `TurnIntelligenceResultDTO` |

**DTO isolation:** `PreSeedContextDTO` carries `session_id`, `school_id`, `school_name`, `purchase_signals` — all primitives. `TurnInputDTO` carries `session_id`, `intent`, `message`, `turn_number`, `conversation_history` (full OpenAI-format message list). `TurnIntelligenceResultDTO` carries evidence chunks, scores, context state, and clarification signal — all primitives. No BC-1 domain objects (`ConversationSession`, `Intent`, `AssistantResponse`) enter BC-2. No BC-2 domain objects (`DecisionContext`, `PreferenceSignal`, `EvidenceChunk`) return to BC-1.

---

#### WIRE-CC-2 — COMM-2: BC-2 → BC-3

```
BC-2 DecisionIntelligence
    IKnowledgeRetrievalService        ← port defined in BC-2 application/ports/
              ↕
    KnowledgeRetrievalAdapter         ← src/shell/composition/adapters/knowledge_retrieval_adapter.py
              ↕
BC-3 KnowledgeRetrieval
    ExecuteRetrievalUseCase
```

| Call | Triggered by | When | Request DTO | Response DTO |
|---|---|---|---|---|
| `retrieve` | `ProcessTurnIntelligenceUseCase` via DecisionIntelligenceSubgraph | When DecisionContext is ready/enriched and intent is `product_inquiry` or `referral_inquiry` | `RetrievalQueryDTO` | `RetrievedEvidenceDTO` |

**Frequency:** 0–N calls per turn. Conditional on context readiness and intent. Includes a retry cycle on low evidence recall — the subgraph may call `retrieve` more than once per turn before committing.

**DTO isolation:** `RetrievalQueryDTO` carries `query_text` and `source_target` — both primitives. `RetrievedEvidenceDTO` carries `chunks` (list of strings) and `evidence_type` (string). No BC-2 domain objects enter BC-3.

---

### Intra-Context Event Wiring

Both event wires terminate at the same shared `LoggingEventPublisher` instance.

#### WIRE-EVT-1 — BC-1 events → LoggingEventPublisher

```
BC-1 aggregates raise events
ConversationSession._events ← [SessionStarted | TurnProcessed | SessionClosed]
    ↓ use case calls collect_events()
    ↓ use case calls IEventPublisher.publish(events)
LoggingEventPublisher.publish(events)
    ↓ dataclasses.asdict(event) per event
    ↓ logging.info("[DomainEvent] ...")
data/domain_events.log
```

**Wired in:** `build_container()` — `event_publisher = LoggingEventPublisher(...)` injected into `StartSessionUseCase`, `ProcessTurnUseCase`, `CloseSessionUseCase`.

#### WIRE-EVT-2 — BC-2 events → LoggingEventPublisher

```
BC-2 aggregates raise events
DecisionContext._events ← [ContextUpdated | GapDetected | ContextReady]
    ↓ use case calls collect_events()
    ↓ use case calls IEventPublisher.publish(events)
LoggingEventPublisher.publish(events)   ← same instance as WIRE-EVT-1
    ↓ dataclasses.asdict(event) per event
    ↓ logging.info("[DomainEvent] ...")
data/domain_events.log
```

**Wired in:** `build_container()` — same `event_publisher` instance injected into `ProcessTurnIntelligenceUseCase`.

**Implementation note:** `LoggingEventPublisher` extends both `BC1IEventPublisher` and `BC2IEventPublisher` via multiple inheritance. One constructor call; one file handler; one log file. Both event streams write to the same sink.

---

## Complete Wiring Topology

```
API / HTTP request
    ↓
BC-1 ConversationManagement
    │
    ├─ COMM-1 ──────────────────────────────────────────┐
    │  IDecisionIntelligenceService                      │
    │  DecisionIntelligenceAdapter (shell)               │
    │                                                 BC-2 DecisionIntelligence
    │                                                    │
    │                                                    ├─ COMM-2 ─────────────────┐
    │                                                    │  IKnowledgeRetrievalService│
    │                                                    │  KnowledgeRetrievalAdapter │
    │                                                    │               BC-3 KnowledgeRetrieval
    │                                                    │               (Qdrant)    │
    │                                                    │  ← RetrievedEvidenceDTO ──┘
    │                                                    │
    │                                                 BC-2 events (ContextUpdated,
    │                                                    GapDetected, ContextReady)
    │                                                    ↓ IEventPublisher (BC-2)
    │  ← TurnIntelligenceResultDTO ──────────────────────┘  LoggingEventPublisher
    │                                                              ↓
    │                                                     domain_events.log
    │
BC-1 events (SessionStarted, TurnProcessed, SessionClosed)
    ↓ IEventPublisher (BC-1)
    LoggingEventPublisher (same instance)
    ↓
domain_events.log
    │
BC-1 returns HTTP response
```

---

## Coordinators

### COORD-1 — Session Initialization (BC-1 × BC-2)

**Realization:** embedded in `StartSessionUseCase` (UC-1)  
**Shell connection:** WIRE-CC-1, `pre_seed_context` method

```
StartSessionUseCase
    → IDecisionIntelligenceService.pre_seed_context(PreSeedContextDTO)
    → DecisionIntelligenceAdapter
    → PreSeedContextUseCase.execute(session_id, school_id, school_name, purchase_signals)
    → DecisionContext created and saved in BC-2
    ← None returned (void)
    → session.complete_initialization() in BC-1 — session becomes idle
```

This coordination is gated: the session becomes idle (ready for turns) only **after** BC-2 confirms the DecisionContext exists. INV-CS-3 is enforced architecturally — the initialization order is the wiring itself.

---

### COORD-2 — Conversation Turn (BC-1 × BC-2 × BC-3)

**Realization:** embedded in `TurnGraph` (WF-GRAPH-1) inside `ProcessTurnUseCase` (UC-2)  
**Shell connections:** WIRE-CC-1 (`process_turn` method) + WIRE-CC-2 (`retrieve` method)

```
ProcessTurnUseCase → TurnGraph
    → classify_intent (BC-1 internal)
    → process_decision_intelligence
        → IDecisionIntelligenceService.process_turn(TurnInputDTO)
        → DecisionIntelligenceAdapter
        → ProcessTurnIntelligenceUseCase → DecisionIntelligenceSubgraph
            → extract_signals (BC-2 internal)
            → update_decision_context (BC-2 internal)
            → evaluate_context_readiness (BC-2 internal)
            ↓ [if context ready + retrieval intent]
            → construct_retrieval_query (BC-2 internal)
            → execute_retrieval
                → IKnowledgeRetrievalService.retrieve(RetrievalQueryDTO)
                → KnowledgeRetrievalAdapter
                → ExecuteRetrievalUseCase.execute(command)
                → Qdrant semantic search
                ← RetrievedEvidenceDTO
            → evaluate_evidence_quality (BC-2 internal)
            ← TurnIntelligenceResultDTO
    → generate_response or generate_clarification (BC-1 internal)
    → evaluate_response (BC-1 internal)
    → persist_turn or return_fallback (BC-1 internal)
```

---

## Shell Wiring Artifacts

```
src/shell/composition/
├── adapters/
│   ├── decision_intelligence_adapter.py    WIRE-CC-1 — BC-1 → BC-2 bridge
│   └── knowledge_retrieval_adapter.py      WIRE-CC-2 — BC-2 → BC-3 bridge
└── logging_event_publisher.py              WIRE-EVT-1 + WIRE-EVT-2 — observability sink
```

---

## Wiring Rules

**Must:**
- All cross-context connections implemented as shell adapters in `src/shell/composition/adapters/`
- Each port interface defined in the calling context's application layer only — never in the receiving context
- DTOs carry only primitives — no domain objects cross context boundaries
- The same `LoggingEventPublisher` instance wired to both `IEventPublisher` ports (BC-1 and BC-2)
- Context isolation confirmed: no BC module has an import statement referencing another BC module

**Must not:**
- No bounded context imports from another bounded context
- No domain event routed across a context boundary — events terminate at the local observability sink
- No `event_bus.subscribe()` between contexts — there are no cross-context handlers
- No async event dispatch — the pipeline is synchronous by design
- No business logic in `LoggingEventPublisher` — it is a transport, not a handler
