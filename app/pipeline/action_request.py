from app.config import get_config


def handle(target_human: str | None) -> str:
    human = target_human or get_config().action_request_human
    return f"This looks like a billing/enrollment action -- routing to {human} directly, no automated answer."
