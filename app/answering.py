import re
from typing import Literal

from pydantic import BaseModel, Field

from app.escalation import escalate
from app.knowledge import load_knowledge_base_document
from app.llm import synthesize_with_llm
from app.session_memory import get_session, resolve_follow_up

Channel = Literal["web", "discord", "email"]
Route = Literal["content", "action_request", "declined", "not_question"]

NO_MATCH_TEXT = "I couldn't find this information in the current course material."
DECLINED_TEXT = (
    "I can only answer Gen Academy cohort-content questions from the approved course material. "
    "For career or job-transition advice, please contact your program mentor."
)
ACTION_TEXT = (
    "This looks like an account, access, scoring, credit, or submission request that needs a human review. "
    "I have escalated it to the support team."
)
ACK_TEXT = "Thanks for the note."

QUESTION_RE = re.compile(r"\?|^(where|what|when|which|who|how|can|could|is|are|do|does|did|has|have)\b", re.I)

ACTION_TERMS = {
    "billing",
    "refund",
    "payment",
    "promo",
    "coupon",
    "credit",
    "code",
    "pinecone",
    "fireworks",
    "elevenlabs",
    "replit",
    "extension",
    "submit",
    "submission",
    "score",
    "grade",
    "certificate",
    "assessment",
    "access",
    "login",
}
DECLINED_TERMS = {"career", "job", "recruiter", "resume", "cv", "layoff", "interview"}
CONTENT_TERMS = {
    "recording",
    "slides",
    "notes",
    "rag",
    "chunking",
    "embedding",
    "embeddings",
    "session",
    "week",
    "guest",
    "handout",
    "lecture",
    "mcp",
    "eval",
    "evaluation",
    "dataset",
}


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


def classify(message: str) -> Route:
    text = message.lower()
    tokens = set(re.findall(r"[a-z0-9]+", text))

    if not QUESTION_RE.search(text) and not (tokens & CONTENT_TERMS):
        return "not_question"
    if tokens & DECLINED_TERMS:
        return "declined"
    if tokens & CONTENT_TERMS:
        return "content"
    if tokens & ACTION_TERMS:
        return "action_request"
    return "content"


async def answer_chat(request: ChatRequest) -> ChatResponse:
    state = get_session(request.session_id)
    effective_message = resolve_follow_up(request.message, state)
    route = classify(effective_message)

    if route == "not_question":
        state.history.append((request.message, ACK_TEXT))
        return ChatResponse(answer=ACK_TEXT, route=route, session_id=state.session_id)

    if route == "declined":
        state.history.append((request.message, DECLINED_TEXT))
        return ChatResponse(answer=DECLINED_TEXT, route=route, session_id=state.session_id)

    if route == "action_request":
        await escalate(
            request.message,
            student_identity=request.student_identity,
            reason="Human action required",
        )
        state.history.append((request.message, ACTION_TEXT))
        return ChatResponse(answer=ACTION_TEXT, route=route, escalated=True, session_id=state.session_id)

    answer = synthesize_with_llm(effective_message, load_knowledge_base_document())

    if answer is None or answer.strip() == NO_MATCH_TEXT:
        await escalate(
            request.message,
            student_identity=request.student_identity,
            reason="No matching knowledge found",
        )
        state.history.append((request.message, NO_MATCH_TEXT))
        return ChatResponse(answer=NO_MATCH_TEXT, route=route, escalated=True, session_id=state.session_id)

    state.last_content_question = effective_message
    state.history.append((request.message, answer))
    return ChatResponse(answer=answer, route=route, session_id=state.session_id)
