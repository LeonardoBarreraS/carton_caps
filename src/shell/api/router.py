from fastapi import APIRouter

from shell.composition.container import AppContainer
from shell.api.schemas import (
    CloseSessionRequest,
    CloseSessionResponse,
    ProcessTurnRequest,
    ProcessTurnResponse,
    StartSessionRequest,
    StartSessionResponse,
)
from conversation_management.application.use_cases.start_session_use_case import (
    StartSessionCommand,
)
from conversation_management.application.use_cases.process_turn_use_case import (
    ProcessTurnCommand,
)
from conversation_management.application.use_cases.close_session_use_case import (
    CloseSessionCommand,
)


def build_router(container: AppContainer) -> APIRouter:
    router = APIRouter()

    @router.post("/sessions", response_model=StartSessionResponse, status_code=201)
    def start_session(body: StartSessionRequest) -> StartSessionResponse:
        result = container.start_session.execute(StartSessionCommand(user_id=body.user_id))
        return StartSessionResponse(session_id=result.session_id, status=result.status)

    @router.post(
        "/sessions/{session_id}/turns",
        response_model=ProcessTurnResponse,
        status_code=200,
    )
    def process_turn(session_id: str, body: ProcessTurnRequest) -> ProcessTurnResponse:
        result = container.process_turn.execute(
            ProcessTurnCommand(
                session_id=session_id,
                user_id=body.user_id,
                message=body.message,
            )
        )
        return ProcessTurnResponse(
            session_id=result.session_id,
            response_text=result.response_text,
            intent=result.intent,
            is_fallback=result.is_fallback,
            groundedness_score=result.groundedness_score,
            context_precision_score=result.context_precision_score,
            context_recall_score=result.context_recall_score,
            relevance_score=result.relevance_score,
        )

    @router.delete("/sessions/{session_id}", response_model=CloseSessionResponse, status_code=200)
    def close_session(session_id: str, body: CloseSessionRequest) -> CloseSessionResponse:
        result = container.close_session.execute(
            CloseSessionCommand(session_id=session_id, user_id=body.user_id)
        )
        return CloseSessionResponse(session_id=result.session_id, status=result.status)

    return router
