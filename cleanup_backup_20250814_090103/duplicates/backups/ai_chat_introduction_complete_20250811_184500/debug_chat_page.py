#!/usr/bin/env python3
"""
Debug script to check what HTML is being served for the chat page
"""

import requests

def debug_chat_page():
    """Debug what HTML is being served for the chat page"""
    
    print("🔍 Debugging Chat Page HTML")
    print("=" * 50)
    
    # Use the provided credentials
    username = "TestUser3"
    password = "password123"
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Login
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
    
    # Access chat page
    print("\n2. Accessing chat page...")
    chat_response = session.get(f"{base_url}/chat/1", allow_redirects=True)
    
    if chat_response.status_code == 200:
        content = chat_response.text
        print("✅ Chat page accessible")
        
        # Save the HTML to a file for inspection
        with open('debug_chat_page.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ HTML saved to debug_chat_page.html")
        
        # Check for specific elements
        print("\n3. Checking for specific elements:")
        
        # Look for message input section
        if 'message-input' in content:
            print("✅ Message input found")
        else:
            print("❌ Message input not found")
            
        # Look for form elements
        if 'message-form' in content:
            print("✅ Message form found")
        else:
            print("❌ Message form not found")
            
        # Look for send button
        if 'send-button' in content:
            print("✅ Send button found")
        else:
            print("❌ Send button not found")
            
        # Look for toggle elements
        if 'ai-response-toggle' in content:
            print("✅ AI response toggle found")
        else:
            print("❌ AI response toggle not found")
            
        # Look for AI response label
        if '🤖 AI Response' in content:
            print("✅ AI response label found")
        else:
            print("❌ AI response label not found")
            
        # Show a snippet around the message input
        print("\n4. Message input section:")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'message-input' in line or 'message-form' in line or 'send-button' in line:
                print(f"Line {i+1}: {line.strip()}")
                
        # Show a snippet around where toggle should be
        print("\n5. Looking for toggle section:")
        for i, line in enumerate(lines):
            if 'ai-response-toggle' in line or 'AI Response' in line:
                print(f"Line {i+1}: {line.strip()}")
                
    else:
        print(f"❌ Could not access chat page: {chat_response.status_code}")

if __name__ == "__main__":
    debug_chat_page() 