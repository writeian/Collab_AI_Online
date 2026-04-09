"""Per-room user presence for chat sidebar (who has the tab open recently).

Uses Redis when REDIS_URL is set so all Gunicorn workers share the same view.
Without Redis, falls back to an in-process map (ok for local dev only).
"""

from __future__ import annotations

import logging
import os
import threading
import time
from typing import Iterable, List

_lock = threading.Lock()
# (room_id, user_id) -> unix expiry timestamp
_mem_expiry: dict[tuple[int, int], float] = {}
_log = logging.getLogger(__name__)

_KEY_PREFIX = "collab:presence:room:"
_redis_client = None


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


def touch_presence(room_id: int, user_id: int) -> None:
    """Mark user as active in this room until TTL elapses (refresh with periodic pings)."""
    rid, uid = int(room_id), int(user_id)
    ttl = _ttl_seconds()
    r = _get_redis()
    if r is not None:
        try:
            r.setex(_redis_key(rid, uid), ttl, "1")
            return
        except Exception as e:
            _log.debug("room_presence redis SETEX failed: %s", e)
    now = time.time()
    with _lock:
        _mem_expiry[(rid, uid)] = now + float(ttl)


def _is_active_redis(r, room_id: int, user_id: int) -> bool:
    try:
        return bool(r.exists(_redis_key(room_id, user_id)))
    except Exception as e:
        _log.debug("room_presence redis EXISTS failed: %s", e)
        return False


def _prune_mem() -> None:
    now = time.time()
    dead = [k for k, exp in _mem_expiry.items() if exp <= now]
    for k in dead:
        _mem_expiry.pop(k, None)


def active_members(room_id: int, member_user_ids: Iterable[int]) -> List[int]:
    """Return which of ``member_user_ids`` have fresh presence in ``room_id``."""
    rid = int(room_id)
    ids = sorted({int(x) for x in member_user_ids})
    if not ids:
        return []
    r = _get_redis()
    if r is not None:
        out: List[int] = []
        for uid in ids:
            if _is_active_redis(r, rid, uid):
                out.append(uid)
        return out
    now = time.time()
    with _lock:
        _prune_mem()
        return [uid for uid in ids if _mem_expiry.get((rid, uid), 0) > now]
