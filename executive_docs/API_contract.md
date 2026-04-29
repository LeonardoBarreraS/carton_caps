# Carton Caps Conversational Assistant — API Contract
## Conversation Management

**Version 1.0 | April 2026**

---

## Overview

This document defines the REST API contract for creating and maintaining conversations between a user and the Carton Caps Conversational Assistant. Three endpoints cover the full lifecycle of a conversation session.

**Base URL:** `http://<host>:8000`

| Endpoint | Method | Path | Purpose |
|----------|--------|------|---------|
| Start Session | `POST` | `/sessions` | Open a new conversation |
| Process Turn | `POST` | `/sessions/{session_id}/turns` | Send a message, receive a response |
| Close Session | `DELETE` | `/sessions/{session_id}` | Close the conversation |

---

## Session Lifecycle

A session moves through the following states. Only **one active or idle session per user** is allowed at a time.

```
created  →  initializing  →  idle  ⇄  active  →  closed
```

The client receives a `session_id` from `POST /sessions` and must include it in every subsequent call. Once closed, a session cannot be reopened.

---

## Endpoints

---

### POST /sessions — Start Session

Opens a new conversation. Loads the user profile, associated school, and conversation history. Returns a `session_id` to use in all subsequent requests.

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | string | Yes | Pre-resolved trusted user identifier |

```json
{
  "user_id": "u-42"
}
```

**Response — 201 Created**

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Use in all subsequent requests |
| `status` | string | Always `"idle"` on success |

```json
{
  "session_id": "sess-a1b2c3",
  "status": "idle"
}
```

**Errors**

| HTTP | Error Code | Cause |
|------|-----------|-------|
| 409 | `SESSION_CONFLICT` | User already has an open session |
| 404 | `USER_NOT_FOUND` | `user_id` does not exist |
| 404 | `SCHOOL_NOT_FOUND` | No school linked to this user |

---

### POST /sessions/{session_id}/turns — Process Turn

Sends a user message to an open session and receives a grounded assistant response. Runs the full AI pipeline: intent classification → context accumulation → knowledge retrieval → response generation → quality evaluation. Returns a safe fallback message if quality checks fail.

**Path parameter**

| Parameter | Type | Description |
|-----------|------|-------------|
| `session_id` | string | Returned by `POST /sessions` |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | string | Yes | Must match the user who opened the session |
| `message` | string | Yes | Raw user message text |

```json
{
  "user_id": "u-42",
  "message": "What healthy snacks do you have for picky kids?"
}
```

**Response — 200 OK**

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Echo of the path parameter |
| `response_text` | string | Assistant answer. If `is_fallback=true`, this is a safe sorry-message |
| `intent` | string | Classified intent (see values below) |
| `is_fallback` | boolean | `true` when quality scores failed — client may show a retry prompt |
| `groundedness_score` | float | 0.0–1.0: how well the response is anchored in retrieved evidence |
| `context_precision_score` | float | 0.0–1.0: fraction of retrieved chunks that are actually relevant |
| `context_recall_score` | float | 0.0–1.0: fraction of relevant content that was retrieved |
| `relevance_score` | float | 0.0–1.0: how directly the response addresses the user question |

**Intent values**

| Value | Meaning |
|-------|---------|
| `product_inquiry` | User is looking for product recommendations |
| `referral_question` | User is asking about the referral program |
| `general_question` | General question about the platform |
| `clarification_response` | User is answering a clarifying question the assistant asked |
| `ambiguous` | Message has mixed or unclear signals |
| `out_of_scope` | Message unrelated to shopping, products, or fundraising |

```json
{
  "session_id": "sess-a1b2c3",
  "response_text": "For picky kids, the Garden Crunch Mix and Sunny Os are great fits — and both support Lincoln Elementary.",
  "intent": "product_inquiry",
  "is_fallback": false,
  "groundedness_score": 0.91,
  "context_precision_score": 0.85,
  "context_recall_score": 0.78,
  "relevance_score": 0.88
}
```

**Errors**

| HTTP | Error Code | Cause |
|------|-----------|-------|
| 404 | `SESSION_NOT_FOUND` | No session with this ID |
| 403 | `OWNERSHIP_MISMATCH` | `user_id` does not match the session owner |
| 422 | `INVALID_SESSION_STATE` | Session is not in `idle` state (e.g. concurrent request) |

---

### DELETE /sessions/{session_id} — Close Session

Closes a session. Only sessions in `idle` state (not mid-turn) can be closed. The requesting user must own the session.

**Path parameter**

| Parameter | Type | Description |
|-----------|------|-------------|
| `session_id` | string | Returned by `POST /sessions` |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | string | Yes | Must match the user who opened the session |

```json
{
  "user_id": "u-42"
}
```

**Response — 200 OK**

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Echo of the path parameter |
| `status` | string | Always `"closed"` on success |

```json
{
  "session_id": "sess-a1b2c3",
  "status": "closed"
}
```

**Errors**

| HTTP | Error Code | Cause |
|------|-----------|-------|
| 404 | `SESSION_NOT_FOUND` | No session with this ID |
| 403 | `AUTHORIZATION_ERROR` | `user_id` does not match the session owner |
| 409 | `INVALID_STATE_TRANSITION` | Session is still `active` (turn in progress) |

---

## Error Response Format

All error responses use a consistent JSON envelope:

```json
{
  "error_code": "SESSION_NOT_FOUND",
  "detail": "No session found with id: sess-xyz"
}
```

---

## Typical Conversation Flow

```
1.  POST /sessions                          →  receive session_id
2.  POST /sessions/{session_id}/turns       →  send message, receive response
3.  POST /sessions/{session_id}/turns       →  repeat for each message
4.  DELETE /sessions/{session_id}           →  close conversation
```
