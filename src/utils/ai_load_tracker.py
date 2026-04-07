"""
Track in-flight LLM work per room for queue estimates.

When REDIS_URL is set, counts are stored in Redis so web workers, RQ workers,
and multiple Gunicorn processes share one view. Otherwise falls back to an
in-memory dict (best-effort per process only).
"""

from __future__ import annotations

import logging
import os
import threading
from contextlib import contextmanager
from typing import Dict, Iterator

_lock = threading.Lock()
_active_by_room: Dict[int, int] = {}
_log = logging.getLogger(__name__)

_REDIS_KEY_PREFIX = "collab:ai_llm_active:"
_REDIS_ACTIVE_TTL_S = int(os.getenv("AI_QUEUE_REDIS_KEY_TTL_S", "7200"))
_redis_client = None


def _avg_seconds_per_job() -> int:
    return max(10, int(os.getenv("AI_QUEUE_SECONDS_PER_ACTIVE_REQUEST", "35")))


def _high_demand_threshold() -> int:
    return max(1, int(os.getenv("AI_QUEUE_HIGH_DEMAND_ACTIVE", "2")))


def _redis_key(room_id: int) -> str:
    return f"{_REDIS_KEY_PREFIX}{int(room_id)}"


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


def _queue_lines(others: int, estimated: int) -> tuple[str, str, str]:
    """Build notice text. ``others`` = in-flight replies excluding the viewer's own when requested."""
    per = _avg_seconds_per_job()
    if others <= 0:
        return ("", "", "")
    if others >= 2:
        primary = "High demand in this room"
        if estimated >= 60:
            lo = max(1, estimated // 60)
            hi = max(lo + 1, (estimated + per) // 60 + 1)
            detail = (
                f"{others} AI replies are generating at once in this chat. "
                f"Rough wait before yours gets going: about {lo}–{hi} min."
            )
        else:
            detail = (
                f"{others} AI replies are generating at once in this chat. "
                f"Rough wait: about {estimated}–{estimated + per} s."
            )
        full = f"{primary} {detail}"
        return (primary, detail, full)
    primary = "You are #2 in the queue."
    detail = (
        f"Another reply is generating now. "
        f"Yours may start in roughly {estimated}–{estimated + per} s."
    )
    full = f"{primary} {detail}"
    return (primary, detail, full)


def snapshot_room(room_id: int, *, subtract_self: int = 0) -> dict:
    """Return queue info for API / UI.

    ``subtract_self=1`` when the client has already received stream ``start`` for this
    browser's request, so the Redis active count includes their own in-flight job.
    """
    redis_active = 0
    r = _get_redis()
    if r is not None:
        try:
            raw = r.get(_redis_key(room_id))
            redis_active = int(raw or 0)
        except Exception as e:
            _log.debug("ai_load_tracker redis GET failed: %s", e)

    with _lock:
        mem_active = int(_active_by_room.get(room_id, 0))

    if r is None:
        active = mem_active
    else:
        active = max(redis_active, mem_active)

    sub = 1 if int(subtract_self) == 1 else 0
    others = max(0, active - sub)

    per = _avg_seconds_per_job()
    estimated = others * per
    high = others >= _high_demand_threshold()
    primary, detail, full = _queue_lines(others, estimated)
    return {
        "active_in_room": active,
        "others_in_room": others,
        "estimated_wait_seconds": estimated,
        "high_demand": high,
        "show_notice": others >= 1,
        "queue_position": 2 if others == 1 else 0,
        "primary_line": primary,
        "detail_line": detail,
        "message": full,
    }


@contextmanager
def room_ai_begin(room_id: int) -> Iterator[None]:
    r = _get_redis()
    key = _redis_key(room_id)
    used_redis = False
    if r is not None:
        try:
            r.incr(key)
            r.expire(key, _REDIS_ACTIVE_TTL_S)
            used_redis = True
        except Exception as e:
            _log.debug("ai_load_tracker redis INCR failed; using local counter: %s", e)
            used_redis = False
    if not used_redis:
        with _lock:
            _active_by_room[room_id] = _active_by_room.get(room_id, 0) + 1
    try:
        yield
    finally:
        if used_redis:
            try:
                n = r.decr(key)
                if n < 0:
                    r.set(key, 0)
            except Exception as e:
                _log.debug("ai_load_tracker redis DECR failed: %s", e)
        else:
            with _lock:
                cur = _active_by_room.get(room_id, 1) - 1
                if cur <= 0:
                    _active_by_room.pop(room_id, None)
                else:
                    _active_by_room[room_id] = cur
