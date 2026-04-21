from pydantic import BaseModel


# ── Requests ────────────────────────────────────────────────────────────────

class StartSessionRequest(BaseModel):
    user_id: str


class ProcessTurnRequest(BaseModel):
    user_id: str
    message: str


class CloseSessionRequest(BaseModel):
    user_id: str


# ── Responses ───────────────────────────────────────────────────────────────

class StartSessionResponse(BaseModel):
    session_id: str
    status: str


class ProcessTurnResponse(BaseModel):
    session_id: str
    response_text: str
    intent: str
    is_fallback: bool
    groundedness_score: float
    context_precision_score: float
    context_recall_score: float
    relevance_score: float


class CloseSessionResponse(BaseModel):
    session_id: str
    status: str


# ── Errors ──────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    error_code: str
    message: str
