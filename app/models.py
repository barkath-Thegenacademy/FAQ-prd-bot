from typing import Literal

from pydantic import BaseModel, Field

Channel = Literal["web", "discord", "email"]
Route = Literal["content", "action_request", "declined", "not_question"]


class Source(BaseModel):
    title: str
    source: str
    url: str | None = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str | None = None
    student_identity: str = "anonymous"
    channel: Channel = "web"


class ChatResponse(BaseModel):
    answer: str
    route: Route
    sources: list[Source] = []
    escalated: bool = False
    session_id: str


class KnowledgeDocument(BaseModel):
    id: str
    title: str
    source: str
    content: str
    url: str | None = None
    tags: list[str] = []
