"""
Email utilities for sending transactional emails via SendGrid or SMTP.

Currently implements SendGrid via HTTP API using the SENDGRID_API_KEY env var.
Falls back to logging if not configured.
"""

from typing import Optional
import os
import json
import requests
import logging

# Use the logger (not print) so these show up reliably in Railway's logs.
logger = logging.getLogger(__name__)


def _get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    val = os.getenv(name)
    return val if val is not None else default


def email_configured() -> bool:
    """True when outbound email can actually be sent (SendGrid provider + API key set)."""
    provider = (_get_env("EMAIL_PROVIDER", "") or "").strip().lower()
    return provider == "sendgrid" and bool(_get_env("SENDGRID_API_KEY"))


def send_email(to_email: str, subject: str, html_body: str, text_body: Optional[str] = None) -> bool:
    """Send an email using configured provider.

    Supports:
    - SendGrid API when EMAIL_PROVIDER=sendgrid and SENDGRID_API_KEY is set
    - Otherwise, logs and returns False
    """
    provider = (_get_env("EMAIL_PROVIDER", "").strip().lower())
    if provider != "sendgrid":
        # Not configured to send emails
        logger.warning(f"[email] Provider not configured (EMAIL_PROVIDER={provider!r}). Email not sent: {subject}")
        return False

    api_key = _get_env("SENDGRID_API_KEY")
    from_email = _get_env("EMAIL_FROM") or "no-reply@example.com"
    from_name = _get_env("EMAIL_FROM_NAME") or "AI Collab Online"
    reply_to = _get_env("EMAIL_REPLY_TO")

    if not api_key:
        logger.warning("[email] SENDGRID_API_KEY is not set. Email not sent.")
        return False

    # Build SendGrid request
    payload = {
        "personalizations": [{"to": [{"email": to_email}], "subject": subject}],
        "from": {"email": from_email, "name": from_name},
        "content": [
            {"type": "text/plain", "value": text_body or ""},
            {"type": "text/html", "value": html_body},
        ],
    }
    if reply_to:
        payload["reply_to"] = {"email": reply_to}

    try:
        resp = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
            timeout=10,
        )
        if 200 <= resp.status_code < 300:
            return True
        logger.warning(f"[email] SendGrid error {resp.status_code}: {resp.text[:500]}")
        return False
    except Exception as e:
        logger.warning(f"[email] Exception sending email: {type(e).__name__}: {e}")
        return False


