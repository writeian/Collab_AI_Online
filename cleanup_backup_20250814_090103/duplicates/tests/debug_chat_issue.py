#!/usr/bin/env python3
"""
Debug script to test the exact chat scenario that's failing.
"""
from app import create_app
from models import db, User, Room, Chat, Message
from openai_utils import get_client_type, get_ai_response, get_mode_system_prompt
import os

def debug_chat_issue():
    """Debug the exact chat scenario that's failing."""
    app = create_app()
    
    with app.app_context():
        print("=== Chat Issue Debug ===")
        
        # Test 1: Check environment variables
        print(f"1. Environment variables:")
        print(f"   ANTHROPIC_API_KEY: {'SET' if os.getenv('ANTHROPIC_API_KEY') else 'NOT SET'}")
        print(f"   USE_OLLAMA: {os.getenv('USE_OLLAMA', 'false')}")
        
        # Test 2: Check client type
        client_type = get_client_type()
        print(f"2. Client type: {client_type}")
        
        if not client_type:
            print("❌ No AI service configured!")
            return False
        
        # Test 3: Test system prompt generation
        print("3. Testing system prompt generation...")
        try:
            system_prompt = get_mode_system_prompt("explore")
            print(f"   System prompt (first 100 chars): {system_prompt[:100]}...")
        except Exception as e:
            print(f"   ❌ System prompt generation failed: {e}")
            return False
        
        # Test 4: Create test data exactly like the web interface
        print("4. Creating test data...")
        
        # Create a test user
        test_user = User(
            username="test_user",
            email="test@example.com",
            display_name="Test User"
        )
        test_user.set_password("password123")
        db.session.add(test_user)
        
        # Create a test room
        test_room = Room(
            name="Test Room",
            description="Test room for AI connection",
            owner_id=1
        )
        db.session.add(test_room)
        
        # Create a test chat (exactly like the web interface)
        test_chat = Chat(
            title="Test Chat",
            room_id=1,
            created_by=1,
            mode="explore"  # This is the default mode
        )
        db.session.add(test_chat)
        db.session.commit()
        
        # Create a test message (exactly like the user's message)
        test_message = Message(
            chat_id=test_chat.id,
            user_id=1,
            role="user",
            content="I am looking to see if using AI in a more collaborative way might benefits students and instructors."
        )
        db.session.add(test_message)
        db.session.commit()
        
        # Test 5: Get AI response (exactly like the web interface)
        print("5. Testing AI response...")
        try:
            response = get_ai_response(test_chat, max_tokens=100)
            print(f"✅ AI Response received: {response[:100]}...")
            
            if "⚠️" in response or "Sorry" in response:
                print(f"❌ AI returned error message: {response}")
                return False
            
            # Clean up test data
            db.session.delete(test_message)
            db.session.delete(test_chat)
            db.session.delete(test_room)
            db.session.delete(test_user)
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"❌ AI Response failed: {e}")
            return False

if __name__ == "__main__":
    success = debug_chat_issue()
    if success:
        print("\n🎉 Chat issue debug successful!")
    else:
        print("\n💥 Chat issue debug failed!") 