# API Entry Points Design
## Carton Caps Conversational Assistant — Phase 6, Infrastructure Layer

> **Companion document:** api_entrypoints.json
> **Derived from:** use_cases.json · domain_model.json · context_communication.json · phase_6_task_analysis.md

---

## Framework: FastAPI (REST)

Three REST endpoints. One framework. No extra surface.

FastAPI is used because it produces automatic OpenAPI documentation, provides Pydantic-based request validation out of the box, and requires minimal boilerplate for a three-endpoint API. Transport is HTTP/REST — no GraphQL, no CLI, no webhooks are needed for the prototype deliverable.

The API layer sits entirely in `src/shell/api/`. It only imports from the composition root and the use-case command/response dataclasses. It contains **no domain logic**.

---

## Endpoint Summary

| ID | Method | Path | Use Case | Success |
|---|---|---|---|---|
| EP-1 | `POST` | `/sessions` | `StartSessionUseCase` (UC-1) | 201 |
| EP-2 | `POST` | `/sessions/{session_id}/turns` | `ProcessTurnUseCase` (UC-2) | 200 |
| EP-3 | `DELETE` | `/sessions/{session_id}` | `CloseSessionUseCase` (UC-3) | 200 |

---

## Module Structure

```
src/shell/api/
├── __init__.py
├── app.py          FastAPI app factory — create_app(), exception handlers
├── router.py       Three route handlers — builds commands, calls use cases, maps responses
└── schemas.py      Pydantic request/response models

main.py             ASGI entry point at workspace root — app = create_app()
```

**Startup sequence:**
1. `uvicorn main:app` loads `main.py`
2. `create_app()` calls `build_container()` — all infrastructure and use cases instantiated once
3. Exception handlers registered on the app instance
4. Router included — app ready to serve

**Run command:**
```
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## EP-1 — Start Session

### `POST /sessions`

**Use case:** `StartSessionUseCase` (UC-1)  
**Success status:** `201 Created`

Creates and fully initialises a `ConversationSession`. Loads user, school, conversation history, and purchase history. Pre-seeds `DecisionContext` in BC-2. Returns a `session_id` the client must use for all subsequent calls. Enforces one active/idle session per user.

#### Request body

```json
{
  "user_id": "u-42"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `user_id` | string | yes | Pre-resolved trusted user identity |

#### Response body

```json
{
  "session_id": "sess-a1b2c3",
  "status": "idle"
}
```

| Field | Type | Notes |
|---|---|---|
| `session_id` | string | Use in all subsequent requests |
| `status` | string | Always `"idle"` on success |

#### Handler flow

```
POST /sessions
  body → StartSessionRequest (Pydantic validation)
  → StartSessionCommand(user_id=body.user_id)
  → container.start_session.execute(command)
  → StartSessionResponseSchema(session_id=..., status=...)
  → HTTP 201
```

#### Error responses

| Exception | Status | Error code | Description |
|---|---|---|---|
| `SessionConflictError` | 409 | `SESSION_CONFLICT` | User already has an active or idle session |
| `UserNotFoundError` | 404 | `USER_NOT_FOUND` | user_id not found in DB |
| `SchoolNotFoundError` | 404 | `SCHOOL_NOT_FOUND` | No school associated with this user |

---

## EP-2 — Process Turn

### `POST /sessions/{session_id}/turns`

**Use case:** `ProcessTurnUseCase` (UC-2)  
**Success status:** `200 OK`

Submits a user message to an active session. Runs the full turn pipeline: intent classification → decision intelligence → knowledge retrieval → response generation → response evaluation. Returns the grounded assistant response (or a safe fallback if quality scores fail).

The session must exist and be in `idle` state. A session transitions to `active` during turn processing and returns to `idle` on completion.

#### Path parameter

| Parameter | Type | Notes |
|---|---|---|
| `session_id` | string | Returned by `POST /sessions` |

#### Request body

```json
{
  "user_id": "u-42",
  "message": "What products do you have for kids aged 5 to 8?"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `user_id` | string | yes | Must match the user who created the session |
| `message` | string | yes | Raw user message text |

#### Response body

```json
{
  "session_id": "sess-a1b2c3",
  "response_text": "We have the Explorer Backpack and the Junior Art Set, both popular with kids in that age range at Lincoln Elementary.",
  "intent": "product_inquiry",
  "is_fallback": false,
  "groundedness_score": 0.91,
  "context_precision_score": 0.85,
  "context_recall_score": 0.78,
  "relevance_score": 0.88
}
```

| Field | Type | Notes |
|---|---|---|
| `session_id` | string | Echo of the path parameter |
| `response_text` | string | The assistant's response. If `is_fallback=true`, this is a safe sorry-I-can't-help message |
| `intent` | string | Classified intent: `product_inquiry` \| `referral_question` \| `general_question` \| `clarification_response` \| `ambiguous` \| `out_of_scope` |
| `is_fallback` | boolean | `true` when quality scores failed the threshold — client may surface a retry prompt |
| `groundedness_score` | float | 0.0–1.0; how well the response is anchored in retrieved evidence |
| `context_precision_score` | float | 0.0–1.0; fraction of retrieved chunks that are actually relevant |
| `context_recall_score` | float | 0.0–1.0; fraction of relevant information that was retrieved |
| `relevance_score` | float | 0.0–1.0; how directly the response addresses the user's question |

#### Handler flow

```
POST /sessions/{session_id}/turns
  path param + body → ProcessTurnRequest (Pydantic validation)
  → ProcessTurnCommand(session_id=session_id, user_id=body.user_id, message=body.message)
  → container.process_turn.execute(command)
  → ProcessTurnResponseSchema(...)
  → HTTP 200
```

#### Error responses

| Exception | Status | Error code | Description |
|---|---|---|---|
| `SessionNotFoundError` | 404 | `SESSION_NOT_FOUND` | No session with this ID |
| `InvalidTurnStateError` | 422 | `INVALID_SESSION_STATE` | Session not in idle state (e.g. still active from a concurrent request) |
| `SessionOwnershipError` | 403 | `OWNERSHIP_MISMATCH` | Requesting user does not own this session |

---

## EP-3 — Close Session

### `DELETE /sessions/{session_id}`

**Use case:** `CloseSessionUseCase` (UC-3)  
**Success status:** `200 OK`

Transitions the session to the `closed` terminal state. Only sessions in `idle` state can be closed — a session mid-turn (`active`) cannot be closed until the turn completes. The requesting user must own the session.

#### Path parameter

| Parameter | Type | Notes |
|---|---|---|
| `session_id` | string | Returned by `POST /sessions` |

#### Request body

```json
{
  "user_id": "u-42"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `user_id` | string | yes | Must match the user who created the session |

#### Response body

```json
{
  "session_id": "sess-a1b2c3",
  "status": "closed"
}
```

| Field | Type | Notes |
|---|---|---|
| `session_id` | string | Echo of the path parameter |
| `status` | string | Always `"closed"` on success |

#### Handler flow

```
DELETE /sessions/{session_id}
  path param + body → CloseSessionRequest (Pydantic validation)
  → CloseSessionCommand(session_id=session_id, user_id=body.user_id)
  → container.close_session.execute(command)
  → CloseSessionResponseSchema(session_id=..., status="closed")
  → HTTP 200
```

#### Error responses

| Exception | Status | Error code | Description |
|---|---|---|---|
| `SessionNotFoundError` | 404 | `SESSION_NOT_FOUND` | No session with this ID |
| `AuthorizationError` | 403 | `AUTHORIZATION_ERROR` | Requesting user does not own this session |
| `InvalidSessionTransitionError` | 409 | `INVALID_STATE_TRANSITION` | Session is in `active` state and cannot be closed yet |

---

## Exception Handler Registry

All handlers are registered at app level in `app.py`. Route handlers never catch exceptions. The standard error envelope is returned for every 4xx response.

**Error envelope:**
```json
{
  "error_code": "SESSION_NOT_FOUND",
  "message": "Session 'sess-a1b2c3' not found."
}
```

| Exception class | Status | Error code | Source module |
|---|---|---|---|
| `SessionConflictError` | 409 | `SESSION_CONFLICT` | `start_session_use_case` |
| `UserNotFoundError` | 404 | `USER_NOT_FOUND` | `start_session_use_case` |
| `SchoolNotFoundError` | 404 | `SCHOOL_NOT_FOUND` | `start_session_use_case` |
| `SessionNotFoundError` | 404 | `SESSION_NOT_FOUND` | `process_turn_use_case`, `close_session_use_case` |
| `InvalidTurnStateError` | 422 | `INVALID_SESSION_STATE` | `process_turn_use_case` |
| `SessionOwnershipError` | 403 | `OWNERSHIP_MISMATCH` | `process_turn_use_case` |
| `AuthorizationError` | 403 | `AUTHORIZATION_ERROR` | `close_session_use_case` |
| `InvalidSessionTransitionError` | 409 | `INVALID_STATE_TRANSITION` | domain (conversation_session) |

---

## Full Request/Response Flow — Per Turn

```
Client
  │
  │  POST /sessions/sess-a1b2c3/turns
  │  { "user_id": "u-42", "message": "..." }
  │
  ▼
router.py — process_turn handler
  │  Pydantic validation (ProcessTurnRequest)
  │  ProcessTurnCommand(session_id, user_id, message)
  │
  ▼
ProcessTurnUseCase.execute(command)                  BC-1
  │  TurnGraph: classify → decision_intelligence → generate → evaluate
  │
  ├──► DecisionIntelligenceAdapter (shell)
  │      ProcessTurnIntelligenceUseCase               BC-2
  │        └──► KnowledgeRetrievalAdapter (shell)
  │               ExecuteRetrievalUseCase             BC-3
  │               (Qdrant vector search)
  │
  ▼
ProcessTurnResponse(session_id, response_text, intent, is_fallback, scores)
  │
  ▼
schemas.py — ProcessTurnResponseSchema
  │
  ▼
HTTP 200 { "session_id": ..., "response_text": ..., ... }
```

---

## Schemas Summary (`schemas.py`)

**Request schemas:**

| Schema | Fields |
|---|---|
| `StartSessionRequest` | `user_id: str` |
| `ProcessTurnRequest` | `user_id: str`, `message: str` |
| `CloseSessionRequest` | `user_id: str` |

**Response schemas:**

| Schema | Fields |
|---|---|
| `StartSessionResponseSchema` | `session_id: str`, `status: str` |
| `ProcessTurnResponseSchema` | `session_id: str`, `response_text: str`, `intent: str`, `is_fallback: bool`, `groundedness_score: float`, `relevance_score: float` |
| `CloseSessionResponseSchema` | `session_id: str`, `status: str` |
| `ErrorResponse` | `error_code: str`, `message: str` |

---

## Scope Boundary

**In scope:**
- Three REST endpoints: `POST /sessions`, `POST /sessions/{session_id}/turns`, `DELETE /sessions/{session_id}`
- Pydantic schemas in `src/shell/api/schemas.py`
- FastAPI app factory in `src/shell/api/app.py` with exception handler registration
- Router in `src/shell/api/router.py`
- ASGI entry point `main.py` at workspace root

**Out of scope:**
- Authentication / JWT — `user_id` is treated as pre-resolved trusted identity
- Rate limiting — not required at prototype scope
- CORS — not required at prototype scope
- GraphQL, CLI, webhook entry points — REST is the sole delivery channel
- Background tasks — the pipeline is synchronous
