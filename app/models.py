from typing import Literal

from pydantic import BaseModel, Field

Channel = Literal["web", "discord", "email"]
Route = Literal["content", "action_request", "declined", "not_question"]


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str | None = None
    student_identity: str = "anonymous"
    channel: Channel = "web"


class ChatResponse(BaseModel):
    answer: str
    route: Route
    escalated: bool = False
    session_id: str
