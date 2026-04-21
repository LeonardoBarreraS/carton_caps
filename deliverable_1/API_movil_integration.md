# Carton Caps — API Mobile Integration Guide

---

## How it works in one sentence

The mobile app calls three endpoints: one to open a conversation, one per message, and one to close — everything else is handled server-side.

---

## Integration Pattern

```
App launches / user taps Assistant
        │
        ▼
POST /sessions  →  store session_id in memory
        │
        ▼
User types message
        │
        ▼
POST /sessions/{session_id}/turns  →  display response_text
        │
        ▼
Repeat per message
        │
        ▼
User closes chat
        │
        ▼
DELETE /sessions/{session_id}
```

---

## Step-by-Step

**1. Open a session when the user enters the chat screen.**
Call `POST /sessions` with the authenticated `user_id`. Store the returned `session_id` for the duration of the chat. This is a one-time call per conversation — do not repeat it per message.

**2. Send each message and display the response.**
Call `POST /sessions/{session_id}/turns` with `user_id` and the message text. Display `response_text` directly in the chat bubble. The entire AI pipeline runs server-side — the app just sends text and renders text back.

**3. Handle the fallback flag.**
If `is_fallback: true` in the response, the AI pipeline could not produce a confident answer. Show the `response_text` as-is (it is a safe, polite message) and optionally offer a "Try again" button.

**4. Close the session when the user leaves the chat screen.**
Call `DELETE /sessions/{session_id}` on screen exit or app background. This is a fire-and-forget call — no response handling is needed beyond confirming success.

---

## What the App Does NOT Need to Do

- No conversation history management — the server maintains it.
- No intent classification — handled server-side.
- No context tracking — the server accumulates signals across turns automatically.
- No authentication logic in this service — pass the existing `user_id` from the app's current auth session.

---

## Error Handling (minimal)

| Situation | Response |
|-----------|----------|
| `409 SESSION_CONFLICT` on open | An old session exists — call `DELETE` on the old `session_id` first, then retry. |
| `404 SESSION_NOT_FOUND` on turn | Session expired — reopen with `POST /sessions` and resend the message. |
| Network timeout | Retry the turn once; if it fails again, show a generic error. |

---

## Key Implementation Notes

- The `session_id` lives only in memory for the duration of the chat screen — no persistence needed.
- One turn at a time: disable the send button while a turn request is in flight to avoid `INVALID_SESSION_STATE` errors.
- The `user_id` comes directly from the app's existing authentication — no new login flow is required.
