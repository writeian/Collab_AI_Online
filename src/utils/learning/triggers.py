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
    Generate missing notes for all chats in a room that need them.
    
    This scans all chats in the room and generates notes for any chat
    that has reached 5+ message milestones but doesn't have notes yet.
    
    Args:
        room_id: The room ID to refresh context for
    """
    try:
        from src.models import Chat, Message
        from .context_manager import auto_generate_notes_if_needed
        
        # Get all chats in this room
        room_chats = Chat.query.filter_by(room_id=room_id).all()
        
        notes_generated = 0
        for chat in room_chats:
            # Get message count for this chat
            message_count = Message.query.filter_by(chat_id=chat.id).count()
            
            if message_count >= 5:
                # Generate notes for all missing milestones
                for milestone in range(5, message_count + 1, 5):
                    try:
                        # Temporarily set message count to milestone for generation
                        if auto_generate_notes_for_milestone(chat.id, milestone):
                            notes_generated += 1
                            logger.info(f"📝 Generated notes for chat {chat.id} at {milestone} messages")
                    except Exception as e:
                        logger.error(f"Failed to generate notes for chat {chat.id} at {milestone}: {e}")
        
        logger.info(f"🎓 Generated {notes_generated} note versions for room {room_id}")
        
        # Get final stats
        from .context_manager import get_completion_stats_for_room
        stats = get_completion_stats_for_room(room_id)
        logger.info(f"🔄 Room {room_id} final stats: {stats['total_completed']} completed chats, "
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


def auto_generate_notes_for_milestone(chat_id: int, target_message_count: int) -> bool:
    """
    Generate notes for a specific milestone, even if the chat has more messages.
    
    This is used when backfilling notes for existing chats.
    """
    try:
        from src.models import Chat, Message, ChatNotes
        
        # Check if notes already exist for this milestone
        existing = ChatNotes.query.filter_by(
            chat_id=chat_id,
            message_count=target_message_count
        ).first()
        
        if existing:
            logger.debug(f"Notes already exist for chat {chat_id} at {target_message_count} messages")
            return False
            
        # Get chat and first N messages for this milestone
        chat = Chat.query.get(chat_id)
        if not chat:
            logger.error(f"Chat {chat_id} not found")
            return False
            
        messages = Message.query.filter_by(chat_id=chat_id)\
                                .order_by(Message.timestamp)\
                                .limit(target_message_count)\
                                .all()
        
        if len(messages) < target_message_count:
            logger.debug(f"Chat {chat_id} doesn't have {target_message_count} messages yet")
            return False
            
        # Generate notes using existing document generation logic
        try:
            from src.app.documents import generate_document_content
            notes_content = generate_document_content(messages, chat, "notes")
            
            # Store the notes
            from .context_manager import store_chat_notes
            success = store_chat_notes(chat_id, chat.room_id, notes_content, target_message_count)
            
            if success:
                logger.info(f"✅ Generated milestone notes for chat {chat_id} at {target_message_count} messages")
                return True
            else:
                logger.error(f"❌ Failed to store milestone notes for chat {chat_id}")
                return False
                
        except Exception as gen_error:
            logger.error(f"Note generation failed for chat {chat_id} at {target_message_count}: {gen_error}")
            return False
            
    except Exception as e:
        logger.error(f"Error generating milestone notes for chat {chat_id} at {target_message_count}: {e}")
        return False
