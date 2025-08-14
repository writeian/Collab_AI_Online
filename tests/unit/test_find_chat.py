#!/usr/bin/env python3
"""
Test script that finds an existing chat and tests the AI toggle functionality
"""

import requests
import re

def test_find_chat():
    """Find an existing chat and test AI toggle functionality"""
    
    print("🧪 Finding Existing Chat and Testing AI Toggle")
    print("=" * 50)
    
    # Use the provided credentials
    username = "TestUser3"
    password = "password123"
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Step 1: Login
    print(f"\n1. Logging in as {username}...")
    login_data = {
        "username": username,
        "password": password
    }
    
    response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=True)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    print("✅ Login successful")
    
    # Step 2: Find existing chats
    print("\n2. Finding existing chats...")
    try:
        # Check the rooms page for chat links
        rooms_response = session.get(f"{base_url}/room/", allow_redirects=True)
        
        if rooms_response.status_code == 200:
            content = rooms_response.text
            
            # Look for chat links using regex
            chat_links = re.findall(r'href="/chat/(\d+)"', content)
            
            if chat_links:
                print(f"✅ Found {len(chat_links)} chat links: {chat_links}")
                
                # Try the first chat
                chat_id = chat_links[0]
                print(f"\n3. Testing chat {chat_id}...")
                
                chat_response = session.get(f"{base_url}/chat/{chat_id}", allow_redirects=True)
                
                if chat_response.status_code == 200:
                    chat_content = chat_response.text
                    
                    # Check if this is actually a chat page (not redirected to home)
                    if 'message-input' in chat_content or 'chat-input' in chat_content:
                        print("✅ Chat page loaded successfully")
                        
                        # Check for toggle elements
                        has_toggle = 'ai-response-toggle' in chat_content
                        has_ai_response_name = 'name="ai_response"' in chat_content
                        has_checked = 'checked' in chat_content
                        has_ai_label = '🤖 AI Response' in chat_content
                        
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
                        print("❌ Chat page redirected to home page")
                        print("This suggests the chat doesn't exist or user doesn't have access")
                        
                else:
                    print(f"❌ Could not access chat {chat_id}: {chat_response.status_code}")
                    
            else:
                print("❌ No chat links found")
                print("You may need to create a chat first")
                
        else:
            print(f"❌ Could not access rooms page: {rooms_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("- Login functionality tested")
    print("- Chat discovery attempted")
    print("- Toggle elements checked")

if __name__ == "__main__":
    test_find_chat() 