from fastapi import FastAPI
from fastapi.responses import JSONResponse

from shell.composition.container import build_container
from shell.api.router import build_router
from shell.api.schemas import ErrorResponse
from conversation_management.application.use_cases.start_session_use_case import (
    SessionConflictError,
    UserNotFoundError,
    SchoolNotFoundError,
)
from conversation_management.application.use_cases.process_turn_use_case import (
    SessionNotFoundError as TurnSessionNotFoundError,
    SessionOwnershipError,
    InvalidTurnStateError,
)
from conversation_management.application.use_cases.close_session_use_case import (
    SessionNotFoundError as CloseSessionNotFoundError,
    AuthorizationError,
)
from conversation_management.domain.entities.conversation_session import (
    InvalidSessionTransitionError,
)


def create_app() -> FastAPI:
    app = FastAPI(title="Carton Caps Conversational Assistant")

    container = build_container()
    app.include_router(build_router(container))

    # ── Exception handlers ───────────────────────────────────────────────────

    @app.exception_handler(SessionConflictError)
    async def handle_session_conflict(request, exc):
        return JSONResponse(
            status_code=409,
            content=ErrorResponse(error_code="SESSION_CONFLICT", message=str(exc)).model_dump(),
        )

    @app.exception_handler(UserNotFoundError)
    async def handle_user_not_found(request, exc):
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(error_code="USER_NOT_FOUND", message=str(exc)).model_dump(),
        )

    @app.exception_handler(SchoolNotFoundError)
    async def handle_school_not_found(request, exc):
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(error_code="SCHOOL_NOT_FOUND", message=str(exc)).model_dump(),
        )

    @app.exception_handler(TurnSessionNotFoundError)
    async def handle_turn_session_not_found(request, exc):
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(error_code="SESSION_NOT_FOUND", message=str(exc)).model_dump(),
        )

    @app.exception_handler(CloseSessionNotFoundError)
    async def handle_close_session_not_found(request, exc):
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(error_code="SESSION_NOT_FOUND", message=str(exc)).model_dump(),
        )

    @app.exception_handler(SessionOwnershipError)
    async def handle_session_ownership(request, exc):
        return JSONResponse(
            status_code=403,
            content=ErrorResponse(error_code="OWNERSHIP_MISMATCH", message=str(exc)).model_dump(),
        )

    @app.exception_handler(InvalidTurnStateError)
    async def handle_invalid_turn_state(request, exc):
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error_code="INVALID_SESSION_STATE", message=str(exc)
            ).model_dump(),
        )

    @app.exception_handler(AuthorizationError)
    async def handle_authorization(request, exc):
        return JSONResponse(
            status_code=403,
            content=ErrorResponse(
                error_code="AUTHORIZATION_ERROR", message=str(exc)
            ).model_dump(),
        )

    @app.exception_handler(InvalidSessionTransitionError)
    async def handle_invalid_transition(request, exc):
        return JSONResponse(
            status_code=409,
            content=ErrorResponse(
                error_code="INVALID_STATE_TRANSITION", message=str(exc)
            ).model_dump(),
        )

    return app
