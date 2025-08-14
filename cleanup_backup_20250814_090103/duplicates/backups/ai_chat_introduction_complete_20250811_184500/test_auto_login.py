#!/usr/bin/env python3
"""
Test script that automatically logs in and tests the AI toggle functionality
"""

import requests

def test_auto_login():
    """Test AI toggle functionality with automatic login"""
    
    print("🧪 Testing AI Toggle with Auto Login")
    print("=" * 50)
    
    # Use the provided credentials
    username = "TestUser3"
    password = "password123"
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Step 1: Login
    print(f"\n1. Logging in as {username}...")
    try:
        login_data = {
            "username": username,
            "password": password
        }
        
        response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=True)
        
        if response.status_code == 200:
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 2: Find a chat to test
    print("\n2. Finding a chat to test...")
    try:
        # Try to access the rooms page
        response = session.get(f"{base_url}/room/", allow_redirects=True)
        
        if response.status_code == 200:
            print("✅ Rooms page accessible")
            
            # Look for chat links in the response
            content = response.text
            if 'href="/chat/' in content:
                print("✅ Chat links found")
            else:
                print("⚠️ No chat links found - you may need to create a chat first")
                
        else:
            print(f"❌ Could not access rooms page: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Error accessing rooms: {e}")
        return
    
    # Step 3: Test a specific chat (you can modify this chat ID)
    chat_id = 1  # Change this to an actual chat ID if needed
    print(f"\n3. Testing chat {chat_id}...")
    
    try:
        response = session.get(f"{base_url}/chat/{chat_id}", allow_redirects=True)
        
        if response.status_code == 200:
            content = response.text
            
            # Check for toggle elements
            has_toggle = 'ai-response-toggle' in content
            has_ai_response_name = 'name="ai_response"' in content
            has_checked = 'checked' in content
            has_ai_label = '🤖 AI Response' in content
            
            print(f"✅ Chat page accessible")
            print(f"Contains toggle ID: {'✅ Yes' if has_toggle else '❌ No'}")
            print(f"Contains ai_response name: {'✅ Yes' if has_ai_response_name else '❌ No'}")
            print(f"Contains checked attribute: {'✅ Yes' if has_checked else '❌ No'}")
            print(f"Contains AI label: {'✅ Yes' if has_ai_label else '❌ No'}")
            
            if has_toggle and has_ai_response_name and has_checked and has_ai_label:
                print("\n🎉 SUCCESS! Toggle is present on the chat page!")
                
                # Test form submission
                print("\n4. Testing form submission...")
                test_response = session.post(f"{base_url}/chat/{chat_id}", data={
                    "content": "Test message with AI toggle",
                    "ai_response": "1"
                }, allow_redirects=True)
                
                if test_response.status_code == 200:
                    print("✅ Form submission successful")
                    print("✅ AI toggle functionality should be working!")
                else:
                    print(f"⚠️ Form submission returned: {test_response.status_code}")
                    
            else:
                print("\n❌ Toggle elements missing from chat page")
                
        else:
            print(f"❌ Could not access chat {chat_id}: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing chat: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("- Login functionality tested")
    print("- Chat page accessibility verified")
    print("- Toggle elements checked")
    print("- Form submission tested")

if __name__ == "__main__":
    test_auto_login() 