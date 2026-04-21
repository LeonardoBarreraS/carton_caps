# Problem Understanding Summary
## Carton Caps Conversational Assistant

---

## What Did We Build in This Phase?

Before writing requirements, designing architecture, or choosing any technology, we had to answer one question: *what is this system actually for?*

Phase 0 is pure discovery. We read the project brief, studied the database schema, analyzed the business model, and synthesized everything into a clear understanding of the problem — the people involved, the business goal, the data available, and the role the assistant needs to play.

This phase produced one essential output: a shared, precise definition of the assistant's purpose that every subsequent phase builds on. Without it, technical decisions would be made in a vacuum.

---

## Why Does Problem Understanding Matter?

Technical systems fail for two reasons: they are built incorrectly, or they are built to solve the wrong problem. The second failure is worse — it can be delivered on time, pass all tests, and still be useless.

Understanding the problem first means every decision that follows — what the assistant must do, how conversations work, which data it uses, what counts as a good response — is anchored to the real business need. If the system ever drifts from that need, this phase is the reference to come back to.

---

# Part 1 — For Non-Technical Readers

## What is Carton Caps?

Carton Caps is a school fundraising platform built around everyday shopping. Parents buy products — cereals, snacks, household items — through the platform, and a portion of every purchase is donated to their child's school. The more parents participate, and the more they invite other parents, the more money the school receives.

This is not a charity. It is a shopping platform where the act of buying groceries becomes a fundraising act. The school does not need to run a bake sale, organize a fundraiser, or ask for donations. Parents simply shop — and the platform converts purchases into school funding.

---

## What problem does the assistant solve?

The platform works well when parents are engaged. But engagement drops off because parents:

- Do not always know which products to buy
- Do not understand how the referral program works
- Do not think about the platform between shopping trips
- Are not reminded of their school's connection to each purchase

The assistant is designed to solve this. It acts as a **personal shopping advisor who also cares about your school**.

Instead of browsing a product list alone, a parent has a conversation. The assistant learns what the parent needs — picky kids, healthy options, budget constraints — and guides them toward the right products. At the same time, it keeps the fundraising angle present in every recommendation, and explains the referral program when the opportunity arises.

---

## Who uses it?

| Who | What they need |
|---|---|
| **Parents** | Know what to buy; understand how purchases help the school; learn about referrals |
| **Schools** | Receive more donations because parents are better guided |
| **The platform** | More purchases, more referrals, more engaged users |

The core user is a parent buying groceries for their family who also wants to support their child's school — without extra effort on their part.

---

## What data does the system have to work with?

The platform has five data tables:

| Table | What it holds |
|---|---|
| **Users** | Parent accounts, each linked to one school |
| **Schools** | Schools receiving donations |
| **Products** | The catalog of everyday goods parents can buy |
| **Purchase History** | Records of past purchases (note: currently empty in the prototype dataset) |
| **Conversation History** | Prior conversations between the user and the assistant |

This data tells the assistant who it is talking to, which school to support, what products are available, and what that user has said in past conversations. Purchase history, once populated, will add behavioral signals — what that parent has bought before.

One important observation: **purchase history is empty today**. This means the assistant cannot rely on past behavior to make recommendations. It must learn preferences through conversation, turn by turn.

---

## What is the assistant?

It is easy to describe what the assistant is **not**:

- It is **not a search engine**. Typing "snacks" does not return a product list.
- It is **not a chatbot** that answers isolated questions.
- It is **not a generic Q&A system** that provides information on demand.
- It is **not a product retrieval system** that ignores what it already knows about you.

What it **is**:

> A **fundraising co-pilot** — a conversational guide that builds a growing picture of what you need, recommends products that match that picture, keeps your school's mission present at every step, and helps you understand how to do even more through referrals.

The assistant is a **decision-guidance system**. Its goal is not to answer questions. Its goal is to convert conversation into action that benefits the school.

---

## What does "stateful" mean in plain terms?

Most chat experiences are stateless — each message is processed without memory of the previous one. The Carton Caps assistant is different.

It remembers. When you say "my kids are picky" in the first message, the second message already has that context. When you later ask "what should I buy?", the assistant uses everything it has learned — picky kids, healthy preference, your school — to give you a specific, personalized answer.

This continuity is what makes the assistant a co-pilot rather than a search box.

---

# Part 2 — Technical Summary

## System Goal

**Final system goal:**

> The system is a stateful conversational decision engine that builds an evolving understanding of a user's fundraising intent and uses that understanding to guide product selections and referral actions that increase engagement, purchases, and school donations.

**Architecture-level transformation chain:**

```
conversation
    → signal extraction
    → decision context accumulation
    → context-aware reasoning
    → grounded recommendations
    → user behavior change
    → increased fundraising
```

**Engineering goal:**

Design a conversation-aware AI service that:
- Accumulates user decision signals across turns
- Models fundraising intent progressively
- Reasons over domain data (products, referral rules)
- Generates grounded recommendations (never invented)
- Encourages referral participation
- Maintains multi-turn context within and across sessions

---

## Business Case Analysis

### Value flow

```
Consumer brands → want exposure and sales
Parents         → buy everyday products
Platform        → tracks purchases, connects parents to schools
Schools         → receive donations proportional to purchases
```

Shopping behavior becomes school funding. The platform replaces bake sales, physical fundraising, and door-to-door selling.

### Referral growth engine

Every invited parent:
1. Signs up
2. Links to a school
3. Makes purchases

Both the referrer and the new user receive bonuses after onboarding. This creates network-driven fundraising amplification — more users means more purchases means more donations.

### The engagement gap

Users have the platform and can act, but engagement drops because:

| Problem | Effect |
|---|---|
| Don't know which products to buy | Fewer purchases |
| Don't understand referral mechanics | Fewer invitations |
| Don't see the school connection | Lower motivation |
| Not reminded between shopping trips | Platform forgotten |

**The assistant fills this gap** by guiding each user actively toward decisions that produce both purchases and referrals.

---

## Data Schema Summary

| Table | Fields | Role in the System |
|---|---|---|
| `Users` | `id`, `school_id`, `name`, `email`, `created_at` | User identity; defines fundraising relationship |
| `Schools` | `id`, `name`, `address`, `created_at` | Fundraising anchor; pre-seeded into every conversation |
| `Products` | `id`, `name`, `description`, `price`, `created_at` | Recommendation catalog; assistant recommends only from this table |
| `Purchase_History` | `id`, `user_id`, `product_id`, `quantity`, `purchased_at` | Behavioral signal; currently empty; graceful-degradation design |
| `Conversation_History` | session and message records | Multi-turn continuity; restored at session start |

**Key observations:**

1. Small product catalog → recommendation scope is bounded and well-defined
2. No purchase history → conversational elicitation of preferences is required
3. Users are linked to exactly one school → fundraising context is always known
4. Conversation history exists → multi-turn reasoning across sessions is expected and supported
5. Simple schema → prototype-level complexity appropriate

---

## Assistant Role Definition

### Final definition

> The assistant is a stateful conversational fundraising co-pilot that understands user intent through dialogue and actively guides users toward product selections and referral actions that increase school fundraising.

### What the assistant is NOT

| Common assumption | Actual role |
|---|---|
| A chatbot | A decision-guidance system |
| A Q&A system | A progressive preference elicitor |
| A search interface | A grounded recommendation engine |
| A product lookup | A context-accumulating co-pilot |

### What the assistant IS (by role)

| Role | Behavior |
|---|---|
| **Shopping advisor** | Learns preferences; guides toward the right products |
| **Fundraising optimizer** | Keeps the school connection present in every recommendation |
| **Referral guide** | Explains referral mechanics using retrieved rules; not LLM memory |
| **Decision co-pilot** | Accumulates signals turn by turn; improves with every message |

### Behavioral definition

1. Listen to user intent
2. Extract preferences and signals
3. Build and update decision context
4. Reason over product and referral data
5. Generate evidence-grounded recommendations
6. Continue the conversation — each turn smarter than the last

---

## Architectural Constraints Established Here

| Constraint | Source | Impact |
|---|---|---|
| User authentication is handled externally | Project brief | This service never authenticates; every request arrives with a pre-resolved `user_id` |
| Recommendations must be grounded in retrieved data | Business trust requirement | LLM cannot invent products or referral rules; everything must be traceable |
| Purchase history is currently empty | Data observation | Recommendations must be driven by conversational context, not behavioral history |
| School must be present in every recommendation | Business goal | Pre-seeded at session start; never something the assistant needs to ask |
| Multi-turn context must persist | Core conversation requirement | Each turn must build on all previous turns |
| Prototype scope | Project brief | Prototype-level storage and infrastructure acceptable at this stage |

---

## Key Insights from This Phase

**1. The business is fundraising, not shopping.**
Products are the mechanism. School funding is the goal. Every design decision must be oriented toward increasing donations — not just answering questions about products.

**2. Empty purchase history is a design constraint, not a gap.**
The system must reach confident recommendations through conversation. The architecture is designed to handle this gracefully both today and when purchase data becomes available.

**3. The school is always known.**
Every user is linked to one school. This context is available before the first message. The assistant never needs to ask what school the user supports — and must use that information in every recommendation.

**4. Stateful conversation is a first-class requirement.**
The value of the system increases with every turn. An assistant that forgets previous messages cannot serve as a co-pilot. Memory is not optional.

**5. The assistant is a behavioral influence system.**
The ultimate measure of success is not response quality — it is whether parents buy more products and invite more people. Everything from context accumulation to recommendation grounding is in service of that behavioral outcome.
