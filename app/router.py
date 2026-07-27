import re

from app.models import Route

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
