import asyncio
import logging

from app.integrations.discord import notify_discord
from app.integrations.email import notify_email

LOGGER = logging.getLogger(__name__)


async def escalate(question: str, *, student_identity: str, reason: str) -> bool:
    sent = False

    try:
        sent = await notify_discord(question, student_identity=student_identity, reason=reason) or sent
    except Exception:
        LOGGER.exception("Discord escalation failed")

    try:
        sent = await asyncio.to_thread(
            notify_email,
            question,
            student_identity=student_identity,
            reason=reason,
        ) or sent
    except Exception:
        LOGGER.exception("Email escalation failed")

    return sent
