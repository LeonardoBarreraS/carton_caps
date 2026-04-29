# Carton Caps Conversational Assistant — How It Works

> **A plain-language overview of the end-to-end process**

---

## What is this app?

Carton Caps is a school fundraising platform where parents buy everyday products — groceries, snacks, household items — and a portion of every purchase is donated to their child's school. The more parents buy, and the more they invite other parents to join, the more money the school receives.

The **Conversational Assistant** is an AI-powered guide built into the platform. It acts as a **personal shopping advisor that also cares about your school** — helping parents discover the right products through a natural conversation, while keeping the fundraising goal front and center.

---

## The Macro Process at a Glance

```mermaid
flowchart TD
    A(["👨‍👧 Parent opens the app\nand starts a conversation"])
    B["🔍 System loads your profile\n─────────────────────\n• Who you are\n• Which school you support\n• Your purchase history"]
    C(["💬 You chat naturally\nabout what you need"])
    D["🧠 Assistant listens and learns\n─────────────────────\nExtracts your preferences:\npicky kids · budget · food type..."]
    E{"Does the assistant\nhave enough to help?"}
    F["❓ Asks ONE focused\nclarifying question"]
    G["📚 Smart Search\n─────────────────────\nSearches the REAL product catalog\nor referral program rules\n— no guessing, no invented data —"]
    H["✅ Quality Check\n─────────────────────\nAre the results relevant?\nDoes the answer address your question?\nIs every claim traceable to real data?"]
    I(["💡 Delivers your personalized answer\n─────────────────────\nProduct recommendations\n+ school donation reminder\nor referral program guidance"])
    J{"Want to keep\nchatting?"}
    K(["🔚 Conversation ends"])
    L(["🛒 Parent purchases products"])
    M(["🏫 School receives\nfundraising donations"])
    N(["🤝 Parent invites friends\nto the platform"])
    O(["📈 More parents join\n→ More purchases\n→ More school funding"])

    A --> B
    B --> C
    C --> D
    D --> E
    E -- "Not yet" --> F
    F --> C
    E -- "Yes" --> G
    G --> H
    H --> I
    I --> J
    J -- "Yes" --> C
    J -- "No" --> K
    I --> L
    L --> M
    I --> N
    N --> O
```

---

## Step-by-Step: What Happens in a Conversation

| Step | What the user sees | What the system does |
|------|-------------------|---------------------|
| **1. Open the app** | Conversation starts instantly | Loads your profile, your school, and your purchase history |
| **2. Send your first message** | Natural chat — no forms to fill | Classifies your intent: product search, referral question, or general chat |
| **3. Assistant learns your needs** | Assistant pays attention | Extracts useful signals from your words: preferences, constraints, budget, family needs |
| **4. Clarifying question (if needed)** | One focused question, never a survey | Detects if a key piece of context is still missing and asks for it before searching |
| **5. Smart catalog search** | Happens automatically | Builds an enriched search query from *everything* it knows about you — not just your last message — and searches the real product catalog |
| **6. Quality verification** | Nothing visible | Checks that retrieved results are relevant and that the answer is grounded in real data — no hallucinations |
| **7. Get your recommendation** | A personalized, grounded answer | Generates a response backed by real products and real rules, always including the school donation reminder |
| **8. Continue the conversation** | Keep asking, keep refining | Every new message makes the next recommendation more precise |
| **9. Purchase & donate** | Normal checkout | Every purchase you make funds your school automatically |
| **10. Invite friends** | Referral guidance woven naturally into the chat | The assistant surfaces the referral program at the right moment — growing the school's fundraising network |

---

## The Three Core Pillars

```
   CONVERSATION              DECISION INTELLIGENCE         KNOWLEDGE BASE
  ───────────────          ─────────────────────────       ──────────────────
  Manages the session      Accumulates what it             Holds the full product
  Knows who you are        knows about you across          catalog and referral
  Keeps the history        turns and decides               program rules —
  Delivers the response    when to search and              only real verified data,
  after quality checks     what to search for              always up-to-date
```

---

## Why It Matters

- **No guessing.** Every product recommendation comes from the real catalog. Every referral rule comes from the real program documentation.
- **No repetition.** The assistant remembers what you said earlier in the conversation — you never have to repeat yourself.
- **Always aligned with the mission.** Every interaction nudges the parent toward a purchase or a referral — both of which directly benefit the school.
- **Gets smarter with every message.** The more you talk, the better the recommendations.
