# Carton Caps Conversational Assistant — System Description & Requirements

---

## System Goal

A stateful AI assistant that learns a parent's shopping preferences through conversation and actively guides them toward product purchases and referral actions that maximize school fundraising donations.

---

## Functional Requirements

| # | Requirement | In one sentence |
|---|-------------|-----------------|
| FR1 | **Conversation Session Management** | The system opens, maintains, and closes a conversation session that preserves all context across multiple user messages. |
| FR2 | **Intent Recognition** | Every user message is classified before processing to determine whether the user is asking about products, referrals, general information, or something out of scope. |
| FR3 | **Progressive Decision Context Construction** | The system continuously extracts preference signals from each message and accumulates them into a growing profile that makes every subsequent response more personalized. |
| FR4 | **Context-Enriched Knowledge Retrieval** | Instead of searching with the raw user message, the system constructs an enriched query from everything it knows about the user and retrieves only verified, real content from the catalog or program rules. |
| FR5 | **Context-Driven Product Recommendation** | The system recommends products that match the user's accumulated preferences, citing only retrieved catalog items and always connecting the recommendation to the user's school. |
| FR6 | **Referral Guidance** | When a user expresses interest in helping their school more, the system provides accurate, grounded guidance on how the referral program works, based on retrieved platform rules. |
| FR7 | **Clarifying Question Generation** | When the system detects it lacks enough context to make a good recommendation, it asks the user one focused clarifying question before proceeding. |
| FR8 | **Conversational API Endpoint** | The entire multi-turn conversation is exposed through a clean API that any client application can call to send a message and receive a grounded, personalized response. |

---

## System Workflows

| # | Workflow | Trigger | In one sentence |
|---|----------|---------|-----------------|
| WF0 | **Conversational Response Loop** | Every user message | The master workflow that orchestrates every step from receiving a message to returning a validated, grounded response — runs on every single turn. |
| WF1 | **Decision Context Building** | Every user message | Extracts preference signals from the user's words and continuously enriches the decision profile, asking a clarifying question when a key piece of context is still missing. |
| WF2 | **Product Recommendation** | Product intent detected or context is ready | Uses the full accumulated context to search the product catalog, evaluates the quality of the results, and generates a personalized recommendation backed exclusively by retrieved evidence. |
| WF3 | **Referral Guidance** | Referral intent or fundraising opportunity detected | Retrieves the platform's actual referral program rules and delivers grounded guidance on how inviting other parents directly increases school donations. |

---

## How Requirements and Workflows Connect

```
Session opened (FR1)
    └─► User sends a message
            └─► Intent classified (FR2)
                    ├─► Context updated (FR3)          ← WF1 runs every turn
                    ├─► Product path (FR4, FR5)        ← WF2 activates
                    ├─► Referral path (FR4, FR6)       ← WF3 activates
                    └─► Clarification if needed (FR7)
                              └─► Grounded response delivered via API (FR8)
```
