# Carton Caps Conversational Assistant — Executive Flow Overview

> **Audience:** C-level / non-technical leadership
> **Purpose:** A single-page glance at everything the system does across the two moments a user interacts with the app — who does what, in what order, and what happens when something needs a second look.

---

## The Two Moments at a Glance

| | Moment A | Moment B |
|---|---|---|
| **Trigger** | User opens the app | User sends a message |
| **Owner** | BC1 hands off to BC2 | BC1 orchestrates BC2, which calls BC3 |
| **Outcome** | A ready, personalized conversation environment | A grounded, quality-verified answer |

---

---

# MOMENT A — START SESSION

```
USER OPENS THE APP
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  UC-1: START SESSION  (BC1 — Conversation Management)   │
│                                                         │
│  1. Guard: Is there already an open session?            │
│  2. Load: User identity, school, history, purchases     │
│  3. Create the conversation slot  →  status: CREATED    │
│  4. Hand off to BC2 ────────────────────────────────┐   │
│  5. Mark session ready  →  status: IDLE             │   │
└─────────────────────────────────────────────────────┼───┘
                                                      │
                                                      ▼
              ┌───────────────────────────────────────────────────────┐
              │  UC-4: PRE-SEED CONTEXT  (BC2 — Decision Intelligence) │
              │                                                        │
              │  1. Create the user's intelligence profile             │
              │  2. Plant the school as a permanent anchor             │
              │  3. Seed any purchase history as early signals         │
              └───────────────────────────────────────────────────────┘
                                                      │
                                                      ▼
                                        SESSION READY — IDLE
                                    (User can send first message)
```

**Session states:** `CREATED` → `INITIALIZING` → `IDLE`

---

---

# MOMENT B — CONVERSATIONAL TURN

```
USER SENDS A MESSAGE
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│  UC-2: PROCESS TURN  (BC1 — Conversation Management)         │
│                                                              │
│  Guards: session exists · session is IDLE · owner matches   │
│  Loads: conversation history · user name · school name      │
│  Marks session ACTIVE  →  runs the Turn Pipeline below      │
│  On finish: marks IDLE · saves · returns answer to user     │
│  On error:  rolls back to IDLE · no data lost               │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌═══════════════════════════════════════════════════════════════════════════════╗
║  TURN PIPELINE  (TurnGraph — runs inside UC-2)                               ║
║                                                                               ║
║  STEP 1 ── Classify Intent                                                    ║
║            What does the user want?                                           ║
║                                                                               ║
║            ┌────────────────────────────────┬─────────────────────────────┐  ║
║            │  OUT OF SCOPE / GENERAL        │  AMBIGUOUS                  │  ║
║            │  → Generate Redirect           │  → Generate Clarification   │  ║
║            │    (no search, no BC2)         │    (no search, no BC2)      │  ║
║            └────────────────┬───────────────┴─────────────────────────────┘  ║
║                             │  PRODUCT INQUIRY / REFERRAL / CLARIFICATION     ║
║                             ▼                                                 ║
║  STEP 2 ── Call BC2 — Decision Intelligence  (UC-5)                          ║
║            (full intelligence pipeline — see below)                          ║
║                                                                               ║
║            ├─ BC2 returns: CLARIFICATION NEEDED                               ║
║            │    → Generate Clarification  ──────────────────────────┐        ║
║            │                                                         │        ║
║            └─ BC2 returns: EVIDENCE RETRIEVED                        │        ║
║                 │                                                    │        ║
║  STEP 3 ──      ▼  Generate Response                                 │        ║
║                 │   (grounded in retrieved evidence)                 │        ║
║                 │                                                    │        ║
║  STEP 4 ──      ▼  Evaluate Response Quality ◄── TWO CHECKS HERE    │        ║
║                 │                                                    │        ║
║                 │   CHECK 1 — GROUNDEDNESS                          │        ║
║                 │   Is every claim traceable to retrieved evidence?  │        ║
║                 │                                                    │        ║
║                 │   CHECK 2 — RELEVANCE                              │        ║
║                 │   Does the answer actually address the question?   │        ║
║                 │                                                    │        ║
║                 │   ┌─ BOTH PASS ──────────────────────────────┐    │        ║
║                 │   │  Deliver the grounded answer             │    │        ║
║                 │   │                                          │    │        ║
║                 │   └─ EITHER FAILS ─► Generate Partial Answer │    │        ║
║                 │                      (use available evidence) │    │        ║
║                 │                                              │    │        ║
║  STEP 5 ── ALL PATHS ◄───────────────────────────────────────-┘◄───┘        ║
║            Save History  →  Return answer to user                            ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## Inside BC2 — Decision Intelligence Pipeline

> Runs entirely within Step 2 of the Turn Pipeline above. BC2 does the thinking so BC1 can deliver a precise answer.

```
┌═══════════════════════════════════════════════════════════════════════════════╗
║  DECISION INTELLIGENCE PIPELINE  (DecisionIntelligenceSubgraph — UC-5)      ║
║                                                                               ║
║  STEP A ── Extract Signals                                                    ║
║            Pull preferences from the user's message                          ║
║            (e.g. "picky kids", "healthy", "breakfast cereal")                ║
║                 │                                                             ║
║  STEP B ──      ▼  Update Intelligence Profile                                ║
║                    Add signals — profile grows: EMPTY→PARTIAL→READY→ENRICHED ║
║                 │                                                             ║
║  STEP C ──      ▼  Evaluate Readiness                                         ║
║                                                                               ║
║            REFERRAL QUESTION?                                                 ║
║            └─ Skip readiness check. The question itself is the query.        ║
║               → Go to STEP D                                                  ║
║                                                                               ║
║            PRODUCT INQUIRY?                                                   ║
║            ├─ Has at least one useful preference signal?                      ║
║            │   YES → Go to STEP D                                             ║
║            │   NO  → Save original intent · Return CLARIFICATION NEEDED      ║
║            │          ↓                                                       ║
║            │         User answers the clarification question                  ║
║            │          ↓                                                       ║
║            │         Re-enter at STEP C with saved intent                    ║
║            │         (loop repeats until signals arrive)                      ║
║                                                                               ║
║  STEP D ── Build Search Query                                                 ║
║            Combine user message + accumulated signals into a precise query   ║
║            Route: Product Inquiry → Product Catalog                          ║
║                   Referral Question → Referral Program Rules                 ║
║                 │                                                             ║
║  STEP E ──      ▼  Execute Retrieval  (calls BC3 — UC-6)                     ║
║                    Search the correct knowledge base                          ║
║                    Return: top matching content chunks                        ║
║                 │                                                             ║
║  STEP F ──      ▼  Evaluate Evidence Quality ◄── TWO CHECKS HERE             ║
║                                                                               ║
║            CHECK 1 — RECALL                                                   ║
║            Did the search return all the content needed to answer?           ║
║            (Is important information missing from the results?)              ║
║                                                                               ║
║            CHECK 2 — PRECISION                                                ║
║            Is everything returned actually relevant?                          ║
║            (Are there off-topic results mixed in?)                            ║
║                                                                               ║
║            ├─ QUALITY PASSES                                                  ║
║            │   → Return evidence to BC1  (Turn Pipeline Step 3)              ║
║            │                                                                  ║
║            └─ RECALL TOO LOW  (key content is missing)                       ║
║                ├─ Retries remaining? (max 3 attempts, wider search each time) ║
║                │   YES → Back to STEP D  (retry loop)                        ║
║                └─   NO → Return best available evidence anyway               ║
║                           (BC1 quality gate handles the fallback)            ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## BC3 — Knowledge Retrieval (called by BC2 Step E)

```
┌────────────────────────────────────────────────────────────────┐
│  UC-6: EXECUTE RETRIEVAL  (BC3 — Knowledge Retrieval)          │
│                                                                │
│  Receives a query from BC2                                     │
│  Routes to the correct store:                                  │
│    Product Inquiry     →  Product Catalog                      │
│    Referral Question   →  Referral Program Rules               │
│  Returns: real content only — never invented                   │
└────────────────────────────────────────────────────────────────┘
```

---

## The Two Quality Gates — At a Glance

| Gate | Where | Checks | If it fails |
|---|---|---|---|
| **Evidence Quality** | BC2 — after retrieval | Recall (completeness) + Precision (relevance of results) | Retry the search up to 3 times with a broader query |
| **Response Quality** | BC1 — after response generation | Groundedness (every claim traceable to evidence) + Relevance (answer matches the question) | Deliver a partial but honest answer using available evidence |

> Both gates exist for the same reason: **the user only ever receives an answer that can be traced back to real data.**
