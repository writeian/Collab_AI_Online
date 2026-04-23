"""Tests for multi-participant 'weaving' in _prepare_anthropic_completion and helpers."""

from unittest.mock import MagicMock, patch

import pytest
from flask import Flask


@pytest.fixture
def app_ctx():
    app = Flask(__name__)
    with app.app_context():
        yield


def _mock_message(mid, role, user_id, content, display_name="User"):
    m = MagicMock()
    m.id = mid
    m.role = role
    m.user_id = user_id
    m.content = content
    u = MagicMock()
    u.display_name = display_name
    u.username = display_name.lower().replace(" ", "_")
    m.user = u
    return m


def _patch_message_query(rows):
    """Patch src.models.Message.query chain: options→filter_by→filter→order_by→all."""
    q_all = MagicMock()
    q_all.all.return_value = rows

    q_order = MagicMock()
    q_order.order_by.return_value = q_all

    q_after_filter_by = MagicMock()
    q_after_filter_by.filter.return_value = q_order

    q_opts = MagicMock()
    q_opts.filter_by.return_value = q_after_filter_by

    q_root = MagicMock()
    q_root.options.return_value = q_opts
    return q_root


def test_format_user_turn_prefixes_with_display_name():
    from src.utils.openai_utils import _format_user_turn_for_llm

    u = MagicMock()
    u.display_name = "Maria"
    u.username = "maria"
    content, raw = _format_user_turn_for_llm(42, u, "Hello")
    assert content == "Maria: Hello"
    assert raw == "Hello"


def test_format_user_turn_no_prefix_without_user_id():
    from src.utils.openai_utils import _format_user_turn_for_llm

    content, raw = _format_user_turn_for_llm(None, None, "Anonymous")
    assert content == "Anonymous"
    assert raw == "Anonymous"


def test_distinct_human_user_ids():
    from src.utils.openai_utils import _distinct_human_user_ids

    payload = [
        {"role": "user", "content": "a", "_user_id": 1},
        {"role": "assistant", "content": "b"},
        {"role": "user", "content": "c", "_user_id": 2},
    ]
    assert _distinct_human_user_ids(payload) == 2


def test_force_individual_only_reply():
    from src.utils.openai_utils import _force_individual_only_reply

    assert _force_individual_only_reply("Hey just for me what is pi")
    assert not _force_individual_only_reply("What is pi")


def test_collaboration_system_addon_variants():
    from src.utils.openai_utils import _collaboration_system_addon

    multi = _collaboration_system_addon(weaving_active=True, max_speakers_named=3)
    assert "multi-participant thread" in multi
    solo = _collaboration_system_addon(weaving_active=False, max_speakers_named=3)
    assert "Only one human participant" in solo


def test_prepare_two_users_weaving_prompt(app_ctx, monkeypatch):
    monkeypatch.delenv("AI_WEAVING_ENABLED", raising=False)
    monkeypatch.delenv("AI_WEAVING_PIN_CHATS", raising=False)

    chat = MagicMock()
    chat.id = 7
    chat.mode = "explore"
    chat.room_id = None

    rows = [
        _mock_message(1, "user", 1, "From Alice", "Alice"),
        _mock_message(2, "user", 2, "From Bob", "Bob"),
    ]
    q_root = _patch_message_query(rows)

    anchor = MagicMock()
    anchor.id = 2
    anchor.role = "user"
    anchor.user_id = 2
    anchor.content = "From Bob"
    anchor.user = rows[-1].user

    with patch("src.models.Message.query", q_root):
        from src.utils.openai_utils import _prepare_anthropic_completion

        messages, system, _mt, _ro = _prepare_anthropic_completion(
            chat, through_message=anchor
        )

    assert "COLLABORATION (multi-participant thread):" in system
    assert any("Alice: From Alice" in m["content"] for m in messages)
    assert any("Bob: From Bob" in m["content"] for m in messages)
    assert all(set(m.keys()) == {"role", "content"} for m in messages)


def test_prepare_single_user_individual_prompt(app_ctx, monkeypatch):
    monkeypatch.delenv("AI_WEAVING_ENABLED", raising=False)

    chat = MagicMock()
    chat.id = 8
    chat.mode = "explore"
    chat.room_id = None

    rows = [_mock_message(1, "user", 1, "Solo", "Alice")]
    q_root = _patch_message_query(rows)

    anchor = MagicMock()
    anchor.id = 1
    anchor.role = "user"
    anchor.user_id = 1
    anchor.content = "Solo"
    anchor.user = rows[0].user

    with patch("src.models.Message.query", q_root):
        from src.utils.openai_utils import _prepare_anthropic_completion

        _messages, system, _mt, _ro = _prepare_anthropic_completion(
            chat, through_message=anchor
        )

    assert "COLLABORATION: Only one human participant" in system


def test_prepare_force_individual_keyword(app_ctx, monkeypatch):
    monkeypatch.delenv("AI_WEAVING_ENABLED", raising=False)

    chat = MagicMock()
    chat.id = 9
    chat.mode = "explore"
    chat.room_id = None

    rows = [
        _mock_message(1, "user", 1, "Hi", "Alice"),
        _mock_message(2, "user", 2, "Just for me: what is 2+2?", "Bob"),
    ]
    q_root = _patch_message_query(rows)

    anchor = MagicMock()
    anchor.id = 2
    anchor.role = "user"
    anchor.user_id = 2
    anchor.content = "Just for me: what is 2+2?"
    anchor.user = rows[-1].user

    with patch("src.models.Message.query", q_root):
        from src.utils.openai_utils import _prepare_anthropic_completion

        _messages, system, _mt, _ro = _prepare_anthropic_completion(
            chat, through_message=anchor
        )

    assert "multi-participant thread" not in system
    assert "Only one human participant" in system


def test_weaving_disabled_env_skips_collaboration_addon(app_ctx, monkeypatch):
    monkeypatch.setenv("AI_WEAVING_ENABLED", "false")

    chat = MagicMock()
    chat.id = 11
    chat.mode = "explore"
    chat.room_id = None

    rows = [
        _mock_message(1, "user", 1, "A", "Alice"),
        _mock_message(2, "user", 2, "B", "Bob"),
    ]
    q_root = _patch_message_query(rows)

    anchor = MagicMock()
    anchor.id = 2
    anchor.role = "user"
    anchor.user_id = 2
    anchor.content = "B"
    anchor.user = rows[-1].user

    with patch("src.models.Message.query", q_root):
        from src.utils.openai_utils import _prepare_anthropic_completion

        messages, system, _mt, _ro = _prepare_anthropic_completion(
            chat, through_message=anchor
        )

    assert "COLLABORATION" not in system
    assert "Address the user's latest message" in system
    assert "Bob: B" in messages[-1]["content"]


def test_pin_mode_skips_collaboration_addon(app_ctx, monkeypatch):
    monkeypatch.delenv("AI_WEAVING_ENABLED", raising=False)
    monkeypatch.delenv("AI_WEAVING_PIN_CHATS", raising=False)

    chat = MagicMock()
    chat.id = 10
    chat.mode = "pins_explore"
    chat.room_id = None

    rows = [
        _mock_message(1, "user", 1, "A", "Alice"),
        _mock_message(2, "user", 2, "B", "Bob"),
    ]
    q_root = _patch_message_query(rows)

    anchor = MagicMock()
    anchor.id = 2
    anchor.role = "user"
    anchor.user_id = 2
    anchor.content = "B"
    anchor.user = rows[-1].user

    with patch("src.models.Message.query", q_root):
        with patch(
            "src.utils.openai_utils._get_pin_chat_system_prompt",
            return_value="PIN SYSTEM",
        ):
            from src.utils.openai_utils import _prepare_anthropic_completion

            messages, system, _mt, _ro = _prepare_anthropic_completion(
                chat, through_message=anchor
            )

    assert "COLLABORATION" not in system
    assert "PIN SYSTEM" in system
    assert "Alice: A" in messages[0]["content"]
