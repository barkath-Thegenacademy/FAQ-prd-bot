from app.models import AgentAnswer


def compose(answers: list[AgentAnswer]) -> str:
    return "\n\n".join(a.text for a in answers)
