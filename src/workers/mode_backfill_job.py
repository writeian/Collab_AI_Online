"""RQ job: generate a room's contextual modes and persist them as CustomPrompt rows.

Runs outside the web request so page renders never block on the model. Enqueued
best-effort from ``get_modes_for_room()`` when a room has learning goals but no
saved modes yet. Idempotent: if modes already exist (another worker, or the room
creation path, saved them first) it does nothing.

Consumed by the existing rq worker on the ``ai_replies`` queue (see Procfile).
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

# Reuse the queue the existing rq worker already consumes (see Procfile).
_QUEUE_NAME = "ai_replies"


def process_mode_backfill_job(room_id: int) -> None:
    """Generate and persist contextual modes for a room. Safe to run repeatedly."""
    from src.app import create_app, db
    from src.models import CustomPrompt, Room
    from src.utils.openai_utils import generate_room_modes

    app = create_app()
    try:
        with app.app_context():
            from flask import current_app

            room = db.session.get(Room, int(room_id))
            if room is None:
                return

            # Idempotency: skip if modes were already saved for this room.
            if CustomPrompt.query.filter_by(room_id=room.id).first() is not None:
                return

            if not (getattr(room, "goals", None) or "").strip():
                return

            try:
                modes = generate_room_modes(room)
            except Exception:
                current_app.logger.exception(
                    "[mode-backfill] generation failed for room %s", room_id
                )
                return

            if not modes:
                return

            for mode_key, mode_info in modes.items():
                db.session.add(
                    CustomPrompt(
                        mode_key=mode_key,
                        label=mode_info.label,
                        prompt=mode_info.prompt,
                        room_id=room.id,
                        created_by=room.owner_id,
                    )
                )

            try:
                db.session.commit()
                current_app.logger.info(
                    "[mode-backfill] saved %d modes for room %s", len(modes), room_id
                )
            except Exception:
                # Most likely a race: the creation path or another worker saved
                # modes first and the unique (room_id, mode_key) constraint fired.
                db.session.rollback()
                current_app.logger.info(
                    "[mode-backfill] modes already saved for room %s (race)", room_id
                )
    except Exception:
        logger.exception("[mode-backfill] job error for room %s", room_id)


def enqueue_mode_backfill_job(room_id: int) -> bool:
    """Best-effort enqueue. Returns True if queued, False if unavailable.

    Uses a short-lived Redis guard so a room is enqueued at most once per window,
    even if many pages render before the worker finishes. Never raises.
    """
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        return False
    try:
        from redis import Redis
        from rq import Queue

        conn = Redis.from_url(redis_url)
        # De-dupe: only enqueue if we can set the guard key (15 min TTL).
        if not conn.set(f"mode_backfill_enqueued:{int(room_id)}", "1", nx=True, ex=900):
            return False
        Queue(_QUEUE_NAME, connection=conn).enqueue(
            process_mode_backfill_job, int(room_id), job_timeout=300
        )
        return True
    except Exception:
        return False
