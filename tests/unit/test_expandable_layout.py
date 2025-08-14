#!/usr/bin/env python3
"""
Test script to verify the new expandable layout implementation.
"""

import requests
from bs4 import BeautifulSoup

def test_expandable_layout():
    """Test the new expandable layout implementation."""
    print("📋 Testing New Expandable Layout Implementation")
    print("=" * 60)
    
    # Create a session to maintain login state
    session = requests.Session()
    
    # Login first
    login_url = "http://127.0.0.1:5000/auth/login"
    login_data = {
        'username': 'TestUser3',
        'password': 'password123'
    }
    
    try:
        # Submit login form
        login_response = session.post(login_url, data=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        # Now test the room page
        room_url = "http://127.0.0.1:5000/room/4"
        room_response = session.get(room_url)
        
        if room_response.status_code != 200:
            print(f"❌ Failed to load room page: {room_response.status_code}")
            return False
            
        soup = BeautifulSoup(room_response.text, 'html.parser')
        
        # Test 1: Check for Room Info expandable section
        print("\n1. Testing Room Info Expandable Section:")
        
        room_info_section = soup.find('div', class_='expandable-section')
        if room_info_section:
            print("   ✅ Room Info expandable section found")
        else:
            print("   ❌ Room Info expandable section missing")
            
        room_info_header = soup.find('button', onclick='toggleSection(\'room-info\')')
        if room_info_header:
            print("   ✅ Room Info header button found")
        else:
            print("   ❌ Room Info header button missing")
            
        # Test 2: Check for Your Chats expandable section
        print("\n2. Testing Your Chats Expandable Section:")
        
        your_chats_header = soup.find('button', onclick='toggleSection(\'your-chats\')')
        if your_chats_header:
            print("   ✅ Your Chats header button found")
        else:
            print("   ❌ Your Chats header button missing")
            
        # Test 3: Check for New Chat button at bottom
        print("\n3. Testing New Chat Button Position:")
        
        # Look for the button with btn-primary class
        all_buttons = soup.find_all('a', class_='btn btn-primary')
        new_chat_buttons = [btn for btn in all_buttons if 'chat/create' in btn.get('href', '')]
        if new_chat_buttons:
            print(f"   ✅ Found {len(new_chat_buttons)} New Chat button(s)")
            for i, btn in enumerate(new_chat_buttons):
                btn_text = btn.get_text().strip()
                href = btn.get('href', '')
                print(f"      - Button {i+1}: '{btn_text}' -> {href}")
        else:
            print("   ❌ No New Chat buttons found")
            
        # Test 4: Check for expandable content sections
        print("\n4. Testing Expandable Content Sections:")
        
        expandable_contents = soup.find_all('div', class_='expandable-content')
        if expandable_contents:
            print(f"   ✅ Found {len(expandable_contents)} expandable content sections")
            for i, content in enumerate(expandable_contents):
                content_id = content.get('id', 'unknown')
                is_hidden = 'hidden' in content.get('class', [])
                print(f"      - Section {i+1}: {content_id} (hidden: {is_hidden})")
        else:
            print("   ❌ No expandable content sections found")
            
        # Test 5: Check for CSS version
        print("\n5. Testing CSS Version:")
        css_links = soup.find_all('link', href=lambda h: h and 'components.css?v=2.6' in h)
        if css_links:
            print("   ✅ Updated CSS version (2.6) found")
        else:
            print("   ❌ Updated CSS version not found")
            
        # Test 6: Check for JavaScript functionality
        print("\n6. Testing JavaScript Functions:")
        
        # Check for toggleSection function
        script_content = soup.find('script')
        if script_content:
            script_text = script_content.get_text()
            if 'toggleSection' in script_text:
                print("   ✅ toggleSection function found")
            else:
                print("   ❌ toggleSection function missing")
                
            if 'room-info-icon' in script_text:
                print("   ✅ Default state initialization found")
            else:
                print("   ❌ Default state initialization missing")
        else:
            print("   ❌ No script tag found")
            
        # Test 7: Show section structure
        print("\n7. Section Structure:")
        expandable_sections = soup.find_all('div', class_='expandable-section')
        if expandable_sections:
            print(f"   Found {len(expandable_sections)} expandable sections:")
            for i, section in enumerate(expandable_sections):
                header = section.find('h3')
                if header:
                    print(f"      - Section {i+1}: {header.get_text().strip()}")
        
        print("\n" + "=" * 60)
        print("🎉 Expandable Layout Test Complete!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error testing expandable layout: {e}")
        return False

if __name__ == "__main__":
    test_expandable_layout() 