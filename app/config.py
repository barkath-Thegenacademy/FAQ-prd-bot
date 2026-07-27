import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Config:
    app_name: str
    knowledge_base_path: Path
    gemini_api_key: str | None
    gemini_model: str
    discord_webhook_url: str | None
    escalation_email_to: str | None
    email_from: str
    smtp_host: str | None
    smtp_port: int
    smtp_user: str | None
    smtp_password: str | None
    smtp_use_tls: bool


@lru_cache
def get_config() -> Config:
    return Config(
        app_name=os.getenv("APP_NAME", "Gen Academy FAQ Bot"),
        knowledge_base_path=Path(os.getenv("KNOWLEDGE_BASE_PATH", "knowledge_base")),
        gemini_api_key=os.getenv("GEMINI_API_KEY") or None,
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
        discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL") or None,
        escalation_email_to=os.getenv("ESCALATION_EMAIL_TO") or None,
        email_from=os.getenv("EMAIL_FROM", "faq-bot@example.com"),
        smtp_host=os.getenv("SMTP_HOST") or None,
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=os.getenv("SMTP_USER") or None,
        smtp_password=os.getenv("SMTP_PASSWORD") or None,
        smtp_use_tls=_bool_env("SMTP_USE_TLS", True),
    )
