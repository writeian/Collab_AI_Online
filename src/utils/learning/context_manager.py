"""
Learning Context Manager

Handles automatic note generation, storage, and retrieval for enhanced
learning progression across multiple chats within a room.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from flask import current_app
from src.app import db

logger = logging.getLogger(__name__)


def auto_generate_notes_if_needed(chat_id: int) -> bool:
    """
    Automatically generate and store notes for a chat if:
    1. Chat has reached a 5-message milestone (5, 10, 15, 20...)
    2. Notes don't already exist for this exact message count
    
    Returns True if notes were generated, False otherwise.
    """
    try:
        from src.models import Chat, Message
        
        # Get current message count
        message_count = Message.query.filter_by(chat_id=chat_id).count()
        
        # Only generate at 5-message milestones
        if message_count < 5 or message_count % 5 != 0:
            logger.debug(f"Chat {chat_id} has {message_count} messages, not at 5-message milestone")
            return False
            
        # Check if notes already exist for this message count
        from src.models import ChatNotes
        
        logger.info(f"🔍 Checking for existing notes: chat_id={chat_id}, message_count={message_count}")
        
        try:
            existing_notes = ChatNotes.query.filter_by(
                chat_id=chat_id, 
                message_count=message_count
            ).first()
        except Exception as db_error:
            logger.error(f"❌ Database error checking notes (table may not exist): {db_error}")
            return False
        
        if existing_notes:
            logger.debug(f"Notes already exist for chat {chat_id} at {message_count} messages")
            return False
            
        # Get chat and messages
        chat = Chat.query.get(chat_id)
        if not chat:
            logger.error(f"Chat {chat_id} not found")
            return False
            
        messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp).all()
        
        # Generate notes using existing document generation logic
        logger.info(f"📝 Generating notes for chat {chat_id} with {len(messages)} messages")
        
        try:
            from src.app.documents import generate_document_content
            notes_content = generate_document_content(messages, chat, "notes")
            logger.info(f"✅ Notes generated successfully, length: {len(notes_content)} chars")
        except Exception as gen_error:
            logger.error(f"❌ Note generation failed: {gen_error}")
            return False
        
        # Store the notes
        success = store_chat_notes(chat_id, chat.room_id, notes_content, message_count)
        
        if success:
            logger.info(f"✅ Auto-generated notes for chat {chat_id} ({message_count} messages)")
            return True
        else:
            logger.error(f"❌ Failed to store notes for chat {chat_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error auto-generating notes for chat {chat_id}: {e}")
        return False


def store_chat_notes(chat_id: int, room_id: int, notes_content: str, message_count: int) -> bool:
    """
    Store notes for a chat in the database.
    
    Returns True if successful, False otherwise.
    """
    try:
        from src.models import ChatNotes
        
        # Always create new notes record for each milestone (versioned notes)
        chat_notes = ChatNotes(
            chat_id=chat_id,
            room_id=room_id,
            notes_content=notes_content,
            message_count=message_count
        )
        db.session.add(chat_notes)
        
        logger.info(f"📝 Created notes version for chat {chat_id} at {message_count} messages")
        
        db.session.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error storing notes for chat {chat_id}: {e}")
        db.session.rollback()
        return False


def has_stored_notes(chat_id: int, message_count: Optional[int] = None) -> bool:
    """Check if notes already exist for a chat at a specific message count."""
    try:
        from src.models import ChatNotes
        
        if message_count:
            # Check for notes at specific message count
            return ChatNotes.query.filter_by(
                chat_id=chat_id, 
                message_count=message_count
            ).first() is not None
        else:
            # Check if any notes exist for this chat
            return ChatNotes.query.filter_by(chat_id=chat_id).first() is not None
            
    except Exception as e:
        logger.error(f"Error checking for existing notes for chat {chat_id}: {e}")
        return False


def get_chat_notes(chat_id: int, message_count: Optional[int] = None) -> Optional[str]:
    """Get stored notes for a specific chat, optionally at a specific message count."""
    try:
        from src.models import ChatNotes
        
        if message_count:
            # Get notes for specific message count
            notes = ChatNotes.query.filter_by(
                chat_id=chat_id, 
                message_count=message_count
            ).first()
        else:
            # Get latest notes for this chat
            notes = ChatNotes.query.filter_by(chat_id=chat_id)\
                                   .order_by(ChatNotes.message_count.desc())\
                                   .first()
                                   
        return notes.notes_content if notes else None
        
    except Exception as e:
        logger.error(f"Error retrieving notes for chat {chat_id}: {e}")
        return None


def get_learning_context_for_room(room_id: int, exclude_chat_id: Optional[int] = None) -> Optional[str]:
    """
    Get cumulative learning context from all completed chats in a room.
    
    This combines notes from all chats with stored notes, providing rich
    context for new chats to build upon previous discussions.
    
    Args:
        room_id: The room to get context for
        exclude_chat_id: Optional chat ID to exclude (e.g., current chat)
        
    Returns:
        Combined notes content or None if no completed chats found
    """
    try:
        from src.models import ChatNotes
        
        # Get latest notes for each chat in this room
        # Use subquery to get the most recent notes per chat
        from sqlalchemy import func
        
        subquery = db.session.query(
            ChatNotes.chat_id,
            func.max(ChatNotes.message_count).label('max_messages')
        ).filter_by(room_id=room_id).group_by(ChatNotes.chat_id).subquery()
        
        query = db.session.query(ChatNotes).join(
            subquery, 
            (ChatNotes.chat_id == subquery.c.chat_id) & 
            (ChatNotes.message_count == subquery.c.max_messages)
        ).filter_by(room_id=room_id)
        
        if exclude_chat_id:
            query = query.filter(ChatNotes.chat_id != exclude_chat_id)
            
        completed_chats = query.order_by(ChatNotes.generated_at).all()
        
        if not completed_chats:
            logger.debug(f"No completed chats found for room {room_id}")
            return None
            
        # Combine all notes into comprehensive context
        context_parts = []
        
        for i, chat_notes in enumerate(completed_chats, 1):
            # Get chat info for context
            from src.models import Chat
            chat = Chat.query.get(chat_notes.chat_id)
            chat_mode = chat.mode if chat else "unknown"
            
            context_parts.append(f"""
## Discussion {i}: {chat_mode.title()} Mode
*Generated from {chat_notes.message_count} messages*

{chat_notes.notes_content}

---
""")
        
        combined_context = "\n".join(context_parts)
        
        logger.info(f"✅ Generated learning context from {len(completed_chats)} completed chats for room {room_id}")
        
        return combined_context.strip()
        
    except Exception as e:
        logger.error(f"Error getting learning context for room {room_id}: {e}")
        return None


def get_completion_stats_for_room(room_id: int) -> Dict[str, Any]:
    """
    Get statistics about completed chats in a room.
    
    Returns information about how many chats have notes, modes covered, etc.
    """
    try:
        from src.models import Chat, ChatNotes
        
        completed_chats = db.session.query(ChatNotes, Chat).join(
            Chat, ChatNotes.chat_id == Chat.id
        ).filter(ChatNotes.room_id == room_id).all()
        
        if not completed_chats:
            return {"total_completed": 0, "modes_covered": [], "total_messages": 0}
            
        modes_covered = []
        total_messages = 0
        
        for chat_notes, chat in completed_chats:
            if chat.mode and chat.mode not in modes_covered:
                modes_covered.append(chat.mode)
            total_messages += chat_notes.message_count
            
        return {
            "total_completed": len(completed_chats),
            "modes_covered": modes_covered,
            "total_messages": total_messages,
            "average_messages": total_messages // len(completed_chats) if completed_chats else 0
        }
        
    except Exception as e:
        logger.error(f"Error getting completion stats for room {room_id}: {e}")
        return {"total_completed": 0, "modes_covered": [], "total_messages": 0}
