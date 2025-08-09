#!/usr/bin/env python3
"""
Detailed debug script to see exactly what HTML is being served.
"""

import requests
from bs4 import BeautifulSoup

def debug_room_detailed():
    """Debug the room page content in detail."""
    print("🔍 Detailed Room Page Debug")
    print("=" * 50)
    
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
        
        # Look for all h3 elements
        print("\n🔍 All H3 Elements Found:")
        all_h3s = soup.find_all('h3')
        for i, h3 in enumerate(all_h3s):
            print(f"   {i+1}. '{h3.get_text().strip()}'")
        
        # Look for all divs with bg-card class
        print("\n🔍 All bg-card Divs Found:")
        bg_cards = soup.find_all('div', class_='bg-card')
        for i, card in enumerate(bg_cards):
            # Get the first h3 or h2 in this card
            header = card.find('h3') or card.find('h2')
            if header:
                print(f"   {i+1}. Card with header: '{header.get_text().strip()}'")
            else:
                print(f"   {i+1}. Card without header")
        
        # Look for grid layouts
        print("\n🔍 Grid Layouts Found:")
        grids = soup.find_all('div', class_=lambda c: c and 'grid' in c)
        for i, grid in enumerate(grids):
            print(f"   {i+1}. Grid classes: {grid.get('class')}")
        
        # Look for chat cards specifically
        print("\n🔍 Chat Cards Found:")
        chat_cards = soup.find_all('div', class_='chat-card')
        for i, card in enumerate(chat_cards):
            title = card.find('h4')
            if title:
                print(f"   {i+1}. Chat card: '{title.get_text().strip()}'")
        
        # Look for member items
        print("\n🔍 Member Items Found:")
        member_items = soup.find_all('div', class_='member-item')
        for i, item in enumerate(member_items):
            name = item.find('p', class_='member-name')
            if name:
                print(f"   {i+1}. Member: '{name.get_text().strip()}'")
        
        # Show the main content area
        print("\n🔍 Main Content Area:")
        main_content = soup.find('div', class_='max-w-7xl')
        if main_content:
            # Show the structure of the main content
            children = main_content.find_all('div', recursive=False)
            print(f"   Main content has {len(children)} direct children")
            for i, child in enumerate(children[:5]):  # Show first 5
                classes = ' '.join(child.get('class', []))
                print(f"   {i+1}. Child classes: {classes}")
        else:
            print("   ❌ Main content container not found")
        
        # Look for specific text patterns
        print("\n🔍 Text Pattern Search:")
        page_text = soup.get_text()
        patterns = ['Quick Stats', 'Existing Chats', 'Room Members', 'Your Achievements']
        for pattern in patterns:
            if pattern in page_text:
                print(f"   ✅ Found '{pattern}' in page text")
            else:
                print(f"   ❌ '{pattern}' not found in page text")
        
        print("\n" + "=" * 50)
        print("🎉 Detailed Debug Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    debug_room_detailed() 