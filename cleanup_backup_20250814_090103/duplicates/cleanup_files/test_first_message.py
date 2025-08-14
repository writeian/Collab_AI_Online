#!/usr/bin/env python3
"""
Test first message in a new chat
"""

from app import create_app
from models import db, Chat, Message, User, Room
from openai_utils import get_ai_response

def test_first_message():
    app = create_app()
    
    with app.app_context():
        print("=== First Message Test ===")
        
        # Get the test user
        user = User.query.filter_by(username="TestUser").first()
        if not user:
            print("❌ TestUser not found!")
            return
        print(f"✅ Found user: {user.username}")
        
        # Get the most recent chat (chat 8)
        chat = Chat.query.order_by(Chat.id.desc()).first()
        if not chat:
            print("❌ No chats found!")
            return
        print(f"✅ Testing chat: {chat.id}")
        
        # Check current messages
        current_messages = Message.query.filter_by(chat_id=chat.id).all()
        print(f"📝 Current messages in chat {chat.id}: {len(current_messages)}")
        
        # Simulate adding a user message
        test_content = "Hello, this is my first message in this chat!"
        print(f"\n📝 Adding test message: '{test_content}'")
        
        user_msg = Message(
            chat_id=chat.id,
            user_id=user.id,
            role="user",
            content=test_content
        )
        db.session.add(user_msg)
        db.session.commit()
        print(f"✅ User message saved with ID: {user_msg.id}")
        
        # Check messages again
        messages_after = Message.query.filter_by(chat_id=chat.id).all()
        print(f"📝 Messages after adding: {len(messages_after)}")
        
        # Test AI response
        print(f"\n🤖 Testing AI response...")
        try:
            ai_content, is_truncated = get_ai_response(chat)
            print(f"✅ AI response: {len(ai_content)} characters")
            print(f"   Preview: {ai_content[:100]}...")
            
            # Save AI response
            ai_msg = Message(
                chat_id=chat.id,
                role="assistant",
                content=ai_content,
                is_truncated=is_truncated,
                parent_message_id=None
            )
            db.session.add(ai_msg)
            db.session.commit()
            print(f"✅ AI message saved with ID: {ai_msg.id}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_first_message() 