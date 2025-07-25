#!/usr/bin/env python3
"""
Debug script to test web session and chat access
"""

from app import create_app
from models import db, Chat, Message, User, Room
from flask import session

def test_web_session():
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            print("=== Web Session Debug ===")
            
            # Get the test user
            user = User.query.filter_by(username="TestUser").first()
            if not user:
                print("❌ TestUser not found!")
                return
            print(f"✅ Found user: {user.username} (ID: {user.id})")
            
            # Get a chat to test with
            chat = Chat.query.first()
            if not chat:
                print("❌ No chats found!")
                return
            print(f"✅ Found chat: {chat.id}")
            
            # Test 1: Access chat without login (should redirect)
            print(f"\n1. Testing chat access without login...")
            response = client.get(f'/chat/{chat.id}')
            print(f"   Status: {response.status_code}")
            print(f"   Redirected to: {response.location if response.location else 'None'}")
            
            # Test 2: Login first
            print(f"\n2. Logging in...")
            login_response = client.post('/auth/login', data={
                'username': 'TestUser',
                'password': 'password123'
            }, follow_redirects=False)
            print(f"   Login status: {login_response.status_code}")
            print(f"   Redirected to: {login_response.location if login_response.location else 'None'}")
            
            # Test 3: Access chat after login
            print(f"\n3. Testing chat access after login...")
            chat_response = client.get(f'/chat/{chat.id}')
            print(f"   Status: {chat_response.status_code}")
            
            if chat_response.status_code == 200:
                print(f"   ✅ Successfully accessed chat!")
                # Check if we can see the messages in the response
                response_text = chat_response.get_data(as_text=True)
                if "Hello, this is a test message!" in response_text:
                    print(f"   ✅ Found our test message in response!")
                else:
                    print(f"   ❌ Test message not found in response")
                    print(f"   Response preview: {response_text[:200]}...")
            else:
                print(f"   ❌ Failed to access chat")
                print(f"   Response: {chat_response.get_data(as_text=True)}")

if __name__ == "__main__":
    test_web_session() 