#!/usr/bin/env python3
"""
pin_helpers.py
Purpose: Helper functions for pinning/unpinning messages and comments
Status: [ACTIVE]
Created: 2025-12-01
Author: AI Collab Team

Provides idempotent pin operations with IntegrityError handling.
"""

from typing import Optional, Dict, Any, Set
from sqlalchemy.exc import IntegrityError
import logging

from src.app import db
from src.models import PinnedItem, Message, Comment, User

logger = logging.getLogger(__name__)


def is_pinned(
    user_id: int, 
    message_id: Optional[int] = None, 
    comment_id: Optional[int] = None
) -> bool:
    """
    Check if a message or comment is pinned by the user.
    
    Args:
        user_id: ID of the user
        message_id: Optional message ID to check
        comment_id: Optional comment ID to check
        
    Returns:
        True if pinned, False otherwise
    """
    try:
        PinnedItem.validate_exactly_one_item(message_id, comment_id)
    except ValueError:
        return False
    
    query = PinnedItem.query.filter_by(user_id=user_id)
    
    if message_id is not None:
        query = query.filter_by(message_id=message_id)
    else:
        query = query.filter_by(comment_id=comment_id)
    
    return query.first() is not None


def pin_item(
    user: User,
    message: Optional[Message] = None,
    comment: Optional[Comment] = None
) -> Dict[str, Any]:
    """
    Pin a message or comment for the user.
    
    Idempotent: Returns success even if already pinned.
    
    Args:
        user: User object doing the pinning
        message: Optional Message object to pin
        comment: Optional Comment object to pin
        
    Returns:
        Dict with keys: success (bool), pinned (bool), created (bool), error (str)
    """
    try:
        # Validate exactly one item
        message_id = message.id if message else None
        comment_id = comment.id if comment else None
        
        PinnedItem.validate_exactly_one_item(message_id, comment_id)
        
        # Get item details
        if message:
            chat_id = message.chat_id
            room_id = message.chat.room_id
            role = message.role
            content = message.content
        else:  # comment
            chat_id = comment.chat_id
            room_id = comment.chat.room_id
            role = None  # Comments don't have roles
            content = comment.content
        
        # Truncate content
        content_snapshot = PinnedItem.truncate_content(content)
        
        # Create pin
        pin = PinnedItem(
            user_id=user.id,
            room_id=room_id,
            chat_id=chat_id,
            message_id=message_id,
            comment_id=comment_id,
            role=role,
            content=content_snapshot
        )
        
        db.session.add(pin)
        db.session.commit()
        
        logger.info(f"User {user.id} pinned {'message' if message else 'comment'} {message_id or comment_id}")
        
        return {
            'success': True,
            'pinned': True,
            'created': True
        }
        
    except ValueError as e:
        # Validation error
        logger.warning(f"Pin validation error: {e}")
        return {
            'success': False,
            'pinned': False,
            'error': str(e)
        }
        
    except IntegrityError as e:
        # Already pinned - rollback and return success anyway (idempotent)
        db.session.rollback()
        logger.debug(f"Pin already exists for user {user.id} - idempotent success")
        
        return {
            'success': True,
            'pinned': True,
            'created': False  # Indicate it already existed
        }
        
    except Exception as e:
        # Other database errors
        db.session.rollback()
        logger.error(f"Error pinning item: {e}")
        
        return {
            'success': False,
            'pinned': False,
            'error': 'Failed to pin item'
        }


def unpin_item(
    user: User,
    message: Optional[Message] = None,
    comment: Optional[Comment] = None
) -> Dict[str, Any]:
    """
    Unpin a message or comment for the user.
    
    Idempotent: Returns success even if not pinned.
    
    Args:
        user: User object doing the unpinning
        message: Optional Message object to unpin
        comment: Optional Comment object to unpin
        
    Returns:
        Dict with keys: success (bool), pinned (bool), deleted (bool), error (str)
    """
    try:
        # Validate exactly one item
        message_id = message.id if message else None
        comment_id = comment.id if comment else None
        
        PinnedItem.validate_exactly_one_item(message_id, comment_id)
        
        # Find and delete pin
        query = PinnedItem.query.filter_by(user_id=user.id)
        
        if message:
            query = query.filter_by(message_id=message_id)
        else:
            query = query.filter_by(comment_id=comment_id)
        
        pin = query.first()
        
        if pin:
            db.session.delete(pin)
            db.session.commit()
            
            logger.info(f"User {user.id} unpinned {'message' if message else 'comment'} {message_id or comment_id}")
            
            return {
                'success': True,
                'pinned': False,
                'deleted': True
            }
        else:
            # Not pinned - return success anyway (idempotent)
            logger.debug(f"Pin doesn't exist for user {user.id} - idempotent success")
            
            return {
                'success': True,
                'pinned': False,
                'deleted': False  # Indicate it didn't exist
            }
        
    except ValueError as e:
        # Validation error
        logger.warning(f"Unpin validation error: {e}")
        return {
            'success': False,
            'pinned': False,
            'error': str(e)
        }
        
    except Exception as e:
        # Database errors
        db.session.rollback()
        logger.error(f"Error unpinning item: {e}")
        
        return {
            'success': False,
            'pinned': False,
            'error': 'Failed to unpin item'
        }


def get_pinned_ids_for_chat(user_id: int, chat_id: int) -> Dict[str, Set[int]]:
    """
    Get all pinned message and comment IDs for a user in a specific chat.
    
    Args:
        user_id: ID of the user
        chat_id: ID of the chat
        
    Returns:
        Dict with 'messages' and 'comments' keys containing sets of IDs
    """
    try:
        pins = PinnedItem.query.filter_by(
            user_id=user_id,
            chat_id=chat_id
        ).all()
        
        message_ids = {
            pin.message_id 
            for pin in pins 
            if pin.message_id is not None
        }
        
        comment_ids = {
            pin.comment_id 
            for pin in pins 
            if pin.comment_id is not None
        }
        
        return {
            'messages': message_ids,
            'comments': comment_ids
        }
        
    except Exception as e:
        logger.error(f"Error getting pinned IDs: {e}")
        # Roll back to recover the session if the table/query failed (e.g., missing table)
        try:
            db.session.rollback()
        except Exception:
            pass
        return {
            'messages': set(),
            'comments': set()
        }


def get_pinned_items_for_chat(user_id: int, chat_id: int) -> list:
    """
    Get all pinned items (with full details) for a user in a specific chat.
    
    Ordered by pin creation time (newest first).
    
    Args:
        user_id: ID of the user
        chat_id: ID of the chat
        
    Returns:
        List of PinnedItem objects
    """
    try:
        return PinnedItem.query.filter_by(
            user_id=user_id,
            chat_id=chat_id
        ).order_by(PinnedItem.created_at.desc()).all()
        
    except Exception as e:
        logger.error(f"Error getting pinned items: {e}")
        # Roll back to recover the session if the table/query failed
        try:
            db.session.rollback()
        except Exception:
            pass
        return []
