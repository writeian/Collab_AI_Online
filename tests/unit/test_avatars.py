#!/usr/bin/env python3
"""Test script to check user avatar functionality."""

from app import app
from models import db, Message, User
from sqlalchemy.orm import joinedload

def test_user_avatars():
    """Test if user avatars are working properly."""
    with app.app_context():
        # Test with joinedload
        messages = Message.query.options(joinedload(Message.user)).filter_by(role='user').limit(5).all()
        print(f"Found {len(messages)} user messages")
        
        for message in messages:
            user_info = f"User: {message.user.display_name}" if message.user else "No user data"
            print(f"Message {message.id}: {user_info}")
            print(f"  Content: {message.content[:50]}...")
            print(f"  User initials: {message.user.display_name[:2].upper() if message.user else 'N/A'}")
            print()

if __name__ == "__main__":
    test_user_avatars() 