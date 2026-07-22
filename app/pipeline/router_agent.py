from app.llm import complete_json
from app.models import RouteDecision

SYSTEM = """You are the router for a cohort support bot. Classify one incoming student question into
exactly one route:

- "action_request": billing issues, tool credit / promo code requests, refunds, enrollment drops, or
  anything that changes a system of record. These always go to a human, never answered by the bot.
- "l4": schedule and deadlines -- session times, calendar invites, channel access, project submission
  dates, assessment or certificate timing.
- "l3": session content -- recordings, solution kits, recaps, technical/conceptual questions about
  course material.
- "declined": career or job-transition coaching questions. The bot has no authority to answer these
  and must decline.

Respond with ONLY a JSON object: {"route": "...", "reason": "...", "target_human": "..." or null}.
target_human is only set when route is "action_request" (use "Arvind" unless the question clearly
names someone else).
"""


def classify(question: str) -> RouteDecision:
    result = complete_json(SYSTEM, question, max_tokens=256)
    return RouteDecision(**result)
