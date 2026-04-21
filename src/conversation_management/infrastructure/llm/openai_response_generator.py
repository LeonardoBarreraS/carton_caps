from __future__ import annotations

from openai import OpenAI

from conversation_management.application.ports.i_response_generator import IResponseGenerator
from conversation_management.domain.models import IntentType
from conversation_management.domain.value_objects.assistant_response import AssistantResponse

_SYSTEM_PROMPT_TEMPLATE = """\
You are a helpful shopping assistant for {user_name} \
supporting {school_name}'s fundraising program on Carton Caps.

Your role is to help families make good grocery choices while supporting their school's \
fundraising goals.

Only recommend products or referral program details that appear in the evidence provided below.
Never invent product names, prices, brands, or referral rules that are not in the evidence.
If the evidence is insufficient to fully answer the question, say so honestly and suggest \
the user ask a more specific question.

Retrieved evidence:
{evidence_text}"""

_CLARIFICATION_SYSTEM = """\
You are a friendly shopping assistant for Carton Caps helping {user_name} \
support {school_name}'s fundraising program. You need to ask the user a clarifying \
question to better understand their needs before making recommendations.
Rephrase the question below in a warm, conversational tone suitable for a family shopping app. \
Keep it brief — one or two sentences."""

_REDIRECT_REASON_INSTRUCTIONS: dict[str, str] = {
    "general_question": (
        "\nThe user has sent a general or conversational message — not a specific product or "
        "referral question. Respond warmly and helpfully. You may discuss how Carton Caps works, "
        "the fundraising mission, or general tips for families. Gently invite them to ask about "
        "specific products or the referral program if they'd like. "
        "Keep it friendly — one to three sentences."
    ),
    "out_of_scope": (
        "\nThe user has sent a message unrelated to Carton Caps — grocery shopping, school "
        "fundraising, or the referral program. Politely acknowledge their message and let them "
        "know what Carton Caps can help with: product recommendations, referral program questions, "
        "and fundraising tips. Invite them to ask a relevant question. "
        "Do not answer the off-topic message. Keep it concise — two to three sentences."
    ),
}

_LOW_QUALITY_WITH_EVIDENCE_SYSTEM = """\
You are a helpful shopping assistant for {user_name} \
supporting {school_name}'s fundraising program on Carton Caps.

The retrieval pipeline ran for this question but returned limited context. \
Use the evidence below as your starting point.

Strict rules:
- NEVER say you have no information, lack details, or cannot help.
- NEVER use phrases like "I'm not sure", "I don't have enough", or similar.
- Share what the evidence suggests, even if it is partial.
- Show genuine curiosity: end your response with exactly one focused follow-up question \
that would help you understand the user's real need better.
- Keep the response warm, conversational, and under four sentences.

Retrieved evidence (limited):
{evidence_text}"""

_REDIRECT_SYSTEM = """\
You are a friendly shopping assistant for Carton Caps helping {user_name} \
support {school_name}'s fundraising program.{reason_instruction}"""

_INTENT_MAP = {
    "product_evidence": IntentType.PRODUCT_INQUIRY,
    "referral_rule_evidence": IntentType.REFERRAL_QUESTION,
}

_REDIRECT_INTENT_MAP: dict[str, IntentType] = {
    "out_of_scope": IntentType.OUT_OF_SCOPE,
    "general_question": IntentType.GENERAL_QUESTION,
    "low_quality": IntentType.GENERAL_QUESTION,
}


class OpenAIResponseGenerator(IResponseGenerator):
    """
    Implements IResponseGenerator using OpenAI gpt-4o.
    Generates responses grounded exclusively in the retrieved evidence.
    Scores start at 0.0 — IResponseEvaluator populates them in the next pipeline step.
    """

    def __init__(self, openai_client: OpenAI, model: str = "gpt-4o") -> None:
        self._client = openai_client
        self._model = model

    def generate(
        self,
        message: str,
        conversation_history: list[dict],
        evidence: dict,
        context_snapshot: dict,
    ) -> AssistantResponse:
        school_name = context_snapshot.get("school_name", "your school")
        user_name = context_snapshot.get("user_name", "there")
        chunks: list[str] = evidence.get("chunks", [])
        evidence_type: str = evidence.get("evidence_type", "")

        evidence_text = (
            "\n".join(f"{i + 1}. {chunk}" for i, chunk in enumerate(chunks))
            if chunks
            else "No evidence retrieved."
        )

        system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(
            school_name=school_name,
            user_name=user_name,
            evidence_text=evidence_text,
        )

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})

        llm_response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.3,
        )

        text = llm_response.choices[0].message.content.strip()
        intent_answered = _INTENT_MAP.get(evidence_type, IntentType.GENERAL_QUESTION)

        # Scores are 0.0 here — IResponseEvaluator fills them in the next step.
        return AssistantResponse.create(
            text=text,
            intent_answered=intent_answered,
            groundedness_score=0.0,
            relevance_score=0.0,
            evidence_source_ids=[],
        )

    def generate_clarification(
        self,
        message: str,
        conversation_history: list[dict],
        clarification_question: str,
        user_context: dict,
    ) -> AssistantResponse:
        user_name = user_context.get("user_name", "there")
        school_name = user_context.get("school_name", "your school")
        system_prompt = _CLARIFICATION_SYSTEM.format(
            user_name=user_name,
            school_name=school_name,
        )
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        messages.append({"role": "assistant", "content": clarification_question})

        llm_response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.4,
        )
        text = llm_response.choices[0].message.content.strip()
        # Clarification responses bypass the quality gate — scores are set to 1.0.
        return AssistantResponse.create(
            text=text,
            intent_answered=IntentType.GENERAL_QUESTION,
            groundedness_score=1.0,
            relevance_score=1.0,
            evidence_source_ids=[],
        )

    def generate_redirect(
        self,
        message: str,
        conversation_history: list[dict],
        user_context: dict,
        redirect_reason: str,
        evidence: dict | None = None,
    ) -> AssistantResponse:
        user_name = user_context.get("user_name", "there")
        school_name = user_context.get("school_name", "your school")

        if redirect_reason == "low_quality" and evidence:
            chunks: list[str] = evidence.get("chunks") or []
            if chunks:
                evidence_text = "\n".join(f"{i + 1}. {chunk}" for i, chunk in enumerate(chunks))
                system_prompt = _LOW_QUALITY_WITH_EVIDENCE_SYSTEM.format(
                    user_name=user_name,
                    school_name=school_name,
                    evidence_text=evidence_text,
                )
            else:
                # No actual chunks despite low_quality reason — fall back to generic redirect.
                system_prompt = _REDIRECT_SYSTEM.format(
                    user_name=user_name,
                    school_name=school_name,
                    reason_instruction=_REDIRECT_REASON_INSTRUCTIONS["general_question"],
                )
        else:
            reason_instruction = _REDIRECT_REASON_INSTRUCTIONS.get(redirect_reason, "")
            system_prompt = _REDIRECT_SYSTEM.format(
                user_name=user_name,
                school_name=school_name,
                reason_instruction=reason_instruction,
            )

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})

        llm_response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.4,
        )
        text = llm_response.choices[0].message.content.strip()
        intent_answered = _REDIRECT_INTENT_MAP.get(redirect_reason, IntentType.GENERAL_QUESTION)
        # Redirect responses bypass the quality gate — scores are set to 1.0.
        return AssistantResponse.create(
            text=text,
            intent_answered=intent_answered,
            groundedness_score=1.0,
            relevance_score=1.0,
            evidence_source_ids=[],
        )
