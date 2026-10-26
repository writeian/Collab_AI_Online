"""
Email utilities for sending transactional emails (password resets, invitations).

Pick a provider with the EMAIL_PROVIDER env var (defaults to brevo when unset):

- EMAIL_PROVIDER=brevo     + BREVO_API_KEY     (Brevo transactional API; the default)
- EMAIL_PROVIDER=sendgrid  + SENDGRID_API_KEY  (SendGrid v3 API; kept as a fallback option)

Shared settings: EMAIL_FROM (must be a sender verified with the provider),
EMAIL_FROM_NAME, EMAIL_REPLY_TO. If nothing is configured, send_email() logs
why and returns False; it never raises.
"""

from typing import Optional
import os
import json
import requests
import logging

# Use the logger (not print) so these show up reliably in Railway's logs.
logger = logging.getLogger(__name__)

# provider name -> env var holding its API key
PROVIDER_KEY_VARS = {
    "brevo": "BREVO_API_KEY",
    "sendgrid": "SENDGRID_API_KEY",
}


def _get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    val = os.getenv(name)
    return val if val is not None else default


DEFAULT_PROVIDER = "brevo"


def _provider() -> str:
    return (_get_env("EMAIL_PROVIDER", "") or "").strip().lower() or DEFAULT_PROVIDER


def email_configured() -> bool:
    """True when outbound email can actually be sent (known provider + its API key set)."""
    key_var = PROVIDER_KEY_VARS.get(_provider())
    return bool(key_var and _get_env(key_var))


def _send_brevo(api_key, to_email, subject, html_body, text_body, from_email, from_name, reply_to):
    payload = {
        "sender": {"email": from_email, "name": from_name},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_body,
    }
    if text_body:
        payload["textContent"] = text_body
    if reply_to:
        payload["replyTo"] = {"email": reply_to}
    return requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={"api-key": api_key, "Content-Type": "application/json", "Accept": "application/json"},
        data=json.dumps(payload),
        timeout=10,
    )


def _send_sendgrid(api_key, to_email, subject, html_body, text_body, from_email, from_name, reply_to):
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
    return requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=10,
    )


_SENDERS = {"brevo": _send_brevo, "sendgrid": _send_sendgrid}


def send_email(to_email: str, subject: str, html_body: str, text_body: Optional[str] = None) -> bool:
    """Send an email with the configured provider. Returns True on success, False otherwise."""
    provider = _provider()
    if provider not in _SENDERS:
        logger.warning(
            f"[email] Provider not configured (EMAIL_PROVIDER={provider!r}; "
            f"expected one of {sorted(_SENDERS)}). Email not sent: {subject}"
        )
        return False

    key_var = PROVIDER_KEY_VARS[provider]
    api_key = _get_env(key_var)
    if not api_key:
        logger.warning(f"[email] {key_var} is not set. Email not sent.")
        return False

    from_email = _get_env("EMAIL_FROM") or "no-reply@example.com"
    from_name = _get_env("EMAIL_FROM_NAME") or "AI Collab Online"
    reply_to = _get_env("EMAIL_REPLY_TO")

    try:
        resp = _SENDERS[provider](
            api_key, to_email, subject, html_body, text_body, from_email, from_name, reply_to
        )
        if 200 <= resp.status_code < 300:
            return True
        logger.warning(f"[email] {provider} error {resp.status_code}: {resp.text[:500]}")
        return False
    except Exception as e:
        logger.warning(f"[email] Exception sending email via {provider}: {type(e).__name__}: {e}")
        return False
