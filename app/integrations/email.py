from datetime import datetime, timezone
from email.message import EmailMessage
import smtplib

from app.config import get_config


def notify_email(question: str, *, student_identity: str, reason: str) -> bool:
    config = get_config()
    if not (config.escalation_email_to and config.smtp_host):
        return False

    message = EmailMessage()
    message["Subject"] = "FAQ bot escalation"
    message["From"] = config.email_from
    message["To"] = config.escalation_email_to
    message.set_content(
        "\n".join(
            [
                "A Gen Academy FAQ bot question needs review.",
                "",
                f"Student: {student_identity or 'unknown'}",
                f"Reason: {reason}",
                f"Timestamp: {datetime.now(timezone.utc).isoformat()}",
                "",
                question,
            ]
        )
    )

    with smtplib.SMTP(config.smtp_host, config.smtp_port, timeout=10) as smtp:
        if config.smtp_use_tls:
            smtp.starttls()
        if config.smtp_user and config.smtp_password:
            smtp.login(config.smtp_user, config.smtp_password)
        smtp.send_message(message)
    return True
