"""Per-room user presence for chat sidebar (who has a chat open recently).

Each heartbeat stores which *chat* in the room the user is viewing (hybrid room + chat).
Uses Redis when REDIS_URL is set; otherwise in-process (local dev / single worker only).
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from typing import Dict, Iterable, List

_lock = threading.Lock()
# (room_id, user_id) -> (expiry_unix, chat_id, chat_title)
_mem: Dict[tuple[int, int], tuple[float, int, str]] = {}
_log = logging.getLogger(__name__)

_KEY_PREFIX = "collab:presence:room:"
_redis_client = None
_MAX_TITLE_LEN = 500


def _ttl_seconds() -> int:
    return max(20, int(os.getenv("ROOM_PRESENCE_TTL_S", "90")))


def _redis_key(room_id: int, user_id: int) -> str:
    return f"{_KEY_PREFIX}{int(room_id)}:u:{int(user_id)}"


def _get_redis():
    global _redis_client
    url = (os.getenv("REDIS_URL") or "").strip()
    if not url:
        return None
    if _redis_client is None:
        from redis import Redis

        _redis_client = Redis.from_url(
            url,
            socket_connect_timeout=2.0,
            socket_timeout=2.0,
        )
    return _redis_client


def _normalize_title(chat_title: str) -> str:
    t = (chat_title or "").strip()
    if len(t) > _MAX_TITLE_LEN:
        t = t[: _MAX_TITLE_LEN] + "…"
    return t


def touch_presence(
    room_id: int,
    user_id: int,
    *,
    chat_id: int,
    chat_title: str,
) -> None:
    """Mark user as active in ``room_id``, viewing ``chat_id``, until TTL elapses."""
    rid, uid = int(room_id), int(user_id)
    cid = int(chat_id)
    title = _normalize_title(chat_title)
    ttl = _ttl_seconds()
    payload = json.dumps(
        {"chat_id": cid, "chat_title": title},
        ensure_ascii=False,
    )
    r = _get_redis()
    if r is not None:
        try:
            r.setex(_redis_key(rid, uid), ttl, payload)
            return
        except Exception as e:
            _log.debug("room_presence redis SETEX failed: %s", e)
    now = time.time()
    with _lock:
        _mem[(rid, uid)] = (now + float(ttl), cid, title)


def _parse_payload(raw) -> tuple[int | None, str]:
    if raw is None:
        return None, ""
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="replace")
    raw = str(raw).strip()
    if raw == "1" or raw == "":
        # Legacy key from older deploy
        return None, ""
    try:
        d = json.loads(raw)
        cid = int(d.get("chat_id", 0) or 0) or None
        title = _normalize_title(str(d.get("chat_title") or ""))
        return cid, title
    except (json.JSONDecodeError, TypeError, ValueError):
        return None, ""


def _prune_mem() -> None:
    now = time.time()
    dead = [k for k, t in _mem.items() if t[0] <= now]
    for k in dead:
        _mem.pop(k, None)


def active_presence_rows(room_id: int, member_user_ids: Iterable[int]) -> List[dict]:
    """Members with fresh presence: ``user_id``, ``chat_id``, ``chat_title``."""
    rid = int(room_id)
    ids = sorted({int(x) for x in member_user_ids})
    if not ids:
        return []
    out: List[dict] = []
    r = _get_redis()
    if r is not None:
        for uid in ids:
            key = _redis_key(rid, uid)
            try:
                raw = r.get(key)
            except Exception as e:
                _log.debug("room_presence redis GET failed: %s", e)
                continue
            if not raw:
                continue
            cid, title = _parse_payload(raw)
            label = title or "Chat in this room"
            out.append(
                {
                    "user_id": uid,
                    "chat_id": cid,
                    "chat_title": label,
                }
            )
        return out
    now = time.time()
    with _lock:
        _prune_mem()
        for uid in ids:
            row = _mem.get((rid, uid))
            if not row or row[0] <= now:
                continue
            _, cid, title = row
            label = title or "Chat in this room"
            out.append(
                {
                    "user_id": uid,
                    "chat_id": cid,
                    "chat_title": label,
                }
            )
        return out


def active_members(room_id: int, member_user_ids: Iterable[int]) -> List[int]:
    """Return user ids with fresh presence (no chat detail)."""
    return [r["user_id"] for r in active_presence_rows(room_id, member_user_ids)]
