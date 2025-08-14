#!/usr/bin/env python3
"""
Test form submission directly
"""

from app import create_app
from models import db, Chat, Message, User
from flask import request

def test_form_submission():
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            print("=== Form Submission Test ===")
            
            # Get the test user
            user = User.query.filter_by(username="TestUser").first()
            if not user:
                print("❌ TestUser not found!")
                return
            print(f"✅ Found user: {user.username}")
            
            # Simulate login
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
            
            # Test POST to chat 8
            test_message = "This is a test message from the script"
            print(f"\n📝 Testing message: '{test_message}'")
            
            response = client.post('/chat/8', data={
                'content': test_message
            }, follow_redirects=False)
            
            print(f"✅ Response status: {response.status_code}")
            print(f"✅ Redirect location: {response.location}")
            
            # Check if message was saved
            messages = Message.query.filter_by(chat_id=8).order_by(Message.timestamp.desc()).limit(3).all()
            print(f"\n📝 Recent messages in chat 8: {len(messages)}")
            for i, msg in enumerate(messages, 1):
                user = User.query.get(msg.user_id) if msg.user_id else None
                print(f"   {i}. [{msg.role}] {msg.content[:50]}... (User: {user.username if user else 'AI'})")

if __name__ == "__main__":
    test_form_submission() 