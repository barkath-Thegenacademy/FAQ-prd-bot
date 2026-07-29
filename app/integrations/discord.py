from datetime import datetime, timezone

import httpx

from app.config import get_config


async def notify_discord(question: str, *, student_identity: str, reason: str) -> bool:
    webhook_url = get_config().discord_webhook_url
    if not webhook_url:
        return False

    payload = {
        "content": None,
        "embeds": [
            {
                "title": "FAQ bot escalation",
                "color": 15158332,
                "fields": [
                    {"name": "Student", "value": student_identity or "unknown", "inline": True},
                    {"name": "Reason", "value": reason, "inline": True},
                    {"name": "Question", "value": question[:1000], "inline": False},
                    {"name": "Timestamp", "value": datetime.now(timezone.utc).isoformat(), "inline": False},
                ],
            }
        ],
    }
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.post(webhook_url, json=payload)
        response.raise_for_status()
    return True
