#!/usr/bin/env python3
"""
Check messages specifically in chat 8
"""

from app import create_app
from models import db, Chat, Message, User
from datetime import datetime, timedelta

def check_chat8_messages():
    app = create_app()
    
    with app.app_context():
        print("=== Chat 8 Messages Check ===")
        
        # Get all messages in chat 8
        chat8_messages = Message.query.filter_by(chat_id=8).order_by(Message.timestamp).all()
        print(f"📝 Total messages in chat 8: {len(chat8_messages)}")
        
        if chat8_messages:
            print("\nAll messages in chat 8:")
            for i, msg in enumerate(chat8_messages, 1):
                user = User.query.get(msg.user_id) if msg.user_id else None
                print(f"   {i}. [{msg.role}] {msg.content[:50]}... (User: {user.username if user else 'AI'}, Time: {msg.timestamp})")
        else:
            print("   No messages found in chat 8")
        
        # Check for any messages in the last 5 minutes
        recent_cutoff = datetime.now() - timedelta(minutes=5)
        recent_messages = Message.query.filter(
            Message.timestamp >= recent_cutoff
        ).order_by(Message.timestamp.desc()).all()
        
        print(f"\n🕒 Messages in last 5 minutes: {len(recent_messages)}")
        for msg in recent_messages:
            user = User.query.get(msg.user_id) if msg.user_id else None
            print(f"   - [{msg.role}] {msg.content[:50]}... (Chat: {msg.chat_id}, User: {user.username if user else 'AI'})")

if __name__ == "__main__":
    check_chat8_messages() 