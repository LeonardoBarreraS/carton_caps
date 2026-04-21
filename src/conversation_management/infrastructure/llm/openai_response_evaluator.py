from __future__ import annotations

import dataclasses
import json

from openai import OpenAI

from conversation_management.application.ports.i_response_evaluator import IResponseEvaluator
from conversation_management.domain.value_objects.assistant_response import AssistantResponse
from conversation_management.domain.value_objects.intent import Intent

_EVALUATION_PROMPT = """\
You are a RAG evaluation judge for a grocery shopping assistant.

Evaluate the assistant's response against the retrieved evidence and the user's intent.

User intent: {intent}

Retrieved evidence:
{evidence_text}

Assistant response:
{response_text}

Score both dimensions and return a JSON object with these exact fields:

- groundedness_score (float 0.0–1.0): Are all claims in the response traceable to the \
evidence above?
  0.0 = all claims are invented or hallucinated
  1.0 = every claim is directly supported by the evidence

- relevance_score (float 0.0–1.0): Does the response actually answer the user's question?
  Use the reverse-question technique: what question does this response answer?
  How closely does that match the stated intent?
  0.0 = answers a completely different question
  1.0 = precisely addresses the user's intent

- reasoning (string): One sentence explaining each score.

Return only a valid JSON object."""


class OpenAIResponseEvaluator(IResponseEvaluator):
    """
    Implements IResponseEvaluator using OpenAI gpt-4o-mini in JSON mode.
    Computes groundedness_score and relevance_score on a generated AssistantResponse.
    Returns a new immutable AssistantResponse with both scores populated.
    """

    def __init__(self, openai_client: OpenAI, model: str = "gpt-4o-mini") -> None:
        self._client = openai_client
        self._model = model

    def evaluate(
        self,
        response: AssistantResponse,
        intent: Intent,
        evidence: dict,
        conversation_history: list[dict],
    ) -> AssistantResponse:
        chunks: list[str] = evidence.get("chunks", [])
        evidence_text = (
            "\n".join(f"{i + 1}. {chunk}" for i, chunk in enumerate(chunks))
            if chunks
            else "No evidence provided."
        )

        history_text = ""
        if conversation_history:
            history_lines = []
            for entry in conversation_history:
                role_label = "User" if entry.get("role") == "user" else "Assistant"
                history_lines.append(f"{role_label}: {entry.get('content', '')}")
            history_text = "\nConversation history:\n" + "\n".join(history_lines) + "\n"

        prompt = _EVALUATION_PROMPT.format(
            intent=intent.value.value,
            evidence_text=evidence_text,
            response_text=response.text,
        ) + history_text

        llm_response = self._client.chat.completions.create(
            model=self._model,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )

        raw = llm_response.choices[0].message.content.strip()
        try:
            scores = json.loads(raw)
            groundedness = max(0.0, min(1.0, float(scores.get("groundedness_score", 0.0))))
            relevance = max(0.0, min(1.0, float(scores.get("relevance_score", 0.0))))
        except (json.JSONDecodeError, ValueError, TypeError):
            groundedness = 0.0
            relevance = 0.0

        return dataclasses.replace(
            response,
            groundedness_score=groundedness,
            relevance_score=relevance,
        )
