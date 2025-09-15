"""
Learning Context Triggers

Handles automatic triggering of note generation when messages are added to chats.
This module integrates with the message creation process to automatically generate
and store notes when chats reach the 5+ message threshold.
"""

import logging
from typing import Any

from flask import current_app

logger = logging.getLogger(__name__)


def trigger_auto_note_generation(message: Any) -> None:
    """
    Trigger automatic note generation after a message is added.
    
    This should be called after every message creation to check if
    the chat has reached the threshold for automatic note generation.
    
    Args:
        message: The message that was just created
    """
    try:
        if not message or not hasattr(message, 'chat_id'):
            logger.debug("Invalid message object for auto note generation")
            return
            
        chat_id = message.chat_id
        
        # Import here to avoid circular imports
        from .context_manager import auto_generate_notes_if_needed
        
        # Attempt to auto-generate notes
        notes_generated = auto_generate_notes_if_needed(chat_id)
        
        if notes_generated:
            logger.info(f"🎓 Auto-generated learning notes for chat {chat_id}")
        else:
            logger.debug(f"No notes generated for chat {chat_id} (may not meet criteria)")
            
    except Exception as e:
        logger.error(f"Error in auto note generation trigger for message {getattr(message, 'id', 'unknown')}: {e}")
        # Don't re-raise - note generation failure shouldn't break message creation


def trigger_context_refresh_for_room(room_id: int) -> None:
    """
    Trigger a context refresh for all active chats in a room.
    
    This can be called when new notes are generated to potentially
    update context for any ongoing conversations in the room.
    
    Args:
        room_id: The room ID to refresh context for
    """
    try:
        from .context_manager import get_completion_stats_for_room
        
        stats = get_completion_stats_for_room(room_id)
        logger.info(f"🔄 Room {room_id} context stats: {stats['total_completed']} completed chats, "
                   f"{len(stats['modes_covered'])} modes covered")
                   
    except Exception as e:
        logger.error(f"Error refreshing context for room {room_id}: {e}")


def should_generate_notes(chat_id: int) -> bool:
    """
    Check if a chat should have notes generated.
    
    Returns True if:
    - Chat has reached a 5-message milestone (5, 10, 15, 20...)
    - Notes don't already exist for this exact message count
    
    Args:
        chat_id: The chat to check
        
    Returns:
        True if notes should be generated, False otherwise
    """
    try:
        from src.models import Message
        from .context_manager import has_stored_notes
        
        # Get current message count
        message_count = Message.query.filter_by(chat_id=chat_id).count()
        
        # Check if we're at a 5-message milestone
        if message_count < 5 or message_count % 5 != 0:
            return False
            
        # Check if notes already exist for this exact message count
        if has_stored_notes(chat_id, message_count):
            logger.debug(f"Notes already exist for chat {chat_id} at {message_count} messages")
            return False
            
        logger.info(f"📝 Chat {chat_id} reached {message_count}-message milestone, generating notes")
        return True
        
    except Exception as e:
        logger.error(f"Error checking if notes should be generated for chat {chat_id}: {e}")
        return False
