# System Composition
## Carton Caps Conversational Assistant — Phase 7, Shell / Composition Layer

> **Companion document:** system_composition.json  
> **Derived from:** dependency_wiring.json · api_entrypoints.json · use_cases.json  
> **Precondition:** Dependency wiring complete — `build_container()` assembles the full object graph (see `dependency_wiring.md`)

---

## What System Composition Does

System composition is the final step that turns the wired object graph into a running application. Where dependency wiring assembles every component, system composition takes the assembled result and exposes it to the outside world: it registers routes, maps HTTP requests to use cases, maps domain exceptions to HTTP responses, and hands the finished application to the runtime server.

In this system, system composition lives in `src/shell/api/`.

---

## Runtime

**Type:** HTTP server  
**Framework:** FastAPI  
**Server:** uvicorn (ASGI)  
**Mode:** synchronous — no background tasks, no async queues

```
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Auto-generated API documentation is available at `/docs` (Swagger UI) and `/redoc` once the server is running.

---

## Bootstrap Sequence

```
uvicorn main:app
    │
    ▼  Step 1 — ASGI server loads entry point
main.py
    app = create_app()
    │
    ▼  Step 2 — App factory creates FastAPI instance
src/shell/api/app.py  →  create_app()
    app = FastAPI(title="Carton Caps Conversational Assistant")
    │
    ▼  Step 3 — Composition root executed (once, at startup)
src/shell/composition/container.py  →  build_container()
    assembles full object graph
    BC-3 → COMM-2 → BC-2 → COMM-1 → event publisher → BC-1
    returns AppContainer(start_session, process_turn, close_session)
    │
    ▼  Step 4 — Router built and included
src/shell/api/router.py  →  build_router(container)
    binds 3 route handlers to wired use cases
    app.include_router(...)
    │
    ▼  Step 5 — Exception handlers registered (9 handlers)
src/shell/api/app.py
    @app.exception_handler(SessionConflictError)   → 409
    @app.exception_handler(UserNotFoundError)       → 404
    ...  (all 9 registered here)
    │
    ▼  Step 6 — App returned, uvicorn begins serving
app  ←  ready
```

The object graph is assembled exactly **once** at startup. All use case instances are shared across requests. There is no per-request wiring.

---

## Entry Point

**File:** `main.py` (workspace root)

```python
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from shell.api.app import create_app

app = create_app()
```

`src/` is inserted into `sys.path` so all bounded-context packages resolve without installation. The `app` variable is the ASGI application instance consumed by uvicorn.

---

## Route Handlers

Three route handlers are defined in `src/shell/api/router.py`. Each handler builds a use-case Command from the request, calls the use case, and maps the result to a Pydantic response schema. Route handlers contain zero domain logic.

### RH-1 — Start Session

| Attribute | Value |
|---|---|
| Method | `POST` |
| Path | `/sessions` |
| Use case | `StartSessionUseCase` |
| Success status | `201 Created` |
| Request schema | `StartSessionRequest` |
| Response schema | `StartSessionResponse` |

```
POST /sessions
Body: { "user_id": "u-42" }

→ StartSessionCommand(user_id="u-42")
→ StartSessionUseCase.execute(command)
← StartSessionResponse(session_id="sess-a1b2c3", status="idle")
```

Creates and fully initialises a `ConversationSession`. Loads user, school, history, and purchase data. Pre-seeds `DecisionContext` in BC-2. Returns `session_id` the client must use for all subsequent calls.

---

### RH-2 — Process Turn

| Attribute | Value |
|---|---|
| Method | `POST` |
| Path | `/sessions/{session_id}/turns` |
| Use case | `ProcessTurnUseCase` |
| Success status | `200 OK` |
| Request schema | `ProcessTurnRequest` |
| Response schema | `ProcessTurnResponse` |

```
POST /sessions/sess-a1b2c3/turns
Body: { "user_id": "u-42", "message": "which products support school fundraising?" }

→ ProcessTurnCommand(session_id, user_id, message)
→ ProcessTurnUseCase.execute(command)
← ProcessTurnResponse(
     session_id, response_text, intent,
     is_fallback, groundedness_score, relevance_score
   )
```

Runs the full RAG turn pipeline: intent classification → decision intelligence (BC-2) → knowledge retrieval (BC-3) → response generation → evaluation. Returns the grounded assistant response with quality scores.

---

### RH-3 — Close Session

| Attribute | Value |
|---|---|
| Method | `DELETE` |
| Path | `/sessions/{session_id}` |
| Use case | `CloseSessionUseCase` |
| Success status | `200 OK` |
| Request schema | `CloseSessionRequest` |
| Response schema | `CloseSessionResponse` |

```
DELETE /sessions/sess-a1b2c3
Body: { "user_id": "u-42" }

→ CloseSessionCommand(session_id, user_id)
→ CloseSessionUseCase.execute(command)
← CloseSessionResponse(session_id="sess-a1b2c3", status="closed")
```

Transitions the session to the closed terminal state. Only idle sessions can be closed (active → closed is an illegal transition; the domain guard raises before the state change). The requesting user must own the session.

---

## Pydantic Schemas

All request, response, and error types are defined in `src/shell/api/schemas.py`. These are pure API-layer models — they import from nothing outside the API layer.

### Request schemas

| Schema | Fields |
|---|---|
| `StartSessionRequest` | `user_id: str` |
| `ProcessTurnRequest` | `user_id: str`, `message: str` |
| `CloseSessionRequest` | `user_id: str` |

### Response schemas

| Schema | Fields |
|---|---|
| `StartSessionResponse` | `session_id: str`, `status: str` |
| `ProcessTurnResponse` | `session_id: str`, `response_text: str`, `intent: str`, `is_fallback: bool`, `groundedness_score: float`, `relevance_score: float` |
| `CloseSessionResponse` | `session_id: str`, `status: str` |

### Error envelope

```json
{
  "error_code": "SESSION_NOT_FOUND",
  "message": "Session 'sess-a1b2c3' not found."
}
```

---

## Exception Handler Registry

All 9 exception handlers are registered inside `create_app()` before the app is returned. Route handlers never catch use-case exceptions — they bubble up and are intercepted here.

| ID | Exception Class | Source | HTTP Status | Error Code |
|---|---|---|---|---|
| EH-1 | `SessionConflictError` | `start_session_use_case` | 409 | `SESSION_CONFLICT` |
| EH-2 | `UserNotFoundError` | `start_session_use_case` | 404 | `USER_NOT_FOUND` |
| EH-3 | `SchoolNotFoundError` | `start_session_use_case` | 404 | `SCHOOL_NOT_FOUND` |
| EH-4 | `SessionNotFoundError` | `process_turn_use_case` | 404 | `SESSION_NOT_FOUND` |
| EH-5 | `SessionNotFoundError` | `close_session_use_case` | 404 | `SESSION_NOT_FOUND` |
| EH-6 | `SessionOwnershipError` | `process_turn_use_case` | 403 | `OWNERSHIP_MISMATCH` |
| EH-7 | `InvalidTurnStateError` | `process_turn_use_case` | 422 | `INVALID_SESSION_STATE` |
| EH-8 | `AuthorizationError` | `close_session_use_case` | 403 | `AUTHORIZATION_ERROR` |
| EH-9 | `InvalidSessionTransitionError` | domain entity | 409 | `INVALID_STATE_TRANSITION` |

`SessionNotFoundError` is raised by two different use cases. Both are aliased separately when imported into `app.py` (`TurnSessionNotFoundError`, `CloseSessionNotFoundError`) to avoid name collision — both map to the same `SESSION_NOT_FOUND` error code and 404 status.

---

## Request Flow

Every HTTP request travels inward through the architecture. Nothing in the API layer reaches downward past the use case boundary.

```
HTTP request
    ↓
uvicorn (ASGI server)
    ↓
FastAPI routing (method + path matching)
    ↓
router.py handler function
    ↓  Pydantic structural validation
    ↓  build Command from request fields
    ↓
UseCase.execute(command)
    ↓  domain objects, adapters, repositories
    ↓  cross-context calls via port interfaces
    ↓
UseCase returns Response dataclass
    ↓
router.py maps Response fields → Pydantic response schema
    ↓
FastAPI serializes to JSON
    ↓
HTTP response

── On exception ──────────────────────────────────────────────
UseCase raises domain exception
    ↓
app.py exception handler intercepts
    ↓
Returns JSONResponse with ErrorResponse envelope
```

---

## Shell API Module Structure

```
src/shell/api/
├── __init__.py
├── app.py        FastAPI factory — create_app(), exception handlers (EH-1 to EH-9)
├── router.py     3 route handlers — build_router(container) → APIRouter
└── schemas.py    StartSessionRequest/Response, ProcessTurnRequest/Response,
                  CloseSessionRequest/Response, ErrorResponse

main.py           ASGI entry point — app = create_app()  (workspace root)
```

---

## Scope Boundary

**In scope:**
- FastAPI app factory (`create_app`) and exception handler registration
- Three route handlers (POST /sessions, POST turns, DELETE session)
- Pydantic request/response/error schemas
- ASGI entry point (`main.py`)

**Out of scope:**
- Authentication / JWT validation — `user_id` is trusted at prototype scope
- Rate limiting — not required at prototype scale
- CORS configuration — no browser client at prototype scope
- Health check endpoint — not required by the deliverable
- Background tasks, webhooks, GraphQL, CLI — REST is the sole delivery channel

---

## Composition Rules

**Must:**
- `build_container()` called once inside `create_app()` — never at module level, never per-request
- All exception handlers registered before `create_app()` returns
- Route handlers receive the container via `build_router(container)` — no global state
- API layer imports only: `AppContainer`, use-case command/response classes, Pydantic schemas

**Must not:**
- No domain logic in route handlers or app factory
- No repository, adapter, or infrastructure class imported in `src/shell/api/`
- No try/except blocks in route handlers — exceptions bubble to app-level handlers
- No per-request object instantiation — graph is immutable after startup
