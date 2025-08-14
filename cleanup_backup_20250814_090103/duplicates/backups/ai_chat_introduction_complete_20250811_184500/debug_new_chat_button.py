#!/usr/bin/env python3
"""
Debug script to check the New Chat button implementation.
"""

import requests
from bs4 import BeautifulSoup

def debug_new_chat_button():
    """Debug the New Chat button implementation."""
    print("🔍 Debugging New Chat Button Implementation")
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
        
        # Debug 1: Look for all buttons with create_chat in href
        print("\n1. All buttons with create_chat in href:")
        all_links = soup.find_all('a', href=True)
        create_chat_links = [link for link in all_links if 'create_chat' in link.get('href', '')]
        
        if create_chat_links:
            print(f"   Found {len(create_chat_links)} create_chat links:")
            for i, link in enumerate(create_chat_links):
                href = link.get('href', '')
                text = link.get_text().strip()
                classes = link.get('class', [])
                print(f"      - Link {i+1}: '{text}' -> {href} (classes: {classes})")
        else:
            print("   ❌ No create_chat links found")
            
        # Debug 2: Look for all buttons with btn-primary class
        print("\n2. All buttons with btn-primary class:")
        btn_primary_links = soup.find_all('a', class_='btn btn-primary')
        
        if btn_primary_links:
            print(f"   Found {len(btn_primary_links)} btn-primary links:")
            for i, link in enumerate(btn_primary_links):
                href = link.get('href', '')
                text = link.get_text().strip()
                print(f"      - Button {i+1}: '{text}' -> {href}")
        else:
            print("   ❌ No btn-primary links found")
            
        # Debug 3: Look for all buttons with "New Chat" text
        print("\n3. All links with 'New Chat' text:")
        new_chat_links = soup.find_all('a', string=lambda text: text and 'New Chat' in text)
        
        if new_chat_links:
            print(f"   Found {len(new_chat_links)} 'New Chat' links:")
            for i, link in enumerate(new_chat_links):
                href = link.get('href', '')
                text = link.get_text().strip()
                print(f"      - Link {i+1}: '{text}' -> {href}")
        else:
            print("   ❌ No 'New Chat' links found")
            
        # Debug 4: Look for all links with "plus" icon
        print("\n4. All links with plus icon:")
        plus_links = soup.find_all('a')
        plus_links = [link for link in plus_links if link.find('i', attrs={'data-lucide': 'plus'})]
        
        if plus_links:
            print(f"   Found {len(plus_links)} links with plus icon:")
            for i, link in enumerate(plus_links):
                href = link.get('href', '')
                text = link.get_text().strip()
                print(f"      - Link {i+1}: '{text}' -> {href}")
        else:
            print("   ❌ No links with plus icon found")
            
        # Debug 5: Show the your-chats-content section
        print("\n5. Your Chats Content Section:")
        your_chats_content = soup.find('div', id='your-chats-content')
        if your_chats_content:
            print("   ✅ your-chats-content found")
            # Show the last few elements in this section
            children = list(your_chats_content.children)
            print(f"   Has {len(children)} child elements")
            for i, child in enumerate(children[-3:]):  # Show last 3 children
                if hasattr(child, 'name') and child.name:
                    print(f"      - Child {i+1}: {child.name} - {child.get_text().strip()[:50]}...")
        else:
            print("   ❌ your-chats-content not found")
            
        # Debug 6: Show all href values
        print("\n6. All href values in the page:")
        all_hrefs = soup.find_all('a', href=True)
        for i, link in enumerate(all_hrefs[:10]):  # Show first 10
            href = link.get('href', '')
            text = link.get_text().strip()
            if 'chat' in href or 'room' in href:
                print(f"      - Link {i+1}: '{text}' -> {href}")
        
        print("\n" + "=" * 60)
        print("🔍 Debug Complete!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error debugging: {e}")
        return False

if __name__ == "__main__":
    debug_new_chat_button() 