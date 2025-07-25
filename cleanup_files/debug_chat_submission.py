#!/usr/bin/env python3
"""
Debug script to test chat message submission
"""

from app import create_app
from models import db, Chat, Message, User, Room
from openai_utils import get_ai_response
import os

def test_chat_submission():
    app = create_app()
    
    with app.app_context():
        print("=== Chat Submission Debug ===")
        
        # Get the test user
        user = User.query.filter_by(username="TestUser").first()
        if not user:
            print("❌ TestUser not found!")
            return
        print(f"✅ Found user: {user.username}")
        
        # Get a chat to test with
        chat = Chat.query.first()
        if not chat:
            print("❌ No chats found!")
            return
        print(f"✅ Found chat: {chat.id} in room {chat.room_id}")
        
        # Test message content
        test_content = "Hello, this is a test message!"
        print(f"📝 Testing with message: '{test_content}'")
        
        try:
            # Step 1: Create user message
            print("\n1. Creating user message...")
            user_msg = Message(
                chat_id=chat.id, 
                user_id=user.id, 
                role="user", 
                content=test_content
            )
            db.session.add(user_msg)
            db.session.commit()
            print(f"✅ User message created with ID: {user_msg.id}")
            
            # Step 2: Get AI response
            print("\n2. Getting AI response...")
            try:
                ai_content, is_truncated = get_ai_response(chat)
                print(f"✅ AI response received: {len(ai_content)} characters")
                print(f"   Truncated: {is_truncated}")
                print(f"   Preview: {ai_content[:100]}...")
            except Exception as e:
                print(f"❌ Error getting AI response: {e}")
                return
            
            # Step 3: Create AI message
            print("\n3. Creating AI message...")
            ai_msg = Message(
                chat_id=chat.id,
                role="assistant",
                content=ai_content,
                is_truncated=is_truncated,
                parent_message_id=None
            )
            db.session.add(ai_msg)
            db.session.commit()
            print(f"✅ AI message created with ID: {ai_msg.id}")
            
            # Step 4: Verify messages in database
            print("\n4. Verifying messages in database...")
            messages = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp).all()
            print(f"✅ Total messages in chat: {len(messages)}")
            for i, msg in enumerate(messages[-4:], 1):  # Show last 4 messages
                print(f"   {i}. {msg.role}: {msg.content[:50]}...")
                
        except Exception as e:
            print(f"❌ Error during test: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_chat_submission() 