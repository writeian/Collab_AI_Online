#!/usr/bin/env python3
"""Debug script to check avatar data."""

from app import create_app
from models import db, Message, User, Chat
from sqlalchemy.orm import joinedload

def debug_avatars():
    """Debug avatar data loading."""
    app = create_app()
    with app.app_context():
        # Get a specific chat
        chat = Chat.query.first()
        if not chat:
            print("No chats found")
            return
            
        print(f"Chat: {chat.title}")
        
        # Get messages with user data
        messages = Message.query.options(joinedload(Message.user)).filter_by(chat_id=chat.id).order_by(Message.timestamp).all()
        
        print(f"Found {len(messages)} messages")
        
        for i, message in enumerate(messages, 1):
            user_info = f"User: {message.user.display_name} (ID: {message.user.id})" if message.user else "No user data"
            color_class = f"avatar-color-{((message.user.id % 6) + 1)}" if message.user else "no-color"
            initials = message.user.display_name[:2].upper() if message.user else "??"
            
            print(f"Message {i}: {message.role}")
            print(f"  Content: {message.content[:50]}...")
            print(f"  {user_info}")
            print(f"  Color class: {color_class}")
            print(f"  Initials: {initials}")
            print()

if __name__ == "__main__":
    debug_avatars() 