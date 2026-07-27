from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class SessionState:
    session_id: str
    last_content_question: str | None = None
    history: list[tuple[str, str]] = field(default_factory=list)


_sessions: dict[str, SessionState] = {}


def get_session(session_id: str | None) -> SessionState:
    sid = session_id or str(uuid4())
    if sid not in _sessions:
        _sessions[sid] = SessionState(session_id=sid)
    return _sessions[sid]


def resolve_follow_up(message: str, state: SessionState) -> str:
    lower = message.strip().lower()
    follow_up_markers = ("what about", "and ", "also ", "for week", "week ")
    if state.last_content_question and lower.startswith(follow_up_markers):
        return f"{state.last_content_question}\nFollow-up: {message}"
    return message
