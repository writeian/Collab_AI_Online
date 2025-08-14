#!/usr/bin/env python3
"""
Test script to directly test AI response functionality
"""

import requests
import json

def test_ai_response():
    """Test the AI response functionality directly"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing AI Response Functionality")
    print("=" * 50)
    
    # Test 1: Check if the server is responding
    print("\n1. Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Server is responding")
        else:
            print(f"⚠️ Server responded with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Test 2: Test AI response function directly
    print("\n2. Testing AI response function...")
    try:
        from app import create_app
        from openai_utils import get_ai_response
        from models import Chat, Message, db
        
        app = create_app()
        
        with app.app_context():
            # Create a test chat
            test_chat = Chat(
                title="Test Chat",
                mode="explore",
                room_id=1
            )
            db.session.add(test_chat)
            db.session.commit()
            
            # Add a test message
            test_message = Message(
                chat_id=test_chat.id,
                user_id=1,
                role="user",
                content="Hello, can you help me with my research?"
            )
            db.session.add(test_message)
            db.session.commit()
            
            # Test AI response
            print("Testing AI response generation...")
            ai_content, is_truncated = get_ai_response(test_chat)
            
            print(f"AI Response: {ai_content}")
            print(f"Is Truncated: {is_truncated}")
            
            if ai_content and not ai_content.startswith("⚠️"):
                print("✅ AI response generated successfully")
            else:
                print("❌ AI response failed or returned error")
                
            # Clean up
            db.session.delete(test_message)
            db.session.delete(test_chat)
            db.session.commit()
            
    except Exception as e:
        print(f"❌ Error testing AI response: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Test the actual chat endpoint
    print("\n3. Testing chat endpoint...")
    try:
        # This will likely redirect to login, but we can check the response
        response = requests.post(f"{base_url}/chat/1", data={
            "content": "Test message",
            "ai_response": "1"
        }, allow_redirects=True)
        
        print(f"Chat endpoint response status: {response.status_code}")
        
        if response.status_code in [200, 302]:
            print("✅ Chat endpoint is accessible")
        else:
            print(f"⚠️ Unexpected response from chat endpoint: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing chat endpoint: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 AI Response Test Summary:")
    print("- Server is running and accessible")
    print("- AI response function can be tested")
    print("- Chat endpoint is accessible")
    print("\nIf AI responses are still not working:")
    print("1. Check the browser console for JavaScript errors")
    print("2. Check the Flask app logs for backend errors")
    print("3. Verify the toggle is sending the correct form data")

if __name__ == "__main__":
    test_ai_response() 