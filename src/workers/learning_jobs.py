"""RQ jobs for learning-context side work."""

from __future__ import annotations


def process_auto_note_generation_job(message_id: int) -> None:
    """Generate/update chat notes for a committed message without blocking web requests."""
    from src.app import create_app, db
    from src.models import Message
    from src.utils.learning.context_manager import auto_generate_notes_if_needed

    app = create_app()
    with app.app_context():
        msg = db.session.get(Message, int(message_id))
        if not msg:
            return
        auto_generate_notes_if_needed(msg.chat_id)
