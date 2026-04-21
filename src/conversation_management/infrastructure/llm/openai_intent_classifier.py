from __future__ import annotations

import json

from openai import OpenAI

from conversation_management.application.ports.i_intent_classifier import IIntentClassifier
from conversation_management.domain.models import IntentType
from conversation_management.domain.value_objects.intent import Intent

_SYSTEM_PROMPT = """\
You are an intent classifier for Carton Caps, a grocery shopping assistant that helps \
families support school fundraising programs.

Classify the user's message into exactly one of these six intent categories:

- product_inquiry: The user is asking about grocery products, recommendations, what to buy, \
product details, prices, or categories.
- referral_question: The user is asking about the referral program, earning points, inviting \
friends, fundraising rewards, or how the incentive program works as: eligibility, referral process, reward structure, limitations & abuse, program changes.
or maybe some general FAQs as: what is the program, all about referrals, experience of new members, bonus, restrictions or policies of the program
- general_question: The user is asking a general question about Carton Caps, the service, \
how it works, its mission.
- clarification_response: The user is providing additional information or answering a \
clarifying question the assistant previously asked (e.g. "I have 3 kids", "we prefer organic").
- ambiguous: The message is unclear, too short, or could simultaneously belong to multiple \
on-domain categories.
- out_of_scope: The message is clearly unrelated to Carton Caps — jokes, random chat, \
weather questions, complaints about the app or service, account or billing claims, insults, \
or any message that has no connection to grocery shopping, products, referrals, or fundraising.

Decision rules:
- Messages mentioning specific foods, groceries, prices, or "what should I buy" → product_inquiry
- Messages mentioning referrals, friends, points, rewards, or fundraising mechanics → referral_question
- Questions about what Carton Caps is, how the service works, or its mission → general_question
- When genuinely uncertain between product_inquiry and referral_question, prefer product_inquiry
- Very short confirmation messages that seem to be answering a prior question → clarification_response
- Jokes, greetings without a question, random chat, weather, complaints about the app, \
account or billing issues, or messages with no Carton Caps reference → out_of_scope
- When uncertain between general_question and out_of_scope: if no Carton Caps reference \
exists, prefer out_of_scope

Respond with a JSON object in exactly this format: {"intent": "<label>"}"""


class OpenAIIntentClassifier(IIntentClassifier):
    """
    Implements IIntentClassifier using OpenAI gpt-4o-mini in JSON mode.
    No domain logic — purely translates model output to the Intent value object.
    """

    def __init__(self, openai_client: OpenAI, model: str = "gpt-4o-mini") -> None:
        self._client = openai_client
        self._model = model

    def classify(self, message: str, conversation_history: list[dict]) -> Intent:
        messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        response = self._client.chat.completions.create(
            model=self._model,
            response_format={"type": "json_object"},
            messages=messages,
            temperature=0.0,
        )
        raw = response.choices[0].message.content.strip()
        try:
            parsed = json.loads(raw)
            intent_str = parsed.get("intent", "ambiguous")
            intent_type = IntentType(intent_str)
        except (json.JSONDecodeError, ValueError):
            intent_type = IntentType.AMBIGUOUS
        return Intent(value=intent_type)
