"""Password recovery (KAN-7): forgot-password -> email link -> reset."""

import re
from unittest.mock import patch

import pytest

from src.main import app as flask_app
from src.app import db
from src.models.user import User


@pytest.fixture
def app():
    """The real app on a fresh test database (same pattern as test_chat_next_step)."""
    with flask_app.app_context():
        flask_app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False)
        db.drop_all()
        # SQLite can't render document_chunk.search_vector (Postgres-only TSVECTOR).
        tables = [t for t in db.metadata.sorted_tables if t.name != "document_chunk"]
        db.metadata.create_all(bind=db.engine, tables=tables)
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def user(app):
    u = User(
        username="reset_user",
        email="Reset.User@Example.edu",  # stored with mixed case
        display_name="Reset User",
    )
    u.set_password("old-passphrase-1")
    db.session.add(u)
    db.session.commit()
    return {"id": u.id, "email": u.email}


def _request_reset(client, email):
    with patch("src.utils.email.send_email", return_value=True) as send:
        resp = client.post("/auth/forgot-password", data={"email": email})
    return resp, send


def test_lookup_is_case_insensitive(app, user):
    resp, send = _request_reset(app.test_client(), user["email"].lower())
    assert resp.status_code == 302
    send.assert_called_once()
    to_email, _subject, _html, text = send.call_args.args
    assert to_email == user["email"]
    assert "/auth/reset-password/" in text


def test_unknown_email_sends_nothing_but_looks_the_same(app):
    resp, send = _request_reset(app.test_client(), "nobody-here@example.edu")
    assert resp.status_code == 302  # same redirect as a real account (no enumeration)
    send.assert_not_called()


def test_reset_link_sets_new_password_and_is_single_use(app, user):
    client = app.test_client()
    _resp, send = _request_reset(client, user["email"])
    link = re.search(r"/auth/reset-password/[\w-]+", send.call_args.args[3]).group(0)

    resp = client.post(link, data={"password": "new-passphrase-2", "confirm_password": "new-passphrase-2"})
    assert resp.status_code == 302

    db.session.expire_all()
    u = db.session.get(User, user["id"])
    assert u.check_password("new-passphrase-2")
    assert u.reset_token is None

    # The same link must not work twice.
    again = client.get(link, follow_redirects=True)
    assert b"Invalid or expired reset link" in again.data


def test_email_configured_flag(monkeypatch):
    from src.utils.email import email_configured

    for var in ("EMAIL_PROVIDER", "SENDGRID_API_KEY", "BREVO_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    assert email_configured() is False

    # No EMAIL_PROVIDER set -> defaults to Brevo, so a Brevo key alone is enough.
    monkeypatch.setenv("BREVO_API_KEY", "xkeysib-test")
    assert email_configured() is True
    monkeypatch.delenv("BREVO_API_KEY")

    monkeypatch.setenv("EMAIL_PROVIDER", "brevo")
    assert email_configured() is False  # provider without its key still can't send
    monkeypatch.setenv("SENDGRID_API_KEY", "SG.test")
    assert email_configured() is False  # the *other* provider's key doesn't count
    monkeypatch.setenv("BREVO_API_KEY", "xkeysib-test")
    assert email_configured() is True

    monkeypatch.setenv("EMAIL_PROVIDER", " SendGrid ")  # case/whitespace tolerant
    assert email_configured() is True


class _Resp:
    def __init__(self, status_code, text=""):
        self.status_code, self.text = status_code, text


def test_brevo_request_shape(monkeypatch):
    """send_email() posts Brevo's expected JSON and treats 201 as success."""
    import json
    from src.utils import email as email_mod

    monkeypatch.setenv("EMAIL_PROVIDER", "brevo")
    monkeypatch.setenv("BREVO_API_KEY", "xkeysib-test")
    monkeypatch.setenv("EMAIL_FROM", "sender@example.edu")
    monkeypatch.setenv("EMAIL_FROM_NAME", "AI Collab Online")
    captured = {}

    def fake_post(url, headers, data, timeout):
        captured.update(url=url, headers=headers, body=json.loads(data))
        return _Resp(201, '{"messageId":"<x>"}')

    monkeypatch.setattr(email_mod.requests, "post", fake_post)
    assert email_mod.send_email("student@example.edu", "Reset your password", "<p>hi</p>", "hi") is True
    assert captured["url"] == "https://api.brevo.com/v3/smtp/email"
    assert captured["headers"]["api-key"] == "xkeysib-test"
    assert captured["body"]["sender"] == {"email": "sender@example.edu", "name": "AI Collab Online"}
    assert captured["body"]["to"] == [{"email": "student@example.edu"}]
    assert captured["body"]["htmlContent"] == "<p>hi</p>"
    assert captured["body"]["textContent"] == "hi"


def test_provider_error_is_logged_not_raised(monkeypatch, caplog):
    from src.utils import email as email_mod

    monkeypatch.setenv("EMAIL_PROVIDER", "brevo")
    monkeypatch.setenv("BREVO_API_KEY", "bad")
    monkeypatch.setattr(email_mod.requests, "post", lambda *a, **k: _Resp(401, '{"message":"Key not found"}'))
    with caplog.at_level("WARNING"):
        assert email_mod.send_email("x@example.edu", "Reset your password", "<p>x</p>") is False
    assert "[email] brevo error 401" in caplog.text
