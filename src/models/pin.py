#!/usr/bin/env python3
"""
pin.py
Purpose: PinnedItem model for user-specific message/comment pinning
Status: [ACTIVE]
Created: 2025-12-01
Author: AI Collab Team

Allows users to pin messages or comments within chats for quick reference.
Stores content snapshot at pin time (truncated to 5000 chars).
"""

from datetime import datetime, timezone
from src.app import db
from typing import Optional
from sqlalchemy.exc import IntegrityError


class PinnedItem(db.Model):
    """
    User-specific pins for messages or comments.
    
    Each pin belongs to exactly one message OR one comment (enforced by constraint).
    Content is snapshotted at pin time and truncated to 5000 chars.
    """
    
    __tablename__ = 'pinned_items'
    __table_args__ = (
        # Check constraint: exactly one of message_id or comment_id must be set
        db.CheckConstraint(
            '(message_id IS NOT NULL AND comment_id IS NULL) OR '
            '(message_id IS NULL AND comment_id IS NOT NULL)',
            name='check_exactly_one_item'
        ),
        # Unique constraints to prevent duplicate pins
        db.UniqueConstraint('user_id', 'message_id', name='unique_user_message_pin'),
        db.UniqueConstraint('user_id', 'comment_id', name='unique_user_comment_pin'),
        # Compound indexes for fast lookups
        db.Index('ix_pins_user_chat', 'user_id', 'chat_id'),
        db.Index('ix_pinned_items_chat_shared', 'chat_id', 'is_shared'),
        db.Index('ix_pinned_items_room_shared', 'room_id', 'is_shared'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('user.id', ondelete='CASCADE'), 
        nullable=False,
        index=True
    )
    room_id = db.Column(
        db.Integer, 
        db.ForeignKey('room.id', ondelete='CASCADE'), 
        nullable=False,
        index=True
    )
    chat_id = db.Column(
        db.Integer, 
        db.ForeignKey('chat.id', ondelete='CASCADE'), 
        nullable=False,
        index=True
    )
    message_id = db.Column(
        db.Integer, 
        db.ForeignKey('message.id', ondelete='CASCADE'), 
        nullable=True
    )
    comment_id = db.Column(
        db.Integer, 
        db.ForeignKey('comment.id', ondelete='CASCADE'), 
        nullable=True
    )
    role = db.Column(db.String(20), nullable=True)  # 'user' or 'assistant' for messages
    content = db.Column(db.Text, nullable=False)  # Snapshot of content at pin time
    is_shared = db.Column(db.Boolean, default=False, nullable=False)  # Shared pins visible to all room members
    created_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )

    # Relationships
    user = db.relationship('User', backref='pinned_items')
    room = db.relationship('Room', backref='pinned_items')
    chat = db.relationship('Chat', backref='pinned_items')
    message = db.relationship('Message', backref='pins', foreign_keys=[message_id])
    comment = db.relationship('Comment', backref='pins', foreign_keys=[comment_id])

    def __repr__(self) -> str:
        item_type = 'message' if self.message_id else 'comment'
        item_id = self.message_id if self.message_id else self.comment_id
        shared_flag = ' shared' if self.is_shared else ''
        return f'<PinnedItem user={self.user_id} {item_type}={item_id}{shared_flag}>'
    
    @property
    def visibility(self) -> str:
        """Return 'shared' or 'personal' for API responses."""
        return 'shared' if self.is_shared else 'personal'

    @staticmethod
    def validate_exactly_one_item(message_id: Optional[int], comment_id: Optional[int]) -> None:
        """
        Application-level validation for SQLite compatibility.
        
        Raises ValueError if not exactly one of message_id or comment_id is provided.
        """
        has_message = message_id is not None
        has_comment = comment_id is not None
        
        if has_message == has_comment:  # Both None or both set
            raise ValueError("Must specify exactly one: message_id or comment_id")

    @staticmethod
    def truncate_content(content: str, max_length: int = 5000) -> str:
        """
        Truncate content to specified length for storage efficiency.
        
        Args:
            content: The content to truncate
            max_length: Maximum length (default 5000 chars)
            
        Returns:
            Truncated content with ellipsis if needed
        """
        if not content:
            return ""
        
        if len(content) <= max_length:
            return content
        
        return content[:max_length] + '...'

