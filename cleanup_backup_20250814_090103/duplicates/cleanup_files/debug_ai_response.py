#!/usr/bin/env python3
"""
Debug script to test AI response functionality
"""

from app import create_app
from models import db, Chat, Message, User
from openai_utils import get_ai_response

def test_ai_response():
    app = create_app()
    
    with app.app_context():
        print("=== AI Response Debug ===")
        
        # Get the most recent chat
        chat = Chat.query.order_by(Chat.id.desc()).first()
        if not chat:
            print("❌ No chats found!")
            return
        print(f"✅ Testing chat: {chat.id}")
        
        # Get the last few messages in this chat
        messages = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp.desc()).limit(5).all()
        print(f"📝 Last {len(messages)} messages in chat {chat.id}:")
        
        for i, msg in enumerate(messages, 1):
            user = User.query.get(msg.user_id) if msg.user_id else None
            print(f"   {i}. [{msg.role}] {msg.content[:50]}... (User: {user.username if user else 'AI'})")
        
        # Test AI response
        print(f"\n🤖 Testing AI response for chat {chat.id}...")
        try:
            ai_content, is_truncated = get_ai_response(chat)
            print(f"✅ AI response received: {len(ai_content)} characters")
            print(f"   Truncated: {is_truncated}")
            print(f"   Preview: {ai_content[:100]}...")
            
            # Save the AI response
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
            print(f"❌ Error getting AI response: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_ai_response() 