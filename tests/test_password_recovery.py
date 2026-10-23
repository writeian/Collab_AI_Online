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

    monkeypatch.delenv("EMAIL_PROVIDER", raising=False)
    monkeypatch.delenv("SENDGRID_API_KEY", raising=False)
    assert email_configured() is False

    monkeypatch.setenv("EMAIL_PROVIDER", "sendgrid")
    assert email_configured() is False  # provider without a key still can't send

    monkeypatch.setenv("SENDGRID_API_KEY", "SG.test")
    assert email_configured() is True
