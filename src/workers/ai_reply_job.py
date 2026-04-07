"""RQ job: generate assistant reply with streaming events over Redis pub/sub."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from src.utils.ai_stream_logging import log_ai_stream_event


def _emit(r: Any, channel: str, obj: dict) -> None:
    r.publish(channel, json.dumps(obj))


def process_ai_reply_job(
    chat_id: int,
    user_message_id: int,
    stream_token: str,
    critique_instructions: str,
) -> None:
    """Run outside the web request; publishes chunks to Redis channel ``ai_stream:{token}``."""
    from redis import Redis

    from src.app import create_app, db
    from src.models import Chat, Message
    from src.utils.ai_load_tracker import room_ai_begin
    from src.utils.openai_utils import get_ai_response_streaming

    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        return

    r = Redis.from_url(redis_url, decode_responses=True)
    channel = f"ai_stream:{stream_token}"
    app = create_app()

    try:
        with app.app_context():
            from flask import current_app

            chat_obj = db.session.get(Chat, chat_id)
            user_msg = db.session.get(Message, user_message_id)
            if not chat_obj or not user_msg or user_msg.chat_id != chat_id:
                log_ai_stream_event(
                    "worker_stream_aborted",
                    logger=current_app.logger,
                    reason="chat_or_message_missing",
                    path="redis_worker_sse",
                    chat_id=chat_id,
                    user_message_id=user_message_id,
                    token=stream_token,
                )
                _emit(r, channel, {"type": "error", "message": "Chat or message not found"})
                return

            log_ai_stream_event(
                "worker_stream_start",
                logger=current_app.logger,
                path="redis_worker_sse",
                chat_id=chat_id,
                room_id=chat_obj.room_id,
                user_message_id=user_message_id,
                token=stream_token,
            )

            extra = (critique_instructions or "").strip() or None

            def on_chunk(text: str) -> None:
                if text:
                    _emit(r, channel, {"type": "chunk", "text": text})

            try:
                _emit(
                    r,
                    channel,
                    {"type": "start", "user_message_id": user_message_id},
                )
                with room_ai_begin(chat_obj.room_id):
                    ai_content, is_truncated = get_ai_response_streaming(
                        chat_obj,
                        extra_system=extra,
                        through_message=user_msg,
                        on_text_chunk=on_chunk,
                    )
            except Exception as ex:
                log_ai_stream_event(
                    "worker_stream_failed",
                    logger=current_app.logger,
                    phase="llm_or_prep",
                    path="redis_worker_sse",
                    chat_id=chat_id,
                    room_id=chat_obj.room_id,
                    user_message_id=user_message_id,
                    error_type=type(ex).__name__,
                    token=stream_token,
                )
                current_app.logger.exception("AI async job failed")
                _emit(r, channel, {"type": "error", "message": str(ex)})
                return

            ai_msg = Message(
                chat_id=chat_obj.id,
                role="assistant",
                content=ai_content,
                is_truncated=is_truncated,
                parent_message_id=user_msg.id,
            )
            db.session.add(ai_msg)
            db.session.commit()

            log_ai_stream_event(
                "worker_stream_persisted",
                logger=current_app.logger,
                path="redis_worker_sse",
                chat_id=chat_id,
                room_id=chat_obj.room_id,
                user_message_id=user_message_id,
                assistant_message_id=ai_msg.id,
                token=stream_token,
            )

            try:
                from src.utils.learning.triggers import trigger_auto_note_generation

                trigger_auto_note_generation(ai_msg)
            except Exception:
                pass

            _emit(
                r,
                channel,
                {
                    "type": "done",
                    "message_id": ai_msg.id,
                    "is_truncated": bool(is_truncated),
                },
            )
    except Exception as ex:
        try:
            _emit(r, channel, {"type": "error", "message": str(ex)})
        except Exception:
            pass


def enqueue_ai_reply_job(
    chat_id: int,
    user_message_id: int,
    stream_token: str,
    critique_instructions: str,
) -> bool:
    """Return True if job was queued."""
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        return False
    try:
        from redis import Redis
        from rq import Queue

        conn = Redis.from_url(redis_url)
        q = Queue("ai_replies", connection=conn)
        q.enqueue(
            process_ai_reply_job,
            chat_id,
            user_message_id,
            stream_token,
            critique_instructions or "",
            job_timeout=600,
        )
        log_ai_stream_event(
            "worker_job_enqueued",
            logger=logging.getLogger(__name__),
            path="redis_worker_sse",
            chat_id=chat_id,
            user_message_id=user_message_id,
            token=stream_token,
        )
        return True
    except Exception:
        return False
