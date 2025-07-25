#!/usr/bin/env python3
"""
Check recent messages in the database
"""

from app import create_app
from models import db, Chat, Message, User
from datetime import datetime, timedelta

def check_recent_messages():
    app = create_app()
    
    with app.app_context():
        print("=== Recent Messages Check ===")
        
        # Get the most recent messages from the last 10 minutes
        recent_cutoff = datetime.now() - timedelta(minutes=10)
        
        recent_messages = Message.query.filter(
            Message.timestamp >= recent_cutoff
        ).order_by(Message.timestamp.desc()).all()
        
        print(f"📝 Messages in last 10 minutes: {len(recent_messages)}")
        
        if recent_messages:
            print("\nRecent messages:")
            for i, msg in enumerate(recent_messages, 1):
                chat = Chat.query.get(msg.chat_id)
                user = User.query.get(msg.user_id) if msg.user_id else None
                print(f"   {i}. [{msg.role}] {msg.content[:50]}...")
                print(f"      Chat: {chat.id}, User: {user.username if user else 'None'}, Time: {msg.timestamp}")
        else:
            print("   No recent messages found")
        
        # Check all messages in chat 6 specifically
        print(f"\n📋 All messages in chat 6:")
        chat6_messages = Message.query.filter_by(chat_id=6).order_by(Message.timestamp).all()
        print(f"   Total messages: {len(chat6_messages)}")
        
        for i, msg in enumerate(chat6_messages[-5:], 1):  # Show last 5
            user = User.query.get(msg.user_id) if msg.user_id else None
            print(f"   {i}. [{msg.role}] {msg.content[:50]}... (User: {user.username if user else 'None'})")

if __name__ == "__main__":
    check_recent_messages() 