"""
Track in-flight LLM work per room for queue estimates (best-effort per process).

Under multiple Gunicorn workers each process maintains its own counts, so figures
are approximate but still useful for user feedback.
"""

from __future__ import annotations

import os
import threading
from contextlib import contextmanager
from typing import Dict, Iterator

_lock = threading.Lock()
_active_by_room: Dict[int, int] = {}


def _avg_seconds_per_job() -> int:
    return max(10, int(os.getenv("AI_QUEUE_SECONDS_PER_ACTIVE_REQUEST", "35")))


def _high_demand_threshold() -> int:
    return max(1, int(os.getenv("AI_QUEUE_HIGH_DEMAND_ACTIVE", "2")))


def _queue_lines(active: int, estimated: int, high: bool) -> tuple[str, str, str]:
    """Return (primary_line, detail_line, full_message)."""
    per = _avg_seconds_per_job()
    if active <= 0:
        return ("", "", "")
    place = active + 1
    primary = f"You are #{place} in the queue."
    if high:
        if estimated >= 60:
            lo = max(1, estimated // 60)
            hi = max(lo + 1, (estimated + per) // 60 + 1)
            detail = (
                f"High demand ({active} other AI request(s) in progress). "
                f"Rough wait before your reply starts: about {lo}–{hi} min."
            )
        else:
            detail = (
                f"High demand: about {estimated}–{estimated + per} s before your reply may start."
            )
    elif active == 1:
        detail = (
            f"Another reply is generating now. "
            f"Yours may start in roughly {estimated}–{estimated + per} s."
        )
    else:
        detail = (
            f"{active} other AI requests are in progress. "
            f"Your response may begin in roughly {estimated}–{estimated + per} s."
        )
    full = f"{primary} {detail}"
    return (primary, detail, full)


def _user_message(active: int, estimated: int, high: bool) -> str:
    _p, _d, full = _queue_lines(active, estimated, high)
    return full


def snapshot_room(room_id: int) -> dict:
    """Return queue info for API / UI (before starting a new LLM job)."""
    with _lock:
        active = int(_active_by_room.get(room_id, 0))
    per = _avg_seconds_per_job()
    estimated = active * per
    high = active >= _high_demand_threshold()
    primary, detail, full = _queue_lines(active, estimated, high)
    return {
        "active_in_room": active,
        "estimated_wait_seconds": estimated,
        "high_demand": high,
        "show_notice": active >= 1,
        "queue_position": active + 1 if active >= 1 else 0,
        "primary_line": primary,
        "detail_line": detail,
        "message": full,
    }


@contextmanager
def room_ai_begin(room_id: int) -> Iterator[None]:
    with _lock:
        _active_by_room[room_id] = _active_by_room.get(room_id, 0) + 1
    try:
        yield
    finally:
        with _lock:
            cur = _active_by_room.get(room_id, 1) - 1
            if cur <= 0:
                _active_by_room.pop(room_id, None)
            else:
                _active_by_room[room_id] = cur
