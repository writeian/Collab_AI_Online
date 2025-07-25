#!/usr/bin/env python3
"""
Debug script to test template message rendering
"""

from app import create_app
from models import db, Chat, Message, User
from chat import view_chat
from flask import request

def test_template_messages():
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            print("=== Template Messages Debug ===")
            
            # Get a chat to test with
            chat = Chat.query.first()
            if not chat:
                print("❌ No chats found!")
                return
            print(f"✅ Testing chat: {chat.id}")
            
            # Simulate a GET request to the chat view
            response = client.get(f'/chat/{chat.id}')
            print(f"✅ GET response status: {response.status_code}")
            
            # Check if we can access the messages directly
            messages = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp).all()
            print(f"✅ Total messages in database: {len(messages)}")
            
            # Show the last few messages
            print("\n📝 Last 5 messages:")
            for i, msg in enumerate(messages[-5:], 1):
                print(f"   {i}. [{msg.role}] {msg.content[:50]}... (ID: {msg.id})")
            
            # Check if there are any recent messages (last 5 minutes)
            from datetime import datetime, timedelta
            recent_cutoff = datetime.now() - timedelta(minutes=5)
            recent_messages = Message.query.filter(
                Message.chat_id == chat.id,
                Message.timestamp >= recent_cutoff
            ).order_by(Message.timestamp).all()
            
            print(f"\n🕒 Messages in last 5 minutes: {len(recent_messages)}")
            for msg in recent_messages:
                print(f"   - [{msg.role}] {msg.content[:50]}...")

if __name__ == "__main__":
    test_template_messages() 