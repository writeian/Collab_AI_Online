"""Plain-text previews and reply context payloads for chat UI."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional


def reply_preview_text(content: str, max_len: int = 200) -> str:
    """Strip markdown noise for ChatGPT-style quoted snippets."""
    if not content:
        return ""
    text = re.sub(r"```[\s\S]*?```", " ", content)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[#*_>|]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_len:
        return text[: max_len - 1].rstrip() + "…"
    return text


def reply_context_dict(message: Any) -> Optional[Dict[str, Any]]:
    """Build API/template payload for assistant messages that reference a parent."""
    if getattr(message, "role", None) != "assistant":
        return None
    pid = getattr(message, "parent_message_id", None)
    if not pid:
        return None
    parent = getattr(message, "parent", None)
    if parent is None:
        return None
    preview = reply_preview_text(parent.content or "")
    avatar_slot: Optional[int] = None
    if getattr(parent, "role", None) == "user":
        label = (
            parent.user.display_name
            if getattr(parent, "user", None)
            else "Participant"
        )
        kind = "user"
        u = getattr(parent, "user", None)
        if u is not None:
            avatar_slot = int(u.id) % 6 + 1
    else:
        label = "Assistant"
        kind = "assistant"
    return {
        "kind": kind,
        "author_label": label,
        "preview": preview,
        "parent_id": parent.id,
        "avatar_slot": avatar_slot,
    }
