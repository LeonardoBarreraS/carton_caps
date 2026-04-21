from __future__ import annotations

import json


from openai import OpenAI

from decision_intelligence.application.ports.i_signal_extractor import ISignalExtractor
from decision_intelligence.domain.value_objects.preference_signal import PreferenceSignal

_SYSTEM_PROMPT = """\
You are a preference signal extractor for Carton Caps, a school fundraising app \
where users buy everyday grocery products (cereal, snacks, oatmeal, mac & cheese, \
pasta, rice, canned vegetables, trail mix, etc.) to raise money for their school.

Extract structured shopping preference signals from the user's message.
A signal is a key-value pair representing a user preference, constraint, or context \
clue relevant to recommending grocery products.

Valid signal keys — these are the only keys you should emit:
- product_category: the type of grocery product the user wants
  e.g. cereal, snacks, oatmeal, mac_and_cheese, pasta, rice, vegetables, trail_mix
- meal_occasion: when or how the product will be consumed
  e.g. breakfast, lunch, dinner, snack, school_lunch, on_the_go
- dietary_restriction: an explicit dietary constraint that rules out certain products
  e.g. gluten_free, nut_free, dairy_free, vegan, halal
- health_goal: a nutritional or wellness objective the user mentions
  e.g. healthy, whole_grain, high_protein, low_sugar, organic, nutritious
- budget_tier: the user's price sensitivity
  e.g. budget, mid_range, premium, cheap, affordable, expensive

Rules:
- Extract only what is explicitly stated or clearly implied by the message.
- Do not infer or guess preferences that are not evident.
- Use lowercase snake_case for keys and lowercase for values.
- Only emit keys from the five valid keys listed above — no other keys.
- If no signals are present, return an empty signals array.

Respond with a JSON object in exactly this format: {"signals": [{"key": "...", "value": "..."}]}"""


class OpenAISignalExtractor(ISignalExtractor):
    """
    Implements ISignalExtractor using OpenAI gpt-4o-mini in JSON mode.
    Extracts preference key-value pairs from a user message and returns
    PreferenceSignal value objects tagged with the current turn_number.
    """

    def __init__(self, openai_client: OpenAI, model: str = "gpt-4o-mini") -> None:
        self._client = openai_client
        self._model = model

    def extract(
        self,
        message: str,
        turn_number: int,
        conversation_history: list[dict] | None = None,
    ) -> list[PreferenceSignal]:
        messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
        if conversation_history:
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
            signals_data = parsed.get("signals", [])
        except json.JSONDecodeError:
            return []

        signals: list[PreferenceSignal] = []
        for item in signals_data:
            key = str(item.get("key", "")).strip().lower()
            value = str(item.get("value", "")).strip().lower()
            if key and value:
                try:
                    signals.append(
                        PreferenceSignal(key=key, value=value, turn_number=turn_number)
                    )
                except ValueError:
                    pass
        return signals
