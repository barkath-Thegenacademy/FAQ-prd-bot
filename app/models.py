from typing import Literal, Optional

from pydantic import BaseModel

Route = Literal["l3", "l4", "action_request", "declined"]
Outcome = Literal["answered", "escalated", "routed_to_human", "declined"]


class RouteDecision(BaseModel):
    route: Route
    reason: str
    target_human: Optional[str] = None


class VerificationResult(BaseModel):
    verified: bool
    cohort_id: Optional[str] = None
    reason: str


class RetrievedChunk(BaseModel):
    text: str
    source: str


class AgentAnswer(BaseModel):
    question: str
    route: Route
    outcome: Outcome
    text: str
