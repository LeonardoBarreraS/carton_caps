# Repository Generator — Carton Caps Conversational Assistant

**Phase**: 6 — Infrastructure Layer Design  
**Task**: Repository Generator  
**Version**: 1.0

---

## Overview

This document defines all repository interfaces and their infrastructure implementations for the Carton Caps Conversational Assistant. Repositories are the persistence boundary between the domain model and storage technology.

All 8 repository interfaces are defined in `domain/ports/` layers — they belong to the domain, not the infrastructure. All 9 implementations are infrastructure adapters that translate domain objects to and from their storage format.

> All repository code was materialized during Phase 6 Task 1 (Adapter Generator). This document provides the formal repository design record.

---

## Repository Categories

| Category | Description | Count |
|---|---|---|
| **Aggregate Repository** | Full lifecycle (save/load) of a mutable aggregate root | 2 |
| **Append Repository** | Append-only write + chronological query read | 1 |
| **Read-Only Repository** | Query only — fixture data managed externally, never written | 3 |
| **Search Repository** | Semantic similarity search via Qdrant vector store | 2 |

---

## Interface-to-Implementation Summary

| ID | Interface | Implementation | Adapter | Storage | BC |
|---|---|---|---|---|---|
| REPO-1 | `IConversationSessionRepository` | `InMemoryConversationSessionRepository` | ADAPT-9 | Python dict | BC-1 |
| REPO-2 | `IConversationHistoryRepository` | `SQLiteConversationHistoryRepository` *(primary)* | ADAPT-16 | SQLite `Conversation_History` | BC-1 |
| REPO-2 | `IConversationHistoryRepository` | `InMemoryConversationHistoryRepository` *(dev alt)* | ADAPT-10 | Python defaultdict | BC-1 |
| REPO-3 | `IUserRepository` | `SQLiteUserRepository` | ADAPT-11 | SQLite `Users` | BC-1 |
| REPO-4 | `ISchoolRepository` | `SQLiteSchoolRepository` | ADAPT-12 | SQLite `Schools`+`Users` JOIN | BC-1 |
| REPO-5 | `IPurchaseHistoryRepository` | `SQLitePurchaseHistoryRepository` | ADAPT-13 | SQLite `Purchase_History`+`Products` JOIN | BC-1 |
| REPO-6 | `IDecisionContextRepository` | `InMemoryDecisionContextRepository` | ADAPT-14 | Python dict | BC-2 |
| REPO-7 | `IProductRepository` | `QdrantProductRepository` | ADAPT-7 | Qdrant `product_catalog` | BC-3 |
| REPO-8 | `IReferralRuleRepository` | `QdrantReferralRuleRepository` | ADAPT-8 | Qdrant `referral_program_rules` | BC-3 |

---

## Repositories

---

### REPO-1 — ConversationSessionRepository

**Category**: Aggregate Repository  
**Aggregate**: `ConversationSession` — aggregate root of BC-1; full session state machine  
**Bounded Context**: BC-1 `conversation_management`

#### Interface

**`IConversationSessionRepository`**  
`src/conversation_management/domain/ports/i_conversation_session_repository.py`

| Method | Signature | Purpose |
|---|---|---|
| `save` | `save(session: ConversationSession) -> None` | Persist or update session after each state transition |
| `find_by_id` | `find_by_id(session_id: str) -> Optional[ConversationSession]` | Load session by ID for turn processing or closure |
| `find_active_by_user_id` | `find_active_by_user_id(user_id: str) -> Optional[ConversationSession]` | Enforce one-active-session-per-user guard (INV-CS-7) |

#### Implementation — `InMemoryConversationSessionRepository` (ADAPT-9)

`src/conversation_management/infrastructure/repositories/in_memory_conversation_session_repository.py`

| Property | Value |
|---|---|
| Storage | `dict[str, ConversationSession]` keyed by `session_id` |
| Scope | Process lifetime — session state is transient |
| `find_active_by_user_id` | Linear scan; filters `session.user_id == user_id AND session.status in {ACTIVE, IDLE}` |

**Rationale**: Session state is per-turn scoped and requires zero-latency access across the multi-turn pipeline. No durability required for prototype scope.

#### Use Cases Served

| Use Case | Operations |
|---|---|
| UC-1 `StartSessionUseCase` | `find_active_by_user_id` (INV-CS-7 guard) → `save` (after `complete_initialization`) |
| UC-2 `ProcessTurnUseCase` | `find_by_id` (load before TurnGraph) → `save` (after `complete_turn` — post-graph action) |
| UC-3 `CloseSessionUseCase` | `find_by_id` (load) → `save` (after `close` — terminal state) |

**Invariants Supported**: INV-CS-7, INV-CS-2

---

### REPO-2 — ConversationHistoryRepository

**Category**: Append Repository  
**Aggregate**: `ConversationHistory` entity — append-only conversation log  
**Bounded Context**: BC-1 `conversation_management`

#### Interface

**`IConversationHistoryRepository`**  
`src/conversation_management/domain/ports/i_conversation_history_repository.py`

| Method | Signature | Purpose |
|---|---|---|
| `append` | `append(entry: ConversationHistory) -> None` | Append a single history entry (user or assistant). Called twice per successful turn. |
| `find_by_user_id` | `find_by_user_id(user_id: str) -> list[ConversationHistory]` | Return all entries for a user, ordered chronologically |

#### Primary Implementation — `SQLiteConversationHistoryRepository` (ADAPT-16)

`src/conversation_management/infrastructure/repositories/sqlite_conversation_history_repository.py`

| Property | Value |
|---|---|
| Storage | SQLite `carton_caps_data.sqlite` — `Conversation_History` table |
| Schema migration | `__init__` adds `history_id` (TEXT) and `session_id` (TEXT) columns via `ALTER TABLE IF NOT EXISTS`. Existing rows receive empty-string defaults — backward compatible. |

**Persistence Mapping**:

| Domain Field | DB Column | Notes |
|---|---|---|
| `history_id` | `history_id` | uuid4; `legacy-{id}` for pre-migration rows |
| `user_id` | `user_id` | int in DB; str in domain |
| `session_id` | `session_id` | empty string for legacy rows |
| `message` | `message` | plain text |
| `sender` | `sender` | `SenderType.value` translated via `_DB_SENDER_MAP`: `'user'`→`'bot'` (satisfies `CHECK(sender IN ('user', 'bot'))`) |
| `timestamp` | `timestamp` | ISO-8601 UTC string |

**Write Mapping**: `sender` translated via `_DB_SENDER_MAP` before insert — `'user'`→`'user'`, `'assistant'`→`'bot'` — to satisfy the legacy CHECK constraint on the `Conversation_History` table.

**Read Mapping**: `sender` decoded via `_SENDER_MAP` (`'user'`→USER, `'assistant'`/`'bot'`→ASSISTANT, unknown→USER); `timestamp` parsed to UTC-aware datetime with `now(UTC)` fallback; `history_id` falls back to `legacy-{row.id}`.

#### Development Variant — `InMemoryConversationHistoryRepository` (ADAPT-10)

`src/conversation_management/infrastructure/repositories/in_memory_conversation_history_repository.py`

| Property | Value |
|---|---|
| Storage | `defaultdict(list[ConversationHistory])` keyed by `user_id` |
| Scope | Process lifetime — history lost on restart |
| Use | Unit testing and local development without a SQLite file |

#### Use Cases Served

| Use Case | Operations |
|---|---|
| UC-1 `StartSessionUseCase` | `find_by_user_id` — load prior history for session context check |
| UC-2 `ProcessTurnUseCase` (via `persist_turn` node) | `append` × 2 — user message entry + assistant response entry |

**Invariants Supported**: INV-WF-1 (turn persisted on completion)

> **Design note**: Conversation history is append-only — no update or delete method exists. Two entries are written per successful turn (user message + assistant response). The full history is loaded in `ProcessTurnUseCase` via `find_by_user_id()` and mapped to `conversation_history: list[dict]` for injection into `TurnGraph` and all LLM calls (Proposal B — explicit history injection).

---

### REPO-3 — UserRepository

**Category**: Read-Only Repository  
**Value Object**: `User` — external reference value object; carries `user_id`, `school_id`, and `name`. Immutable reference to User entity in external Auth BC — never created or mutated here.  
**Bounded Context**: BC-1 `conversation_management`

#### Interface

**`IUserRepository`**  
`src/conversation_management/domain/ports/i_user_repository.py`

| Method | Signature | Purpose |
|---|---|---|
| `find_by_id` | `find_by_id(user_id: str) -> Optional[User]` | Validate user existence before session creation (INV-CS-6) |

#### Implementation — `SQLiteUserRepository` (ADAPT-11)

`src/conversation_management/infrastructure/repositories/sqlite_user_repository.py`

| Property | Value |
|---|---|
| Storage | SQLite `carton_caps_data.sqlite` — `Users` table (read-only) |
| Query | `SELECT id, school_id, name FROM Users WHERE id = ?` |
| ID cast | `user_id` string → int for SQL; returns `None` for non-numeric input |

**Persistence Mapping**: `id` → `User.user_id (str)`, `school_id` → `User.school_id (str)`, `name` → `User.name (str)`

#### Use Cases Served

| Use Case | Operations |
|---|---|
| UC-1 `StartSessionUseCase` | `find_by_id` — raise `NotFoundError` if user does not exist (INV-CS-6) |
| UC-2 `ProcessTurnUseCase` | `find_by_id` — load `User.name` for LLM personalization before graph invocation |

**Invariants Supported**: INV-CS-6

---

### REPO-4 — SchoolRepository

**Category**: Read-Only Repository  
**Value Object**: `School` — external reference value object; carries `school_id`, `name`, `address`. Immutable reference to School entity in external Master Data BC — never created or mutated here.  
**Bounded Context**: BC-1 `conversation_management`

#### Interface

**`ISchoolRepository`**  
`src/conversation_management/domain/ports/i_school_repository.py`

| Method | Signature | Purpose |
|---|---|---|
| `find_by_user_id` | `find_by_user_id(user_id: str) -> Optional[School]` | Resolve the school associated with a user for DecisionContext seeding (INV-CS-3) |

#### Implementation — `SQLiteSchoolRepository` (ADAPT-12)

`src/conversation_management/infrastructure/repositories/sqlite_school_repository.py`

| Property | Value |
|---|---|
| Storage | SQLite `carton_caps_data.sqlite` — `Schools` + `Users` JOIN (read-only) |
| Query | `SELECT s.id, s.name, s.address FROM Schools s JOIN Users u ON u.school_id = s.id WHERE u.id = ?` |
| ID cast | `user_id` string → int for SQL |

**Persistence Mapping**: `s.id` → `School.school_id (str)`, `s.name` → `School.name`, `s.address` → `School.address`

#### Use Cases Served

| Use Case | Operations |
|---|---|
| UC-1 `StartSessionUseCase` | `find_by_user_id` — raise `NotFoundError` if school not found; `school_name` forwarded in `PreSeedContextDTO` to BC-2 |

**Invariants Supported**: INV-CS-3, INV-DC-2

> **Design note**: School is the fundraising anchor of the entire conversation. Its `school_id` and `name` are forwarded to BC-2 via `PreSeedContextDTO` during session initialization. The repository resolves school indirectly through the user's `school_id` foreign key — there is no direct school_id lookup from the application layer.

---

### REPO-5 — PurchaseHistoryRepository

**Category**: Read-Only Repository  
**Aggregate**: PurchaseHistory (raw `list[dict]` — intentionally no domain entity wrapper)  
**Bounded Context**: BC-1 `conversation_management`

#### Interface

**`IPurchaseHistoryRepository`**  
`src/conversation_management/domain/ports/i_purchase_history_repository.py`

| Method | Signature | Purpose |
|---|---|---|
| `find_by_user_id` | `find_by_user_id(user_id: str) -> list[dict]` | Return purchase records as raw dicts for BC-2 signal seeding. Empty list if none. |

#### Implementation — `SQLitePurchaseHistoryRepository` (ADAPT-13)

`src/conversation_management/infrastructure/repositories/sqlite_purchase_history_repository.py`

| Property | Value |
|---|---|
| Storage | SQLite `carton_caps_data.sqlite` — `Purchase_History` + `Products` JOIN (read-only) |
| Query | `SELECT ph.id, ph.product_id, p.name AS product_name, ph.quantity, ph.purchased_at FROM Purchase_History ph JOIN Products p ON p.id = ph.product_id WHERE ph.user_id = ? ORDER BY ph.purchased_at DESC` |
| Return type | `list[dict]` — keys: `id`, `product_id`, `product_name`, `quantity`, `purchased_at` |

#### Use Cases Served

| Use Case | Operations |
|---|---|
| UC-1 `StartSessionUseCase` | `find_by_user_id` — optional signal; empty list handled gracefully; dicts forwarded in `PreSeedContextDTO.purchase_signals` to BC-2 |

> **Design note**: `list[dict]` is intentional — purchase records cross the BC-1→BC-2 boundary as primitive signal seeds in `PreSeedContextDTO`. There is no purchase domain entity in BC-1 and creating one would add unnecessary coupling without domain benefit.

---

### REPO-6 — DecisionContextRepository

**Category**: Aggregate Repository  
**Aggregate**: `DecisionContext` — aggregate root of BC-2; stateful preference signal accumulator  
**Bounded Context**: BC-2 `decision_intelligence`

#### Interface

**`IDecisionContextRepository`**  
`src/decision_intelligence/domain/ports/i_decision_context_repository.py`

| Method | Signature | Purpose |
|---|---|---|
| `save` | `save(context: DecisionContext) -> None` | Persist or update DecisionContext after each turn (post-graph action) and at session initialization |
| `find_by_session_id` | `find_by_session_id(session_id: str) -> Optional[DecisionContext]` | Load context before `DecisionIntelligenceSubgraph` invocation |

#### Implementation — `InMemoryDecisionContextRepository` (ADAPT-14)

`src/decision_intelligence/infrastructure/repositories/in_memory_decision_context_repository.py`

| Property | Value |
|---|---|
| Storage | `dict[str, DecisionContext]` keyed by `session_id` |
| Scope | Process lifetime — one entry per active session |
| Save strategy | Last-write-wins overwrite of the session-scoped key |

**Rationale**: DecisionContext accumulates signals within a session. Session state is transient in the prototype — cross-restart persistence is not required. In-memory ensures zero-latency access across all turns.

#### Use Cases Served

| Use Case | Operations |
|---|---|
| UC-4 `PreSeedContextUseCase` | `save` — create and persist initial DecisionContext with school anchor and purchase signals |
| UC-5 `ProcessTurnIntelligenceUseCase` | `find_by_session_id` (load before subgraph) → `save` (persist updated context — post-graph action) |

**Invariants Supported**: INV-DC-2, INV-DC-5, INV-CS-5

---

### REPO-7 — ProductRepository

**Category**: Search Repository  
**Aggregate**: `Product` — read-only domain entity carrying product facts  
**Bounded Context**: BC-3 `knowledge_retrieval`

#### Interface

**`IProductRepository`**  
`src/knowledge_retrieval/domain/ports/i_product_repository.py`

| Method | Signature | Purpose |
|---|---|---|
| `search` | `search(query_text: str, top_k: int) -> list[Product]` | Semantic similarity search over `product_catalog`; returns top_k products by cosine similarity |

#### Implementation — `QdrantProductRepository` (ADAPT-7)

`src/knowledge_retrieval/infrastructure/repositories/qdrant_product_repository.py`

| Property | Value |
|---|---|
| Storage | Qdrant `product_catalog` collection |
| Embedding model | `text-embedding-3-small` (same as ingestion — guarantees vector space alignment) |
| Similarity | Cosine |
| Vector size | 1536 |
| Constructor | `qdrant_url: str`, `openai_client: OpenAI`, `collection_name: str = 'product_catalog'`, `qdrant_api_key: str | None = None` |

**Persistence Mapping** (Qdrant payload → `Product` domain fields):

| Qdrant Payload | Domain Field | Notes |
|---|---|---|
| `payload.product_id` or `payload.doc_id` or `str(point.id)` | `product_id` | Fallback chain |
| `payload.name` | `name` | |
| `payload.category` | `category` | |
| `payload.brand` | `brand` | |
| `payload.text` | `description` | Raw document text chunk |
| `{}` | `attributes` | Not stored in current ingestion schema |

Write side: `QdrantVectorStoreWriter` (ADAPT-1) — offline ingestion pipeline only.

#### Use Cases Served

| Use Case | Operations |
|---|---|
| UC-6 `ExecuteRetrievalUseCase` | `search(query_text, top_k)` when `source_target == 'product_catalog'` |

**Invariants Supported**: INV-AR-2, INV-WF-3

---

### REPO-8 — ReferralRuleRepository

**Category**: Search Repository  
**Aggregate**: `ReferralRule` — read-only domain entity carrying referral program rule facts  
**Bounded Context**: BC-3 `knowledge_retrieval`

#### Interface

**`IReferralRuleRepository`**  
`src/knowledge_retrieval/domain/ports/i_referral_rule_repository.py`

| Method | Signature | Purpose |
|---|---|---|
| `search` | `search(query_text: str, top_k: int) -> list[ReferralRule]` | Semantic similarity search over `referral_program_rules`; returns top_k rules by cosine similarity |

#### Implementation — `QdrantReferralRuleRepository` (ADAPT-8)

`src/knowledge_retrieval/infrastructure/repositories/qdrant_referral_rule_repository.py`

| Property | Value |
|---|---|
| Storage | Qdrant `referral_program_rules` collection |
| Embedding model | `text-embedding-3-small` (same as ingestion) |
| Similarity | Cosine |
| Vector size | 1536 |
| Constructor | `qdrant_url: str`, `openai_client: OpenAI`, `collection_name: str = 'referral_program_rules'`, `qdrant_api_key: str | None = None` |

**Persistence Mapping** (Qdrant payload → `ReferralRule` domain fields):

| Qdrant Payload | Domain Field | Notes |
|---|---|---|
| `payload.doc_id` or `str(point.id)` | `rule_id` | |
| `payload.label` | `title` | |
| `payload.text` | `description` | Raw document text chunk |
| `payload.label` via `_LABEL_TO_RULE_TYPE` | `rule_type` | `eligibility`→ELIGIBILITY, `bonus`→BONUS, `invitation`→INVITATION, `requirement`→REQUIREMENT; defaults to ELIGIBILITY |

Write side: `QdrantVectorStoreWriter` (ADAPT-1) — offline ingestion pipeline only.

#### Use Cases Served

| Use Case | Operations |
|---|---|
| UC-6 `ExecuteRetrievalUseCase` | `search(query_text, top_k)` when `source_target == 'referral_program_rules'` |

**Invariants Supported**: INV-AR-3, INV-WF-3

---

## Storage Summary

### SQLite — `carton_caps_data.sqlite`

| Table | Repository | Access | Notes |
|---|---|---|---|
| `Conversation_History` | REPO-2 | Read + Write (append) | Schema migration on first use: adds `history_id`, `session_id` columns |
| `Users` | REPO-3 | Read-only | Pre-existing fixture data |
| `Schools` + `Users` JOIN | REPO-4 | Read-only | Pre-existing fixture data |
| `Purchase_History` + `Products` JOIN | REPO-5 | Read-only | Pre-existing fixture data |

### Qdrant Vector Store

| Collection | Repository | Access | Write Side |
|---|---|---|---|
| `product_catalog` | REPO-7 | Read-only (runtime search) | `QdrantVectorStoreWriter` (ADAPT-1) — offline ingestion |
| `referral_program_rules` | REPO-8 | Read-only (runtime search) | `QdrantVectorStoreWriter` (ADAPT-1) — offline ingestion |

> Both search repositories use `text-embedding-3-small` — the same model used during ingestion — to guarantee correct cosine distance comparisons.

### In-Process Python

| Repository | Storage | Scope |
|---|---|---|
| REPO-1 `ConversationSession` | `dict[session_id, ConversationSession]` | Process lifetime |
| REPO-6 `DecisionContext` | `dict[session_id, DecisionContext]` | Process lifetime |
| REPO-2 (dev alt) | `defaultdict(list)` keyed by `user_id` | Process lifetime |

---

## Folder Structure

```
src/
  conversation_management/
    domain/ports/                                  ← BC-1 repository interfaces
      i_conversation_session_repository.py
      i_conversation_history_repository.py
      i_user_repository.py
      i_school_repository.py
      i_purchase_history_repository.py
    infrastructure/repositories/                   ← BC-1 implementations
      in_memory_conversation_session_repository.py
      sqlite_conversation_history_repository.py    ← primary
      in_memory_conversation_history_repository.py ← dev/test variant
      sqlite_user_repository.py
      sqlite_school_repository.py
      sqlite_purchase_history_repository.py

  decision_intelligence/
    domain/ports/                                  ← BC-2 repository interfaces
      i_decision_context_repository.py
    infrastructure/repositories/                   ← BC-2 implementations
      in_memory_decision_context_repository.py

  knowledge_retrieval/
    domain/ports/                                  ← BC-3 repository interfaces
      i_product_repository.py
      i_referral_rule_repository.py
    infrastructure/repositories/                   ← BC-3 implementations
      qdrant_product_repository.py
      qdrant_referral_rule_repository.py
```

---

## Dependency Direction

```
Application layer
      │  depends on  ↓
Domain interfaces (IConversationSessionRepository, IDecisionContextRepository, …)
      │  implemented by  ↓
Infrastructure implementations (InMemoryConversationSessionRepository, SQLiteUserRepository, QdrantProductRepository, …)
```

Domain and application layers never import infrastructure. The shell composition root (`src/shell/composition/container.py`) is the only module that instantiates implementations and wires them to use cases via constructor injection.
