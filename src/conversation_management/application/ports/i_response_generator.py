from __future__ import annotations

from abc import ABC, abstractmethod

from conversation_management.domain.value_objects.assistant_response import AssistantResponse


class IResponseGenerator(ABC):
    """
    Application-layer port for grounded response generation.

    Implemented in infrastructure by an LLM adapter.
    Receives retrieved evidence and a DecisionContext snapshot.
    Must produce a response grounded exclusively in that evidence.

    INV-AR-2: product recommendations cite only retrieved products.
    INV-AR-3: referral guidance derived exclusively from retrieved rules.
    INV-AR-4: school reference injected into generation context.
    """

    @abstractmethod
    def generate(
        self,
        message: str,
        conversation_history: list[dict],
        evidence: dict,
        context_snapshot: dict,
    ) -> AssistantResponse:
        """
        Generate a grounded response from retrieved evidence.

        conversation_history: full prior turns as [{"role": ..., "content": ...}].
        evidence: dict with 'chunks' (list[str]) and 'evidence_type' (str).
        context_snapshot: primitive snapshot from DecisionContext.snapshot().
        """
        ...

    @abstractmethod
    def generate_clarification(
        self,
        message: str,
        conversation_history: list[dict],
        clarification_question: str,
        user_context: dict,
    ) -> AssistantResponse:
        """
        Wrap a clarification question into a user-friendly response.
        Used when BC-2 detects context gaps or intent is ambiguous.

        conversation_history: full prior turns for LLM context.
        user_context: dict with 'user_name' and 'school_name' for personalization.
        """
        ...

    @abstractmethod
    def generate_redirect(
        self,
        message: str,
        conversation_history: list[dict],
        user_context: dict,
        redirect_reason: str,
        evidence: dict | None = None,
    ) -> AssistantResponse:
        """
        Generate a context-aware redirect response for situations where no
        knowledge-grounded answer can be produced.

        redirect_reason controls the tone and framing of the response:
          - "out_of_scope"     — message is off-domain; politely redirect to Carton Caps topics
          - "general_question" — conversational message; engage warmly, guide toward products or referral
          - "low_quality"      — pipeline ran but quality gate failed; evidence chunks are injected
                                 so the LLM can attempt a partial answer and ask a focused follow-up

        Does not invoke the DI pipeline or retrieval.
        Scores are hardcoded to 1.0 (quality gate is not meaningful here).

        conversation_history: full prior turns for LLM context.
        user_context: dict with 'user_name' and 'school_name' for personalization.
        redirect_reason: one of 'out_of_scope', 'general_question', 'low_quality'.
        evidence: optional dict with 'chunks' (list[str]) passed only for 'low_quality' so
                  the adapter can build a partial answer from retrieved context.
        """
        ...
