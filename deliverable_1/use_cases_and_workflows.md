# Carton Caps Conversational Assistant — Use Cases & Workflows
### A Plain-Language Guide for Two Key User Moments

> **Who this is for:** Non-technical readers who want to understand what the app actually does, step by step, at the two moments a user interacts with it.
>
> **How to read this:** Each section maps one real user moment. Every box in the flows below is a named step or decision point — labeled so a diagram can be drawn directly from this text.

---

## The Two Moments

| Moment | What the user does | What the system must do |
|---|---|---|
| **A. START SESSION** | Opens the app to begin a conversation | Load everything the system needs to know about this user before the first message is processed |
| **B. CONVERSATIONAL TURN** | Sends a message asking about products or the referral program | Understand the request, search the knowledge base, verify the answer, and reply |

---

---

# MOMENT A — START SESSION

> **Goal:** Before the user can chat, the system must prepare a fully loaded conversation environment — who the user is, which school they support, and their purchase history — and hand it off to the intelligence engine so it is ready for the first message.

---

## A.1 — Overview

```
[USER OPENS THE APP]
        │
        ▼
[A — START SESSION USE CASE]  ←── BC1: Conversation Management owns this step
        │
        ├── Loads: Who is this user?
        ├── Loads: Which school do they support?
        ├── Loads: Any prior conversation history?
        ├── Loads: Any previous purchases?
        │
        ▼
[B — PRE-SEED CONTEXT USE CASE]  ←── BC2: Decision Intelligence owns this step
        │
        ├── Creates the user's "intelligence profile" (DecisionContext)
        ├── Plants the school as a permanent anchor
        └── Seeds any purchase history as early signals
        │
        ▼
[SESSION IS READY — status: IDLE]
        │
        └── The user can now send their first message
```

---

## A.2 — Step-by-Step: Start Session

### Step 1 of 2 — [A] START SESSION USE CASE
**Which part of the system:** BC1 — Conversation Management
**Goal:** Create a new conversation slot for this user and load all the information needed to have a meaningful first exchange.

```
[A — START SESSION USE CASE]
        │
        ├─ CHECK: Does this user already have an open conversation?
        │         ├─ YES → REJECT. One conversation at a time.
        │         └─ NO  → Continue
        │
        ├─ LOAD: User identity (who is the person?)
        │         └─ Not found → REJECT. Unknown user.
        │
        ├─ LOAD: School (which school does this user support?)
        │         └─ Not found → REJECT. No school linked to this user.
        │
        ├─ LOAD: Conversation History (has this user chatted before?)
        │         └─ None found → OK. Start fresh.
        │
        ├─ LOAD: Purchase History (has this user bought anything before?)
        │         └─ None found → OK. Skip. (Will be used when populated)
        │
        ├─ CREATE: A new conversation slot (status: INITIALIZING)
        │
        ├─ HAND OFF → [B] PRE-SEED CONTEXT USE CASE in BC2
        │             (pass: school info + any purchase signals)
        │
        ├─ MARK conversation as READY (status: IDLE)
        │
        └─ RETURN: Session ID to the app interface
```

---

### Step 2 of 2 — [B] PRE-SEED CONTEXT USE CASE
**Which part of the system:** BC2 — Decision Intelligence
**Goal:** Build the user's "intelligence profile" from scratch, planting the school anchor and any early purchase signals before any message arrives.

```
[B — PRE-SEED CONTEXT USE CASE]
        │
        ├─ CREATE: A fresh intelligence profile (DecisionContext)
        │           └─ Plant the school as a permanent anchor
        │               (This anchor NEVER changes during the session)
        │
        ├─ CHECK: Were any purchase signals passed in?
        │         ├─ YES → Add each one as an early preference signal
        │         │         (profile may move from EMPTY → PARTIAL)
        │         └─ NO  → Profile stays EMPTY. That is fine.
        │
        └─ SAVE the intelligence profile
           (It will grow with every message the user sends)
```

---

## A.3 — Session States

The conversation slot moves through these states during startup:

```
[CREATED] → [INITIALIZING] → [IDLE — ready for first message]
```

| State | Meaning |
|---|---|
| CREATED | Slot reserved. Identity confirmed. |
| INITIALIZING | Loading data. Pre-seeding the intelligence profile. |
| IDLE | Everything loaded. Waiting for the user's first message. |

---

## A.4 — What Goes Wrong & What Happens

| Situation | What the system does |
|---|---|
| User already has an open conversation | REJECT. Returns an error. One session at a time. |
| User identity not found | REJECT. Returns an error. |
| School not linked to the user | REJECT. Returns an error. School is required. |
| No prior conversation history | Accepted. Conversation starts fresh. |
| No purchase history | Accepted. Intelligence profile starts empty. |

---

---

# MOMENT B — CONVERSATIONAL TURN (with Knowledge Retrieval)

> **Goal:** The user sends a message asking about products or the referral program. The system must understand what the user wants, decide if it knows enough to search, search the real knowledge base, verify the quality of what it found, and deliver a grounded, personalized answer.

---

## B.1 — Overview

```
[USER SENDS A MESSAGE]
        │
        ▼
[C — PROCESS TURN USE CASE]  ←── BC1 owns the full turn
        │
        ├── Checks: Is the session ready for a new message?
        │
        ▼
[TURN PIPELINE — TurnGraph]  ←── Runs inside BC1
        │
        ├─ [STEP 1] Classify Intent
        │            What does the user actually want?
        │
        ├─ [STEP 2] Route by Intent
        │            Four possible paths (see B.3)
        │
        ├─ [STEP 3 — RAG PATH] Process Decision Intelligence ──► BC2 is called here
        │            Understand the user deeper. Search if ready.
        │
        ├─ [STEP 4] Generate Response
        │            Write an answer grounded in real evidence
        │
        ├─ [STEP 5] Evaluate Response Quality
        │            Is the answer grounded? Does it actually help?
        │
        ├─ [STEP 6] Deliver Answer or Redirect
        │
        └─ [STEP 7] Save the conversation history
```

---

## B.2 — Step-by-Step: Process Turn Use Case

**Which part of the system:** BC1 — Conversation Management
**Goal:** Be the entry door for every user message. Guard the session state. Run the turn pipeline. Save the result.

```
[C — PROCESS TURN USE CASE]
        │
        ├─ LOAD: The user's open conversation slot
        │         └─ Not found → REJECT with error
        │
        ├─ CHECK: Is the conversation in IDLE state?
        │         ├─ Not IDLE (still initializing, already active, or closed) → REJECT
        │         └─ IDLE → Continue
        │
        ├─ CHECK: Does this message belong to this session's owner?
        │         ├─ Mismatch → REJECT
        │         └─ Match → Continue
        │
        ├─ LOAD: Full conversation history (to give context to all AI calls)
        ├─ LOAD: User's name (for personalized responses)
        ├─ LOAD: School's name (for personalized responses)
        │
        ├─ MARK conversation as ACTIVE (turn is in progress)
        │
        ├─ RUN → [TURN PIPELINE — TurnGraph]
        │         (see B.3 below)
        │
        ├─ On success:
        │   ├─ MARK conversation as IDLE again (ready for next message)
        │   ├─ SAVE the conversation slot
        │   └─ RETURN response to the app interface
        │
        └─ On any error during the pipeline:
            ├─ ROLLBACK: Mark conversation as IDLE (no data lost)
            └─ RETURN error to the app interface
```

---

## B.3 — The Turn Pipeline (TurnGraph)

**Which part of the system:** BC1 — Conversation Management (internal pipeline)
**Goal:** Run the full processing pipeline for one user message, from intent classification to final response delivery.

### Step 1 — [STEP 1] Classify Intent

```
[STEP 1 — CLASSIFY INTENT]
        │
        ├─ Read the user's message (with conversation history for context)
        └─ Decide: What does the user want?

        Intent options:
        ├─ PRODUCT INQUIRY      → User wants product recommendations
        ├─ REFERRAL QUESTION    → User wants to know about the referral program
        ├─ CLARIFICATION RESPONSE → User is answering a question the assistant asked
        ├─ GENERAL QUESTION     → User has an on-topic but non-search question
        ├─ AMBIGUOUS            → Unclear what the user wants
        └─ OUT OF SCOPE         → Unrelated to Carton Caps entirely
```

---

### Step 2 — [STEP 2] Route by Intent (4 Paths)

```
[STEP 2 — ROUTE BY INTENT]
        │
        ├─ OUT OF SCOPE or GENERAL QUESTION
        │   └──► [PATH A] GENERATE REDIRECT RESPONSE
        │         Goal: Give a helpful but scope-aware reply.
        │         No intelligence pipeline. No knowledge search.
        │         └──► [STEP 7] SAVE HISTORY → END
        │
        ├─ AMBIGUOUS
        │   └──► [PATH B] GENERATE CLARIFICATION
        │         Goal: Ask one focused question to understand the user.
        │         No intelligence pipeline. No knowledge search.
        │         └──► [STEP 7] SAVE HISTORY → END
        │
        └─ PRODUCT INQUIRY, REFERRAL QUESTION, or CLARIFICATION RESPONSE
            └──► [PATH C — RAG PATH] Continue to Step 3
```

---

### Step 3 — [STEP 3] Process Decision Intelligence (BC2 is called)

> This is where BC1 hands off to BC2 — Decision Intelligence — to do the deep work.
> The entire intelligence pipeline described in B.4 runs here.
> BC2 returns either: (a) retrieved evidence ready for an answer, or (b) a signal that clarification is still needed.

```
[STEP 3 — PROCESS DECISION INTELLIGENCE]
        │
        ├─ SEND to BC2: intent + message + conversation history
        │
        ├─ BC2 runs its full pipeline (see B.4 for detail)
        │
        └─ BC2 RETURNS one of two outcomes:
            │
            ├─ CLARIFICATION NEEDED
            │   └──► [PATH B] GENERATE CLARIFICATION
            │         (Ask the user for a missing piece of information)
            │         └──► [STEP 7] SAVE HISTORY → END
            │
            └─ EVIDENCE RETRIEVED
                └──► [STEP 4] GENERATE RESPONSE
```

---

### Step 4 — [STEP 4] Generate Response

```
[STEP 4 — GENERATE RESPONSE]
        │
        ├─ Use the retrieved evidence + conversation context
        ├─ Personalize with the user's name and school name
        └─ Write an answer grounded only in retrieved evidence
           (No invented products. No fabricated rules.)
        │
        └──► [STEP 5] EVALUATE RESPONSE QUALITY
```

---

### Step 5 — [STEP 5] Evaluate Response Quality

```
[STEP 5 — EVALUATE RESPONSE QUALITY]
        │
        ├─ Check 1 — GROUNDEDNESS: Is every claim in the answer traceable
        │             to something retrieved from the knowledge base?
        │
        ├─ Check 2 — RELEVANCE: Does the answer actually address
        │             what the user asked?
        │
        └─ DECISION:
            │
            ├─ BOTH CHECKS PASS
            │   └──► [STEP 7] SAVE HISTORY → END
            │         (Deliver the grounded, relevant answer)
            │
            └─ EITHER CHECK FAILS
                └──► [PATH D] GENERATE PARTIAL ANSWER REDIRECT
                      Goal: Use the partial evidence to give the best
                      possible answer, and ask a follow-up question.
                      (Never deflect. Never leave the user empty-handed.)
                      └──► [STEP 7] SAVE HISTORY → END
```

---

### Step 6 — [STEP 6] All Paths Converge Here

Every path — grounded answer, clarification, redirect, or partial answer — ends the same way:

```
[STEP 7 — SAVE HISTORY]
        │
        ├─ Save the user's message to conversation history
        ├─ Save the assistant's response to conversation history
        └─ Return the response to the app interface
```

---

## B.4 — Inside BC2: The Decision Intelligence Pipeline

> This pipeline runs inside Step 3 of the Turn Pipeline.
> BC2's job is to understand the user deeply enough to build a precise search query — and then search.

**Which part of the system:** BC2 — Decision Intelligence (internal pipeline: DecisionIntelligenceSubgraph)
**Goal:** Extract what the user cares about, decide if there is enough to search well, search the right knowledge base, and verify the quality of what was found.

---

### The Intelligence Profile (DecisionContext)

Before going into the steps, it helps to know what the intelligence profile is:

```
THE INTELLIGENCE PROFILE (DecisionContext)
        │
        ├─ Starts at session creation (from Moment A)
        ├─ ALWAYS contains: the user's school (permanent anchor)
        ├─ GROWS with every message: preferences, constraints, family needs
        └─ NEVER loses information: signals only accumulate, never get removed

        Profile States:
        EMPTY → PARTIAL → READY → ENRICHED
        (More signals = more precise search queries)
```

---

### BC2 Step-by-Step

#### [BC2-STEP 1] Extract Signals

```
[BC2-STEP 1 — EXTRACT SIGNALS]
        │
        ├─ Read the user's message (with recent conversation history for context)
        └─ Pull out structured preferences:
           Examples: "picky kids", "healthy", "budget-sensitive",
                     "cereal", "breakfast", "nut allergy"
        │
        └──► [BC2-STEP 2] UPDATE INTELLIGENCE PROFILE
```

---

#### [BC2-STEP 2] Update Intelligence Profile

```
[BC2-STEP 2 — UPDATE INTELLIGENCE PROFILE]
        │
        ├─ Add each new preference to the profile
        ├─ Profile may move states:
        │   EMPTY → PARTIAL (first signal added)
        │   PARTIAL → READY (enough signals for a good search)
        │   READY → ENRICHED (even more signals for precise search)
        │
        └──► [BC2-STEP 3] EVALUATE READINESS
```

---

#### [BC2-STEP 3] Evaluate Readiness (Intent-Sensitive)

```
[BC2-STEP 3 — EVALUATE READINESS]
        │
        ├─ REFERRAL QUESTION intent?
        │   └──► SKIP readiness check entirely
        │         (The user's question IS the search query. No preferences needed.)
        │         └──► [BC2-STEP 4] BUILD SEARCH QUERY
        │
        └─ PRODUCT INQUIRY intent?
            │
            ├─ Does the profile have at least ONE useful preference signal?
            │  (category, meal type, dietary need, health goal, budget level)
            │
            ├─ YES — enough to search
            │   ├─ Mark profile as READY (if not already)
            │   └──► [BC2-STEP 4] BUILD SEARCH QUERY
            │
            └─ NO — not enough context
                ├─ Save the user's original intent (to resume later)
                └──► RETURN to BC1: CLARIFICATION NEEDED
                      (BC1 will ask the user one focused question)
                      ──► When the user answers → comes back as CLARIFICATION RESPONSE intent
                      ──► Resume loop: check saved intent → if ready → [BC2-STEP 4]
                                                             if still missing → ask again
```

---

#### [BC2-STEP 4] Build Search Query

```
[BC2-STEP 4 — BUILD SEARCH QUERY]
        │
        ├─ For PRODUCT INQUIRY and REFERRAL QUESTION (fresh intent):
        │   Primary: Use the user's actual message words
        │   (These words match the knowledge base vocabulary best)
        │   Plus: Reinforce with accumulated preference signals
        │
        ├─ For CLARIFICATION RESPONSE (resuming after a clarification gap):
        │   Primary: Use the accumulated preference signals
        │   (The user's answer may be short like "yes" or "cereal")
        │
        ├─ If the combined text is too short (vague answer like "ok", "yes"):
        │   └─ Look back in conversation history for the last meaningful message
        │      and use that as the query foundation
        │
        └─ ROUTE:
            ├─ PRODUCT INQUIRY  →  Search the PRODUCT CATALOG
            └─ REFERRAL QUESTION →  Search the REFERRAL PROGRAM RULES
        │
        └──► [BC2-STEP 5] EXECUTE RETRIEVAL (calls BC3)
```

---

#### [BC2-STEP 5] Execute Retrieval (BC3 is called)

```
[BC2-STEP 5 — EXECUTE RETRIEVAL]
        │
        ├─ SEND query to BC3 — Knowledge Retrieval
        │
        └─ BC3 searches the correct knowledge base:
            ├─ PRODUCT CATALOG vector store     (for product inquiries)
            └─ REFERRAL PROGRAM RULES store     (for referral questions)
        │
        ├─ RETURN: Top matching content chunks from the knowledge base
        │
        ├─ Increment attempt counter
        └──► [BC2-STEP 6] EVALUATE EVIDENCE QUALITY
```

---

#### [BC2-STEP 6] Evaluate Evidence Quality (Retry Loop)

```
[BC2-STEP 6 — EVALUATE EVIDENCE QUALITY]
        │
        ├─ Check 1 — RECALL: Did the search return all the relevant content?
        │             (Are key parts of the answer missing from the results?)
        │
        ├─ Check 2 — PRECISION: Is what was returned actually on-topic?
        │             (Are there irrelevant chunks mixed in?)
        │
        └─ DECISION:
            │
            ├─ QUALITY PASSES
            │   └──► RETURN evidence to BC1
            │         (BC1 Step 4 will generate a response from this evidence)
            │
            └─ RECALL IS TOO LOW (important content is missing)
                ├─ Retry allowed? (max 3 attempts)
                │   ├─ YES:
                │   │   ├─ Expand the search (retrieve more results next time)
                │   │   └──► [BC2-STEP 4] BUILD SEARCH QUERY again (retry)
                │   │
                │   └─ NO (max retries reached):
                │       └──► RETURN what was found anyway
                │             (BC1's quality gate will handle the fallback)
```

---

### BC2 Clarification Resume Loop (Full Picture)

```
[USER MESSAGE — product inquiry]
        │
        ▼
[BC2-STEP 3 — EVALUATE READINESS]
        │
        └─ No useful signals yet
            │
            ├─ Save original intent: "product_inquiry"
            └─ Return: CLARIFICATION NEEDED
                        ↓
            BC1 asks the user a question, e.g.:
            "What kind of products are you looking for?"
                        ↓
            [USER REPLIES — clarification response]
                        ↓
            [BC2-STEP 3 — EVALUATE READINESS again]
                        │
                        ├─ Recover saved original intent: "product_inquiry"
                        ├─ Re-check: Are there useful signals now?
                        │
                        ├─ YES → Override intent to "product_inquiry"
                        │         Clear the saved intent
                        │         └──► [BC2-STEP 4] BUILD SEARCH QUERY
                        │
                        └─ STILL NO → Save intent again, return CLARIFICATION NEEDED
                                       (Loop continues until signals arrive)
```

---

## B.5 — Inside BC3: Knowledge Retrieval

**Which part of the system:** BC3 — Knowledge Retrieval
**Goal:** Receive a search query, search the correct knowledge base, return only real content. Never invent anything.

```
[BC3 — EXECUTE RETRIEVAL USE CASE]
        │
        ├─ VALIDATE: Is the target a valid knowledge base?
        │             └─ Invalid target → REJECT with error
        │
        ├─ ROUTE:
        │   ├─ Target = PRODUCT CATALOG
        │   │   └─ Run semantic search on the product catalog
        │   │       Returns: matching products from the real catalog
        │   │
        │   └─ Target = REFERRAL PROGRAM RULES
        │       └─ Run semantic search on the referral rules store
        │           Returns: matching referral rules from the real documentation
        │
        └─ RETURN: Retrieved content chunks
                   (Quality scoring happens back in BC2, not here)
```

---

## B.6 — Session States During a Turn

The conversation slot moves through these states on every turn:

```
[IDLE] → [ACTIVE — turn running] → [IDLE — ready for next message]

If an error occurs mid-turn:
[ACTIVE] → [IDLE — rolled back, no data lost. User can try again.]
```

---

## B.7 — Complete Turn Flow Summary (All Paths)

```
USER SENDS A MESSAGE
        │
        ▼
[C] PROCESS TURN USE CASE (BC1)
        │  Load session, load history, mark ACTIVE
        ▼
[STEP 1] CLASSIFY INTENT
        │
        ├─ OUT OF SCOPE ──────────────────────────────────────────────────────────┐
        │                                                                          │
        ├─ GENERAL QUESTION ──────────────────────────────────────────────────────┤
        │                                                                          │
        ├─ AMBIGUOUS ──────────────────────────────────────► GENERATE CLARIFICATION┤
        │                                                                          │
        └─ PRODUCT INQUIRY / REFERRAL QUESTION / CLARIFICATION RESPONSE           │
                │                                                                  │
                ▼                                                                  │
        [STEP 3] PROCESS DECISION INTELLIGENCE (BC2)                              │
                │                                                                  │
                ├─ [BC2] Extract signals                                           │
                ├─ [BC2] Update intelligence profile                               │
                ├─ [BC2] Evaluate readiness                                        │
                │         ├─ CLARIFICATION NEEDED ─────────────────────────────► GENERATE CLARIFICATION
                │         └─ READY TO SEARCH                                      │
                │                 │                                                │
                │         [BC2] Build search query                                 │
                │         [BC2] Execute retrieval (BC3 called)                     │
                │         [BC2] Evaluate evidence quality                          │
                │               ├─ Low recall → Retry (up to 3x)                  │
                │               └─ Pass → Return evidence                          │
                │                                                                  │
                ▼                                                                  │
        [STEP 4] GENERATE RESPONSE                                                 │
                │                                                                  │
                ▼                                                                  │
        [STEP 5] EVALUATE RESPONSE QUALITY                                         │
                │                                                                  │
                ├─ PASS ──────────────────────────────────────────────────────────┤
                │                                                                  │
                └─ FAIL ─────────────────────────────► GENERATE PARTIAL ANSWER   │
                                                        REDIRECT                  │
                                                                                  │
                                                        ◄─────────────────────────┘
                                                        ALL PATHS ARRIVE HERE
                                                                │
                                                                ▼
                                                        [STEP 7] SAVE HISTORY
                                                                │
                                                                ▼
                                                        RETURN ANSWER TO USER
```

---

## B.8 — What Goes Wrong & What Happens

| Situation | What the system does |
|---|---|
| Session not found | REJECT with error |
| Session not in IDLE state | REJECT. Turn refused until session is ready. |
| Message not from this session's owner | REJECT. Security guard. |
| User's intent is unclear | Ask one clarifying question. Wait for the answer. |
| User's message is off-topic | Give a polite, scope-aware response. No search. |
| Not enough context to search well | Ask one targeted question. Resume the search when answered. |
| Retrieved content has low relevance | Retry the search up to 3 times with broader queries. |
| Generated answer can't be traced to real data | Use partial evidence to give the best possible answer + follow-up question. Never return a fabricated answer. |
| Any error mid-turn | Roll back. Session returns to IDLE. User can try again. |

---

## Glossary for Diagram Creation

> Use the labels below when creating visual diagrams of these flows.

| Label | What it represents |
|---|---|
| `START SESSION` | Moment A entry point |
| `UC-1: Start Session` | BC1 use case that initializes the conversation |
| `UC-4: Pre-Seed Context` | BC2 use case that builds the initial intelligence profile |
| `DecisionContext` | The intelligence profile — grows with every turn |
| `PROCESS TURN` | Moment B entry point |
| `UC-2: Process Turn` | BC1 use case that owns every conversation turn |
| `TurnGraph` | The pipeline engine that runs inside UC-2 |
| `Classify Intent` | TurnGraph node that decides what the user wants |
| `RAG PATH` | The path taken when the user wants products or referral info |
| `UC-5: Process Turn Intelligence` | BC2 use case that runs the full intelligence pipeline |
| `DecisionIntelligenceSubgraph` | The pipeline engine that runs inside UC-5 |
| `Extract Signals` | Subgraph node that pulls preferences from the message |
| `Update Profile` | Subgraph node that adds signals to DecisionContext |
| `Evaluate Readiness` | Subgraph node that decides if there is enough context to search |
| `Build Search Query` | Subgraph node that constructs a precise search query |
| `UC-6: Execute Retrieval` | BC3 use case that performs the actual knowledge base search |
| `Product Catalog` | Knowledge base for product searches |
| `Referral Program Rules` | Knowledge base for referral program questions |
| `Evaluate Evidence Quality` | Subgraph node that checks if retrieved content is good enough |
| `Retrieval Retry Loop` | Back-edge from quality check to query building (max 3 attempts) |
| `Generate Response` | TurnGraph node that writes the personalized answer |
| `Evaluate Response Quality` | TurnGraph node that checks groundedness and relevance |
| `Generate Clarification` | TurnGraph node that asks the user a focused question |
| `Generate Redirect` | TurnGraph node for off-topic, general, or quality-failed responses |
| `Save History` | TurnGraph node that persists the full turn to conversation history |
| `Clarification Resume Loop` | Cycle from clarification back to readiness check with saved intent |
