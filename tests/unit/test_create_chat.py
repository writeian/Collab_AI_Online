#!/usr/bin/env python3
"""
Test script that creates a chat and tests the AI toggle functionality
"""

import requests

def test_create_chat():
    """Create a chat and test AI toggle functionality"""
    
    print("🧪 Creating Chat and Testing AI Toggle")
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
    
    # Step 2: Find a room to create a chat in
    print("\n2. Finding a room to create a chat...")
    try:
        response = session.get(f"{base_url}/room/", allow_redirects=True)
        
        if response.status_code == 200:
            print("✅ Rooms page accessible")
            
            # Look for room links
            content = response.text
            if 'href="/room/' in content:
                print("✅ Room links found")
                
                # Try to access the first room
                room_response = session.get(f"{base_url}/room/1", allow_redirects=True)
                if room_response.status_code == 200:
                    print("✅ Room 1 accessible")
                    
                    # Try to create a chat in this room
                    print("\n3. Creating a test chat...")
                    chat_data = {
                        "title": "Test Chat for AI Toggle",
                        "mode": "explore"
                    }
                    
                    create_response = session.post(f"{base_url}/room/1/chat/create", data=chat_data, allow_redirects=True)
                    
                    if create_response.status_code == 200:
                        print("✅ Chat created successfully")
                        
                        # Now test the chat page
                        print("\n4. Testing the created chat...")
                        chat_response = session.get(f"{base_url}/chat/1", allow_redirects=True)
                        
                        if chat_response.status_code == 200:
                            content = chat_response.text
                            
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
                                print("\n5. Testing form submission...")
                                test_response = session.post(f"{base_url}/chat/1", data={
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
                            print(f"❌ Could not access chat: {chat_response.status_code}")
                            
                    else:
                        print(f"❌ Could not create chat: {create_response.status_code}")
                        
                else:
                    print(f"❌ Could not access room 1: {room_response.status_code}")
                    
            else:
                print("⚠️ No room links found")
                
        else:
            print(f"❌ Could not access rooms page: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("- Login functionality tested")
    print("- Room access verified")
    print("- Chat creation attempted")
    print("- Toggle elements checked")

if __name__ == "__main__":
    test_create_chat() 