from __future__ import annotations

"""
Composition root for the Carton Caps Conversational Assistant.

This module is the ONLY place in the system that imports from multiple bounded
contexts simultaneously. All other modules depend strictly downward within
their own layer.

Usage:
    from shell.composition.container import build_container

    container = build_container()
    start_session_uc = container["start_session"]
    process_turn_uc  = container["process_turn"]
    close_session_uc = container["close_session"]
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# ── Bounded Context 1 — Conversation Management ────────────────────────────
from conversation_management.application.use_cases.start_session_use_case import (
    StartSessionUseCase,
)
from conversation_management.application.use_cases.process_turn_use_case import (
    ProcessTurnUseCase,
)
from conversation_management.application.use_cases.close_session_use_case import (
    CloseSessionUseCase,
)
from conversation_management.infrastructure.repositories.sqlite_conversation_history_repository import (
    SQLiteConversationHistoryRepository,
)
from conversation_management.infrastructure.repositories.in_memory_conversation_session_repository import (
    InMemoryConversationSessionRepository,
)
from conversation_management.infrastructure.repositories.sqlite_user_repository import (
    SQLiteUserRepository,
)
from conversation_management.infrastructure.repositories.sqlite_school_repository import (
    SQLiteSchoolRepository,
)
from conversation_management.infrastructure.repositories.sqlite_purchase_history_repository import (
    SQLitePurchaseHistoryRepository,
)
from conversation_management.infrastructure.llm.openai_intent_classifier import (
    OpenAIIntentClassifier,
)
from conversation_management.infrastructure.llm.openai_response_generator import (
    OpenAIResponseGenerator,
)
from conversation_management.infrastructure.llm.openai_response_evaluator import (
    OpenAIResponseEvaluator,
)
from conversation_management.infrastructure.observability.sqlite_rag_metrics_logger import (
    SQLiteRAGMetricsLogger,
)

# ── Bounded Context 2 — Decision Intelligence ──────────────────────────────
from decision_intelligence.application.use_cases.pre_seed_context_use_case import (
    PreSeedContextUseCase,
)
from decision_intelligence.application.use_cases.process_turn_intelligence_use_case import (
    ProcessTurnIntelligenceUseCase,
)
from decision_intelligence.infrastructure.repositories.in_memory_decision_context_repository import (
    InMemoryDecisionContextRepository,
)
from decision_intelligence.infrastructure.llm.openai_signal_extractor import (
    OpenAISignalExtractor,
)
from decision_intelligence.infrastructure.llm.openai_evidence_evaluator import (
    OpenAIEvidenceEvaluator,
)

# ── Bounded Context 3 — Knowledge Retrieval ────────────────────────────────
from knowledge_retrieval.application.use_cases.execute_retrieval_use_case import (
    ExecuteRetrievalUseCase,
)
from knowledge_retrieval.infrastructure.repositories.qdrant_product_repository import (
    QdrantProductRepository,
)
from knowledge_retrieval.infrastructure.repositories.qdrant_referral_rule_repository import (
    QdrantReferralRuleRepository,
)

# ── Shell — cross-context adapters ─────────────────────────────────────────
from shell.composition.adapters.decision_intelligence_adapter import (
    DecisionIntelligenceAdapter,
)
from shell.composition.adapters.knowledge_retrieval_adapter import (
    KnowledgeRetrievalAdapter,
)
from shell.composition.logging_event_publisher import LoggingEventPublisher


@dataclass(frozen=True)
class AppContainer:
    """Holds the fully-wired application use cases exposed to the API layer."""

    start_session: StartSessionUseCase
    process_turn: ProcessTurnUseCase
    close_session: CloseSessionUseCase


def build_container() -> AppContainer:
    """
    Instantiate and wire every infrastructure adapter and use case.

    Configuration is read from environment variables (with sensible defaults
    for local development).  Call load_dotenv() before this function if you
    need to source a .env file from a non-default location.
    """
    load_dotenv()

    # ── Configuration ──────────────────────────────────────────────────────
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")
    sqlite_db_path: str = os.environ.get(
        "SQLITE_DB_PATH",
        str(Path(__file__).parent.parent.parent.parent / "data" / "carton_caps_data.sqlite"),
    )
    domain_event_log_path: str = os.environ.get(
        "DOMAIN_EVENT_LOG_PATH",
        str(Path(__file__).parent.parent.parent.parent / "data" / "domain_events.log"),
    )
    qdrant_url: str = os.environ.get("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key: str | None = os.environ.get("QDRANT_API_KEY") or None
    llm_model: str = os.environ.get("LLM_MODEL", "gpt-5.4-mini")
    min_groundedness: float = float(os.environ.get("MIN_GROUNDEDNESS", "0.8"))
    min_relevance: float = float(os.environ.get("MIN_RELEVANCE", "0.75"))
    rag_metrics_db_path: str = os.environ.get(
        "RAG_METRICS_DB_PATH",
        str(Path(__file__).parent.parent.parent.parent / "data" / "rag_metrics.sqlite"),
    )

    # ── Shared clients ─────────────────────────────────────────────────────
    openai_client = OpenAI(api_key=openai_api_key)

    # ── Infrastructure — BC-1 ──────────────────────────────────────────────
    # Conversation history now persisted to SQLite (replaces in-memory adapter).
    history_repo = SQLiteConversationHistoryRepository(db_path=sqlite_db_path)
    session_repo = InMemoryConversationSessionRepository()
    user_repo = SQLiteUserRepository(db_path=sqlite_db_path)
    school_repo = SQLiteSchoolRepository(db_path=sqlite_db_path)
    purchase_history_repo = SQLitePurchaseHistoryRepository(db_path=sqlite_db_path)

    intent_classifier = OpenAIIntentClassifier(openai_client=openai_client, model=llm_model)
    response_generator = OpenAIResponseGenerator(openai_client=openai_client, model=llm_model)
    response_evaluator = OpenAIResponseEvaluator(openai_client=openai_client, model=llm_model)
    rag_metrics_logger = SQLiteRAGMetricsLogger(db_path=rag_metrics_db_path)

    # ── Cross-cutting — domain event publisher ─────────────────────────────
    # Single instance satisfies both BC-1 and BC-2 IEventPublisher ports.
    event_publisher = LoggingEventPublisher(log_path=domain_event_log_path)

    # ── Infrastructure — BC-2 ──────────────────────────────────────────────
    decision_context_repo = InMemoryDecisionContextRepository()
    signal_extractor = OpenAISignalExtractor(openai_client=openai_client, model=llm_model)
    evidence_evaluator = OpenAIEvidenceEvaluator(openai_client=openai_client, model=llm_model)

    # ── Infrastructure — BC-3 ──────────────────────────────────────────────
    product_repo = QdrantProductRepository(qdrant_url=qdrant_url, openai_client=openai_client, qdrant_api_key=qdrant_api_key)
    referral_repo = QdrantReferralRuleRepository(qdrant_url=qdrant_url, openai_client=openai_client, qdrant_api_key=qdrant_api_key)

    # ── Use cases — BC-3 ───────────────────────────────────────────────────
    execute_retrieval_uc = ExecuteRetrievalUseCase(
        product_repository=product_repo,
        referral_rule_repository=referral_repo,
    )

    # ── Cross-context adapter: BC-2 → BC-3 ────────────────────────────────
    knowledge_retrieval_adapter = KnowledgeRetrievalAdapter(
        execute_retrieval_use_case=execute_retrieval_uc,
    )

    # ── Use cases — BC-2 ───────────────────────────────────────────────────
    pre_seed_uc = PreSeedContextUseCase(decision_context_repository=decision_context_repo)
    process_turn_intelligence_uc = ProcessTurnIntelligenceUseCase(
        decision_context_repository=decision_context_repo,
        signal_extractor=signal_extractor,
        evidence_evaluator=evidence_evaluator,
        knowledge_retrieval_service=knowledge_retrieval_adapter,
        event_publisher=event_publisher,
    )

    # ── Cross-context adapter: BC-1 → BC-2 ────────────────────────────────
    decision_intelligence_adapter = DecisionIntelligenceAdapter(
        pre_seed_use_case=pre_seed_uc,
        process_turn_use_case=process_turn_intelligence_uc,
    )

    # ── Use cases — BC-1 ───────────────────────────────────────────────────
    start_session_uc = StartSessionUseCase(
        session_repository=session_repo,
        history_repository=history_repo,
        user_repository=user_repo,
        school_repository=school_repo,
        purchase_history_repository=purchase_history_repo,
        decision_intelligence_service=decision_intelligence_adapter,
        event_publisher=event_publisher,
    )
    process_turn_uc = ProcessTurnUseCase(
        session_repository=session_repo,
        intent_classifier=intent_classifier,
        decision_intelligence_service=decision_intelligence_adapter,
        response_generator=response_generator,
        response_evaluator=response_evaluator,
        history_repository=history_repo,
        event_publisher=event_publisher,
        rag_metrics_logger=rag_metrics_logger,
        user_repository=user_repo,
        school_repository=school_repo,
        min_groundedness=min_groundedness,
        min_relevance=min_relevance,
    )
    close_session_uc = CloseSessionUseCase(
        session_repository=session_repo,
        event_publisher=event_publisher,
    )

    return AppContainer(
        start_session=start_session_uc,
        process_turn=process_turn_uc,
        close_session=close_session_uc,
    )
